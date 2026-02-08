"""
Career Sniper Agent - Main Entry Point
Uses CrewAI + Ollama (Local LLM) + Personal Memory Tool
Analyzes job vacancies against user's profile
"""

import sys
import io
import os
from pathlib import Path

# --- ЖЕЛЕЗНЫЙ КУПОЛ (НАЧАЛО) ---

# 1. Затыкаем рот OpenAI (чтобы CrewAI даже не думал туда стучаться)
os.environ["OPENAI_API_KEY"] = "NA"
os.environ["OPENAI_MODEL_NAME"] = "NA"

# 2. Принудительная кодировка (лечит ошибку "invalid UTF-8" из логов)
os.environ["PYTHONIOENCODING"] = "utf-8"
os.environ["LANG"] = "C.UTF-8"

# 3. Перехват вывода (чтобы Windows консоль не крашилась от эмодзи)
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding='utf-8')
    sys.stderr.reconfigure(encoding='utf-8')

# --- ЖЕЛЕЗНЫЙ КУПОЛ (КОНЕЦ) ---

from crewai import Agent, Task, Crew, LLM
# from langchain_ollama import ChatOllama # Deprecated for CrewAI 1.6+

# Import personal memory tool
from tools.memory_tool import search_personal_memory

# Import UTF-8 sanitization
from utils import sanitize_for_grpc

# ============================================================================
# LLM CONFIGURATION (Local Ollama)
# ============================================================================

def setup_llm():
    """
    Configure Ollama LLM for CrewAI
    Model: gemma3:4b (local, no API required)
    """
    llm = LLM(
        model="ollama/gemma3:4b",
        base_url="http://localhost:11434"
    )
    return llm


# ============================================================================
# AGENT DEFINITION
# ============================================================================

def create_career_sniper_agent(llm):
    """
    Create Career Sniper Agent
    
    Specializes in:
    - Analyzing job vacancies
    - Matching requirements with user's skills
    - Providing strategic career advice
    """
    # Sanitize all text for Ollama to prevent UTF-8 errors
    goal = sanitize_for_grpc("Найти идеальное применение навыкам пользователя")
    backstory = sanitize_for_grpc(
        "Ты опытный карьерный стратег и аналитик.\n"
        "У тебя есть полный доступ к профилю пользователя через инструмент памяти.\n"
        "Ты знаешь все его навыки, цели, проекты и предпочтения.\n"
        "Твоя задача - объективно оценить, насколько вакансия соответствует профилю пользователя.\n"
        "Ты всегда даешь честную оценку и конкретные аргументы."
    )
    
    agent = Agent(
        role="Personal Career Strategist",
        goal=goal,
        backstory=backstory,
        tools=[search_personal_memory],
        llm=llm,
        verbose=True,
        allow_delegation=False,
        max_retry_limit=5
    )
    return agent


# ============================================================================
# TASK DEFINITION
# ============================================================================

def create_job_analysis_task(agent, job_description: str):
    """
    Create task for analyzing job vacancy
    
    Args:
        agent: Career Sniper agent
        job_description: Job vacancy text
    """
    # Sanitize job description to prevent UTF-8 errors
    clean_job_desc = sanitize_for_grpc(job_description)
    
    # Sanitize task description
    description = sanitize_for_grpc(
        f"Проанализируй следующую вакансию и определи, насколько она подходит пользователю:\n\n"
        f"ВАКАНСИЯ:\n{clean_job_desc}\n\n"
        f"ИНСТРУКЦИИ:\n"
        f"1. Используй инструмент search_personal_memory для поиска релевантных навыков пользователя\n"
        f"2. Сравни требования вакансии с навыками, опытом и целями пользователя\n"
        f"3. Оцени соответствие по шкале 0-100%\n"
        f"4. Предоставь конкретные аргументы (что совпадает, чего не хватает)\n"
        f"5. Дай рекомендацию: стоит ли откликаться"
    )
    
    expected_output = sanitize_for_grpc(
        "Краткий отчет в формате:\n"
        "Match Score: [0-100]%\n"
        "Совпадения: [список навыков, которые есть]\n"
        "Пробелы: [что требуется, но отсутствует]\n"
        "Рекомендация: [откликаться/не откликаться + обоснование]"
    )
    
    task = Task(
        description=description,
        expected_output=expected_output,
        agent=agent
    )
    return task


