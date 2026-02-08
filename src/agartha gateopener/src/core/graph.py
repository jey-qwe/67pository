
import logging
from typing import TypedDict, List, Dict, Any, Annotated
from langgraph.graph import StateGraph, END
import operator

# Imports from our modules
from src.agents.scout import ScoutAgent
from src.agents.brain import BrainAgent
from src.notifications import send_alert

logger = logging.getLogger(__name__)

# Try to import Archivarius (graceful fallback if not available)
try:
    import sys
    from pathlib import Path
    # Add parent directory to path to find archivarius
    sys.path.insert(0, str(Path(__file__).parent.parent.parent))
    from agents.archivarius import Archivarius
    ARCHIVARIUS_AVAILABLE = True
    logger.info("✅ Archivarius loaded successfully")
except Exception as e:
    ARCHIVARIUS_AVAILABLE = False
    logger.warning(f"⚠️ Archivarius not available: {e}")

# --- State Definition ---
class AgentState(TypedDict):
    feed_url: str
    platform: str # 'rss', 'fiverr', 'qwork'
    seen_ids: List[str]
    fetched_jobs: List[Dict]      # Output of Scout
    relevant_jobs: List[Dict]     # Output of Sifter (Keyword filter + Duplicate check)
    filtered_jobs: List[Dict]     # Output of Memory Guard (Spam + Evidence filter)
    analyzed_jobs: List[Dict]     # Output of Brain (AI Analysis)
    approved_jobs: List[Dict]     # Output of Critic (Verified High Quality)

# --- Nodes ---

def scout_node(state: AgentState) -> Dict:
    """
    Stealth Scout: Fetches RSS feed data.
    """
    url = state['feed_url']
    platform = state.get('platform', 'rss')
    logger.info(f"🕸️ [Graph] Scout activated for {url} ({platform})")
    
    scout = ScoutAgent()
    jobs = scout.fetch(url, platform)
    
    return {"fetched_jobs": jobs}

def sifter_node(state: AgentState) -> Dict:
    """
    Sifter: Filters out seen jobs and checks basic keywords (optional).
    """
    logger.info("🕸️ [Graph] Sifter filtering jobs...")
    jobs = state.get('fetched_jobs', [])
    seen_ids = set(state.get('seen_ids', []))
    
    # Basic keyword filter could be here, but we'll assume Brain does deep check.
    # We mainly filter duplicates here.
    new_relevant = []
    
    NEGATIVE_KEYWORDS = ['for hire', '[for hire]', 'looking for', 'seeking', 'available for', 'hiring me']
    
    for job in jobs:
        if job['id'] in seen_ids:
            continue
            
        # Check for negative keywords (Case Insensitive)
        title_lower = job['title'].lower()
        if any(neg in title_lower for neg in NEGATIVE_KEYWORDS):
            logger.info(f"🚫 [Sifter] Skipped (Negative Keyword): {job['title']}")
            continue
            
        new_relevant.append(job)
            
    logger.info(f"🕸️ [Graph] Sifter found {len(new_relevant)} new jobs")
    return {"relevant_jobs": new_relevant}

def memory_guard_node(state: AgentState) -> Dict:
    """
    NEW: Memory Guard - Pre-filters spam and low-quality jobs.
    Runs BEFORE the expensive Brain LLM analysis.
    """
    logger.info("🛡️  [Graph] Memory Guard filtering...")
    jobs = state.get('relevant_jobs', [])
    
    if not ARCHIVARIUS_AVAILABLE:
        logger.warning("⚠️ Memory Guard skipped (Archivarius unavailable)")
        return {"filtered_jobs": jobs}
    
    arch = Archivarius()
    filtered = []
    
    for job in jobs:
        job_text = f"{job['title']}\n{job.get('description', '')}"
        
        # Quick garbage check
        if arch.guard.is_garbage(job_text):
            logger.info(f"❌ [Guard] Blocked (Spam): {job['title'][:40]}...")
            continue
        
        # Evidence score
        score = arch.guard.calculate_score(job_text)
        job['evidence_score'] = score
        
        if score < 4.0:
            logger.info(f"❌ [Guard] Blocked (Low Quality {score:.1f}): {job['title'][:40]}...")
            continue
        
        logger.info(f"✅ [Guard] Passed (Score {score:.1f}): {job['title'][:40]}...")
        filtered.append(job)
    
    logger.info(f"🛡️  [Graph] Memory Guard passed {len(filtered)}/{len(jobs)} jobs")
    return {"filtered_jobs": filtered}

def brain_node(state: AgentState) -> Dict:
    """
    Brain: Analyzes each filtered job using Gemma.
    Now receives pre-filtered jobs from Memory Guard.
    """
    logger.info("🧠 [Graph] Brain analyzing...")
    jobs = state.get('filtered_jobs', [])  # Changed from relevant_jobs
    brain = BrainAgent()
    
    analyzed_batch = []
    for job in jobs:
        logger.info(f"   Analyzing: {job['title'][:30]}...")
        analysis = brain.analyze_job(job['description'])
        
        # Merge analysis into job dict
        job_with_analysis = {**job, **analysis}
        analyzed_batch.append(job_with_analysis)
        
    return {"analyzed_jobs": analyzed_batch}

