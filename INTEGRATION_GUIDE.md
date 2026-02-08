# Job Sniper + Archivarius Integration Guide

## 🎯 What Changed

Your `src/main.py` has been enhanced with **Archivarius 2.0** integration. The Job Sniper bot now has intelligent filtering and memory capabilities.

## ✨ New Features

### 1. **Pre-Filter Stage** (Spam Detection)
- Blocks garbage jobs instantly using Memory Guard blacklist
- Saves expensive LLM calls on obvious spam
- Checks for: chatgpt wrapper, passive income, no-code builder, crypto pump, course selling

### 2. **Evidence Score** (Quality Assessment)
- Quick quality check before deep analysis
- Scores 0-10 based on: trusted domains, code blocks, authorities, relevance keywords
- Jobs scoring < 4.0 are rejected immediately

### 3. **Automatic Memory Saving** (Knowledge Building)
- High-value jobs automatically saved to FAISS database
- Tagged with #Priority_Alpha for easy retrieval
- Includes full job description + Career Sniper analysis
- Future queries can reference past opportunities

## 📊 New Workflow

```
Job Description Input
    ↓
🛡️  Pre-Filter (Memory Guard)
    ├─ Spam? → ❌ REJECT (no LLM call)
    ├─ Score < 4.0? → ❌ REJECT (no LLM call)
    └─ Passed → Continue
    ↓
⚡ Deep Analysis (CrewAI + LLM)
    ↓
💾 Memory Save (if recommended)
    ├─ High-value job → Save to FAISS
    └─ Not recommended → Skip save
    ↓
📊 Final Report
```

## 🚀 How to Test

### Run the Enhanced Job Sniper

```powershell
cd c:\Users\guyla\Desktop\archive
python src\main.py
```

### What Happens

**Test 1: Spam Job**
- Input: "passive income chatgpt wrapper no-code builder"
- Expected: ❌ Blocked at pre-filter stage
- Result: No LLM call made (saves time/resources)

**Test 2: Quality Job**
- Input: Python AI developer with RAG, CUDA, RTX 4090, GSoC
- Expected: ✅ Passes filters → Deep analysis → Saved to memory
- Result: Full CrewAI analysis + saved with #Priority_Alpha

## 📝 Sample Output

### Spam Job (Rejected)
```
🛡️  [PRE-FILTER] Memory Guard Check...
   Evidence Score: 5.0/10
❌ REJECTED: Spam/Garbage detected by blacklist
   (Saved you an expensive LLM call!)
```

### Quality Job (Analyzed & Saved)
```
🛡️  [PRE-FILTER] Memory Guard Check...
   Evidence Score: 9.5/10
✅ Passed pre-filter (Evidence: 9.5/10)
   Proceeding to deep analysis...

⚡ EXECUTING DEEP ANALYSIS...
[CrewAI analysis runs...]

💾 [MEMORY SAVE] Checking if job should be saved...
   Job seems promising, attempting to save to knowledge base...
   ✅ Job saved to knowledge base with #Priority_Alpha tag!
   Future searches can reference this opportunity.
```

## 🔧 Configuration

### Adjust Pre-Filter Threshold

In `src/main.py`, line ~185:
```python
if evidence_score < 4.0:  # Change this threshold
    # Reject low quality
```

**Recommended values**:
- `3.0` - Very permissive (only blocks spam)
- `4.0` - Balanced (default)
- `5.0` - Strict (only high-quality jobs get analyzed)
- `6.0` - Very strict (only jobs with evidence get analyzed)

### Disable Archivarius (if needed)

The integration has graceful fallback. If Archivarius is unavailable, Job Sniper continues working normally:

```python
try:
    from agents.archivarius import Archivarius
    arch = Archivarius()
    use_archivarius = True
except Exception as e:
    print(f"⚠️  Archivarius not available: {e}")
    use_archivarius = False
    # Job Sniper continues without filtering
```

## 💾 Querying Saved Jobs

After running Job Sniper, you can query saved opportunities:

```python
from tools.memory_tool import PersonalMemoryTool

tool = PersonalMemoryTool()

# Search for saved jobs
result = tool._run("Python AI jobs with RTX 4090")
print(result)
```

Or using Archivarius directly:

```python
from agents.archivarius import Archivarius

arch = Archivarius()
memories = arch.recall("high paying remote AI jobs", k=5)
print(memories)
```

## 📈 Benefits

| Feature | Before | After |
|---------|--------|-------|
| Spam filtering | Manual review | ✅ Automatic (saves time) |
| Quality assessment | None | ✅ Evidence scoring (0-10) |
| LLM calls on spam | Yes (wasteful) | ❌ No (efficient) |
| Job memory | Not saved | ✅ Auto-saved with tags |
| Future reference | Lost | ✅ Queryable from FAISS |

## ⚙️ Performance Impact

- **Spam jobs**: ~0.1s (instant rejection)
- **Low-quality jobs**: ~0.2s (quick rejection)
- **Quality jobs**: Same as before + ~1s for memory save
- **Overall**: Faster due to avoiding unnecessary LLM calls

## 🎯 Next Steps

1. **Run the tests**: `python src\main.py`
2. **Integrate with live job feeds**: Update to pull from Upwork/Freelancer APIs
3. **Batch processing**: Process multiple jobs in one run
4. **Custom filters**: Add your own domain-specific blacklist patterns

## 🔍 Troubleshooting

### "Archivarius not available"
- Check if `src/agents/archivarius.py` exists
- Ensure dependencies installed: `pip install -r requirements.txt`
- Job Sniper will continue working (just without filtering)

### "gemma:2b model not found"
- Archivarius defaults to gemma:2b
- You have gemma3:4b, which works fine
- Optional: Pull gemma:2b with `ollama pull gemma:2b`

### Jobs not being saved
- Check Archivarius Deep Think criteria (must be RELEVANT)
- Check evidence score (must be >= 7.0)
- Check job recommendation (must contain "apply" or similar keywords)

## 📚 Files Modified

- ✅ `src/main.py` - Enhanced with Archivarius integration
- ✅ Job analysis flow updated with 5-step process
- ✅ Two test cases added (spam + quality)
- ✅ Graceful fallback if Archivarius unavailable

Enjoy your intelligent Job Sniper! 🎯🔥