# ============================================================================
# CREW EXECUTION
# ============================================================================

def run_job_analysis(job_description: str):
    """
    Run complete job analysis workflow with Archivarius integration.
    
    Enhanced Flow:
    1. Pre-filter spam/garbage with Memory Guard
    2. Check evidence score for quick quality assessment
    3. Run full CrewAI analysis if passed filters
    4. Save high-value jobs to knowledge base
    
    Args:
        job_description: Text of the job vacancy
        
    Returns:
        Analysis result
    """
    from datetime import datetime
    
    print("=" * 70)
    print("🎯 CAREER SNIPER - Job Vacancy Analysis (Archivarius Enhanced)")
    print("=" * 70)
    
    # ========================================================================
    # STEP 0: PRE-FILTER with Archivarius Guard
    # ========================================================================
    print("\n🛡️  [PRE-FILTER] Memory Guard Check...")
    
    try:
        from agents.archivarius import Archivarius
        arch = Archivarius()
        use_archivarius = True
    except Exception as e:
        print(f"⚠️  Archivarius not available: {e}")
        print("   Continuing without pre-filter...")
        use_archivarius = False
    
    if use_archivarius:
        # Quick garbage detection
        if arch.guard.is_garbage(job_description):
            print("❌ REJECTED: Spam/Garbage detected by blacklist")
            print("   (Saved you an expensive LLM call!)")
            print("=" * 70)
            return {
                "status": "REJECTED",
                "reason": "Spam/Garbage (blacklist)",
                "match_score": 0,
                "recommendation": "SKIP - Not worth your time"
            }
        
        # Evidence score quick assessment
        evidence_score = arch.guard.calculate_score(job_description)
        print(f"   Evidence Score: {evidence_score:.1f}/10")
        
        # Ultra-low quality filter
        if evidence_score < 4.0:
            print("❌ REJECTED: Very low quality (no trusted domains, authorities, or relevance)")
            print("   (Saved you an expensive LLM call!)")
            print("=" * 70)
            return {
                "status": "REJECTED",
                "reason": "Low evidence score",
                "evidence_score": evidence_score,
                "match_score": 0,
                "recommendation": "SKIP - Low quality posting"
            }
        
        print(f"✅ Passed pre-filter (Evidence: {evidence_score:.1f}/10)")
        print("   Proceeding to deep analysis...\n")
    
    # ========================================================================
    # STEP 1-4: Full CrewAI Analysis
    # ========================================================================
    print(f"📋 Analyzing Job Description:")
    print("-" * 70)
    print(f"{job_description[:300]}...")
    print("-" * 70)
    
    # Setup LLM
    print("\n🧠 Initializing Ollama LLM (gemma3:4b)...")
    llm = setup_llm()
    
    # Create agent
    print("🤖 Creating Career Sniper Agent...")
    career_agent = create_career_sniper_agent(llm)
    
    # Create task
    print("📝 Defining analysis task...")
    analysis_task = create_job_analysis_task(career_agent, job_description)
    
    # Create crew
    print("🚀 Assembling crew...\n")
    crew = Crew(
        agents=[career_agent],
        tasks=[analysis_task],
        verbose=True
    )
    
    # Execute
    print("=" * 70)
    print("⚡ EXECUTING DEEP ANALYSIS...")
    print("=" * 70)
    
    result = crew.kickoff()
    
    print("\n" + "=" * 70)
    print("✅ ANALYSIS COMPLETE")
    print("=" * 70)
    
    # ========================================================================
    # STEP 5: Save High-Value Jobs to Memory
    # ========================================================================
    if use_archivarius:
        print("\n💾 [MEMORY SAVE] Checking if job should be saved...")
        
        result_str = str(result).lower()
        
        # Check if recommendation is positive (откликаться = apply in Russian)
        should_save = any(keyword in result_str for keyword in [
            'откликаться', 'apply', 'рекомендую', 'подходит', 'recommend'
        ])
        
        if should_save:
            print("   Job seems promising, attempting to save to knowledge base...")
            
            # Prepare comprehensive job entry
            job_entry = f"""
HIGH-MATCH JOB OPPORTUNITY DETECTED

=== JOB DESCRIPTION ===
{job_description}

=== CAREER SNIPER ANALYSIS ===
{result}

=== METADATA ===
Analyzed on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Evidence Score: {evidence_score if use_archivarius else 'N/A'}/10
Source: Job Sniper Bot
"""
            
            # Attempt to save with Archivarius
            saved = arch.learn(job_entry, metadata={
                "source": "job_sniper",
                "type": "job_opportunity",
                "evidence_score": evidence_score if use_archivarius else None,
                "timestamp": datetime.now().isoformat(),
                "job_preview": job_description[:200]
            })
            
            if saved:
                print("   ✅ Job saved to knowledge base with #Priority_Alpha tag!")
                print("   Future searches can reference this opportunity.")
            else:
                print("   ℹ️  Job analyzed but not saved to memory")
                print("   (Didn't meet Archivarius criteria: relevance, Deep Think, or score threshold)")
        else:
            print("   ℹ️  Job not recommended, skipping memory save")
    
    return result