def critic_node(state: AgentState) -> Dict:
    """
    Critic: Reviews the analysis and filters for high scores.
    """
    logger.info("🧐 [Graph] Critic reviewing...")
    jobs = state.get('analyzed_jobs', [])
    brain = BrainAgent() # Reuse brain instance or make a CriticAgent
    
    approved = []
    for job in jobs:
        score = job.get('score', 0)
        if score >= 6: # Threshold
            # Double check with critic
            critique = brain.critique_decision(job)
            if critique.get('valid', True):
                job['critique_feedback'] = critique.get('feedback', '')
                job['score'] = critique.get('refined_score', score) # Update score if refined
                approved.append(job)
            else:
                logger.info(f"   Critic rejected: {job['title']}")
        else:
             logger.info(f"   Low score ({score}): {job['title']}")
             
    logger.info(f"🧐 [Graph] Critic approved {len(approved)} jobs")
    return {"approved_jobs": approved}

def memory_save_node(state: AgentState) -> Dict:
    """
    NEW: Memory Save - Saves approved high-value jobs to FAISS.
    Runs AFTER critic approval.
    """
    logger.info("💾 [Graph] Memory Save checking approved jobs...")
    jobs = state.get('approved_jobs', [])
    
    if not ARCHIVARIUS_AVAILABLE:
        logger.warning("⚠️ Memory Save skipped (Archivarius unavailable)")
        return {}
    
    arch = Archivarius()
    saved_count = 0
    
    for job in jobs:
        from datetime import datetime
        
        # Prepare comprehensive job entry
        job_entry = f"""
HIGH-VALUE JOB OPPORTUNITY (Agartha Approved)

=== JOB DETAILS ===
Title: {job['title']}
Platform: {job.get('platform', 'unknown')}
Link: {job['link']}

Description:
{job.get('description', 'No description')}

=== ANALYSIS ===
Score: {job['score']}/10
Evidence Score: {job.get('evidence_score', 'N/A')}/10
Reasoning: {job.get('reasoning', '')}
Bid Draft: {job.get('bid_draft', '')}
Critic Feedback: {job.get('critique_feedback', '')}

=== METADATA ===
Saved on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source: Agartha LangGraph Bot
"""
        
        # Try to save with Archivarius
        saved = arch.learn(job_entry, metadata={
            "source": "agartha_langgraph",
            "type": "approved_job",
            "platform": job.get('platform'),
            "score": job['score'],
            "evidence_score": job.get('evidence_score'),
            "timestamp": datetime.now().isoformat(),
            "job_link": job['link']
        })
        
        if saved:
            saved_count += 1
            logger.info(f"   ✅ Saved: {job['title'][:40]}...")
        else:
            logger.info(f"   ⏭️  Skipped save: {job['title'][:40]}...")
    
    logger.info(f"💾 [Graph] Saved {saved_count}/{len(jobs)} jobs to memory")
    return {}

def notify_node(state: AgentState) -> Dict:
    """
    Notifier: Sends alerts to Telegram.
    """
    jobs = state.get('approved_jobs', [])
    for job in jobs:
        msg = (
            f"🎯 **AGARTHA ALERT (Score: {job['score']})**\n\n"
            f"📌 **{job['title']}**\n"
            f"💡 Reasoning: {job['reasoning']}\n"
            f"🧐 Critic: {job.get('critique_feedback', 'Approved')}\n\n"
            f"🔗 {job['link']}\n\n"
            f"Use the Bid Draft:\n`{job['bid_draft']}`"
        )
        send_alert(msg)
        
    return {}

# --- Conditional Logic ---

def should_continue_after_sifter(state: AgentState) -> str:
    """
    Decides if we proceed to Memory Guard.
    """
    if not state.get('relevant_jobs'):
        return "end"
    return "continue"

def should_continue_after_guard(state: AgentState) -> str:
    """
    Decides if we proceed to Brain analysis after Memory Guard.
    """
    if not state.get('filtered_jobs'):
        logger.info("🛡️  [Graph] All jobs filtered out, ending workflow")
        return "end"
    return "continue"

# --- Graph Construction ---

workflow = StateGraph(AgentState)

workflow.add_node("scout", scout_node)
workflow.add_node("sifter", sifter_node)
workflow.add_node("memory_guard", memory_guard_node)  # NEW
workflow.add_node("brain", brain_node)
workflow.add_node("critic", critic_node)
workflow.add_node("memory_save", memory_save_node)  # NEW
workflow.add_node("notify", notify_node)

# Edges
workflow.set_entry_point("scout")
workflow.add_edge("scout", "sifter")

# Sifter -> Memory Guard (with conditional)
workflow.add_conditional_edges(
    "sifter",
    should_continue_after_sifter,
    {
        "continue": "memory_guard",
        "end": END
    }
)

# Memory Guard -> Brain (with conditional)
workflow.add_conditional_edges(
    "memory_guard",
    should_continue_after_guard,
    {
        "continue": "brain",
        "end": END
    }
)

# Brain -> Critic -> Memory Save -> Notify -> END
workflow.add_edge("brain", "critic")
workflow.add_edge("critic", "memory_save")
workflow.add_edge("memory_save", "notify")
workflow.add_edge("notify", END)

# Compile
app = workflow.compile()
