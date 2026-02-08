"""
Quick test script to check if CrewAI can connect to Ollama
"""
import os

# Set dummy OpenAI API key
os.environ["OPENAI_API_KEY"] = "NA"

from crewai import Agent, Task, Crew, LLM

print("🧪 Testing Ollama + CrewAI Integration...\n")

# Setup LLM
print("1️⃣ Setting up LLM...")
try:
    llm = LLM(
        model="ollama/gemma3:4b",
        base_url="http://localhost:11434"
    )
    print("   ✅ LLM configured\n")
except Exception as e:
    print(f"   ❌ LLM setup failed: {e}\n")
    exit(1)

# Create a simple agent
print("2️⃣ Creating agent...")
try:
    agent = Agent(
        role="Test Agent",
        goal="Answer a simple question",
        backstory="You are a helpful assistant",
        llm=llm,
        verbose=True
    )
    print("   ✅ Agent created\n")
except Exception as e:
    print(f"   ❌ Agent creation failed: {e}\n")
    exit(1)

# Create a simple task
print("3️⃣ Creating task...")
try:
    task = Task(
        description="What is 2+2?",
        expected_output="The answer to the math problem",
        agent=agent
    )
    print("   ✅ Task created\n")
except Exception as e:
    print(f"   ❌ Task creation failed: {e}\n")
    exit(1)

# Create crew and execute
print("4️⃣ Creating crew and executing...")
try:
    crew = Crew(
        agents=[agent],
        tasks=[task],
        verbose=True
    )
    result = crew.kickoff()
    print(f"\n   ✅ Success! Result: {result}\n")
except Exception as e:
    print(f"   ❌ Crew execution failed: {e}\n")
    import traceback
    traceback.print_exc()
    exit(1)

print("🎉 All tests passed!")