# ============================================================================
# MAIN EXECUTION
# ============================================================================

def main():
    """Main entry point"""
    
    # Test 1: Spam job (should be filtered out)
    print("\n" + "🧪" * 35)
    print("TEST 1: SPAM JOB (Should be rejected at pre-filter)")
    print("🧪" * 35 + "\n")
    
    spam_job = """
Make passive income with this chatgpt wrapper!
No coding required, just use our no-code builder.
Course selling opportunity - teach others!
"""
    
    try:
        result = run_job_analysis(spam_job)
        print("\n📊 SPAM TEST RESULT:")
        print(result)
    except Exception as e:
        print(f"❌ Error in spam test: {e}")
    
    print("\n" + "=" * 70)
    print("⏸️  Press Enter to continue to next test...")
    print("=" * 70)
    input()
    
    # Test 2: Quality job (should pass filters and get analyzed)
    print("\n" + "🧪" * 35)
    print("TEST 2: QUALITY JOB (Should pass all filters)")
    print("🧪" * 35 + "\n")
    
    quality_job = """
Senior Python Developer - AI/ML Focus

We're looking for an experienced Python developer to join our AI team.

Requirements:
- Strong Python programming skills (3+ years)
- Experience with RAG (Retrieval-Augmented Generation) systems
- Knowledge of CrewAI or LangChain frameworks
- Ability to work with vector databases (FAISS, Pinecone, etc.)
- Experience with LLM integration and optimization
- CUDA/GPU programming experience is a plus

Nice to have:
- After Effects or video editing skills for AI-generated content
- Experience with local LLM deployment (Ollama, vLLM)
- Knowledge of agentic AI workflows
- RTX 4090 or similar GPU experience

About the role:
This is an opportunity to work on cutting-edge AI systems. You'll be building
autonomous agents, optimizing RAG pipelines, and working with the latest LLM tech.

Location: Remote (preferred: Kazakhstan/Central Asia timezone)
Salary: Competitive, based on experience ($3000-5000/month)
Bonus: Hardware budget for GPU upgrade (RTX 4090 coverage)

GitHub portfolio required. Experience with GSoC or open source contributions is highly valued.
"""
    
    try:
        result = run_job_analysis(quality_job)
        
        # Display final result
        print("\n" + "=" * 70)
        print("📊 FINAL REPORT")
        print("=" * 70)
        print(result)
        print("\n" + "=" * 70)
        print("🔥 UnderDog Analysis Complete!")
        print("=" * 70)
        
    except Exception as e:
        print(f"\n❌ ERROR: {type(e).__name__}")
        print(f"   {str(e)}")
        
        # Check common issues
        print("\n💡 Troubleshooting:")
        print("   1. Is Ollama running? (ollama serve)")
        print("   2. Is gemma3:4b model pulled? (ollama pull gemma3:4b)")
        print("   3. Is the FAISS database created? (run src/ingest_memory.py)")
        print("   4. Is Archivarius available? (check src/agents/archivarius.py)")
        
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
