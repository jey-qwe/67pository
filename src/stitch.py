# -*- coding: utf-8 -*-
"""
Stitch - Jules Persona Logic
Webhook-based response system for Jules AI persona with Code Vision.
"""

import aiohttp
import asyncio
import json
import requests
import os
import glob
import re
from pathlib import Path


class Stitch:
    """
    Jules AI persona handler.
    Responds via Discord webhook with custom avatar and username.
    Now includes Code Vision - ability to read project files.
    """
    
    def __init__(self, webhook_url: str, ollama_url: str = "http://localhost:11434", model: str = "gemma3:4b", system_prompt: str = "", project_root: str = None):
        """
        Initialize Stitch with webhook and AI configuration.
        
        Args:
            webhook_url: Discord webhook URL for Jules responses
            ollama_url: Ollama API URL
            model: Ollama model name
            system_prompt: System prompt for Jules personality
            project_root: Root directory of the project (defaults to parent of src/)
        """
        self.webhook_url = webhook_url
        self.ollama_url = ollama_url
        self.model = model
        self.base_system_prompt = system_prompt
        
        # Jules persona configuration
        self.username = "Jules"
        self.avatar_url = "https://i.imgur.com/YourJulesAvatar.png"  # Placeholder
        
        # Project structure
        if project_root:
            self.project_root = Path(project_root)
        else:
            # Auto-detect: assume we're in src/ and go up one level
            current_file = Path(__file__).resolve()
            self.project_root = current_file.parent.parent
        
        # Generate project tree and enhance system prompt
        self.project_tree = self._get_project_tree()
        self.system_prompt = self._build_enhanced_prompt()
        
        print(f"[Stitch] Project root: {self.project_root}")
        print(f"[Stitch] Indexed {len(self.project_tree.splitlines())} files")
        
    def _get_project_tree(self) -> str:
        """
        Scan src/ directory recursively and return tree structure.
        
        Returns:
            Formatted string of project structure
        """
        tree_lines = []
        src_dir = self.project_root / "src"
        
        if not src_dir.exists():
            return "⚠️ [No src/ directory found]"
        
        # Find all Python files recursively
        py_files = glob.glob(str(src_dir / "**" / "*.py"), recursive=True)
        
        for file_path in sorted(py_files):
            # Make path relative to project root
            rel_path = Path(file_path).relative_to(self.project_root)
            tree_lines.append(f"  - {rel_path}")
        
        return "\n".join(tree_lines) if tree_lines else "⚠️ [No Python files found]"
    
    def _build_enhanced_prompt(self) -> str:
        """
        Build enhanced system prompt with project tree.
        
        Returns:
            Enhanced system prompt
        """
        tree_section = f"""

[PROJECT STRUCTURE]
You have access to the following files in this project:
{self.project_tree}

When users ask about specific files, you can see their content in the context.
"""
        return self.base_system_prompt + tree_section
    
    def _read_mentioned_files(self, user_input: str) -> str:
        """
        Detect and read files mentioned in user input.
        
        Args:
            user_input: User's message
            
        Returns:
            Formatted code context string
        """
        # Pattern to detect .py files mentioned
        file_pattern = r'\b(\w+\.py)\b'
        mentioned_files = re.findall(file_pattern, user_input, re.IGNORECASE)
        
        if not mentioned_files:
            return ""
        
        context_parts = []
        src_dir = self.project_root / "src"
        max_file_size = 3000  # Max 3KB per file - reduced to prevent Ollama timeout
        
        for filename in set(mentioned_files):  # Remove duplicates
            # Search for file in project
            matches = glob.glob(str(src_dir / "**" / filename), recursive=True)
            
            if matches:
                # Read first match
                file_path = Path(matches[0])
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    rel_path = file_path.relative_to(self.project_root)
                    
                    # Smart truncation: show first 50 lines for large files
                    if len(content) > max_file_size:
                        lines = content.split('\n')
                        total_lines = len(lines)
                        content = '\n'.join(lines[:50])
                        context_parts.append(f"\n[SYSTEM CONTEXT: {rel_path} - First 50/{total_lines} lines (file too large)]")
                        print(f"[Stitch] Truncated {filename}: showing 50/{total_lines} lines")
                    else:
                        context_parts.append(f"\n[SYSTEM CONTEXT: Content of {rel_path}]")
                    
                    context_parts.append(f"```python\n{content}\n```\n")
                    print(f"[Stitch] Read file: {rel_path} ({len(content)} chars)")
                    
                except Exception as e:
                    context_parts.append(f"\n⚠️ [Error reading {filename}: {e}]\n")
                    print(f"[Stitch] Error reading {filename}: {e}")
            else:
                # File not found, but don't break the flow
                print(f"[Stitch] File not found: {filename}")
        
        return "\n".join(context_parts)
        
    async def speak(self, text: str, mode: str = None):
        """
        Send message via Discord webhook as Jules.
        
        Args:
            text: Message content to send
            mode: Optional mode suffix (e.g., "Architect Mode")
        """
        if not self.webhook_url:
            print("⚠️ [Stitch] No webhook URL configured. Falling back to print.")
            print(f"[Jules]: {text}")
            return
        
        # Customize username based on mode
        username = self.username
        if mode:
            username = f"{self.username} [{mode}]"
        
        payload = {
            "content": text,
            "username": username,
            "avatar_url": self.avatar_url
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(self.webhook_url, json=payload) as response:
                    if response.status == 204:
                        print(f"✅ [Stitch] Jules spoke: {text[:50]}...")
                    else:
                        print(f"⚠️ [Stitch] Webhook error: {response.status}")
        except Exception as e:
            print(f"❌ [Stitch] Error sending webhook: {e}")
    
    async def query_ollama(self, prompt: str) -> str:
        """
        Query Ollama API with Jules system prompt (Async).
        
        Args:
            prompt: User input prompt
            
        Returns:
            AI-generated response
        """
        try:
            timeout = aiohttp.ClientTimeout(total=60)
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(
                    f"{self.ollama_url}/api/generate",
                    json={
                        "model": self.model,
                        "prompt": prompt,
                        "system": self.system_prompt,
                        "stream": False
                    }
                ) as response:
                    
                    if response.status == 200:
                        data = await response.json()
                        return data.get('response', 'Ошибка: нет ответа от модели.')
                    else:
                        return f"❌ API Error: {response.status}"
        
        except aiohttp.ClientConnectorError:
            return "❌ Ollama не запущен. Запусти `ollama serve`."
        except asyncio.TimeoutError:
            return "⏱️ Таймаут. Модель слишком долго думает."
        except Exception as e:
            return f"❌ Ошибка: {str(e)}"
    
    async def process_and_reply(self, user_input: str, user_name: str, mode: str = None):
        """
        Process user input with AI and reply via webhook.
        Includes Code Vision - reads mentioned files for context.
        
        Args:
            user_input: User's message
            user_name: Username of the person asking
            mode: Optional mode suffix
        """
        # Step 1: Read mentioned files for code context
        code_context = self._read_mentioned_files(user_input)
        
        # Step 2: Build enriched prompt
        enriched_input = user_input
        if code_context:
            enriched_input = f"{user_input}\n{code_context}"
            print(f"[Stitch] Code Vision activated - files injected into context")
        
        # Step 3: Generate AI response
        print(f"🤖 [Stitch] Processing: {user_input[:50]}... (from {user_name})")
        
        try:
            ai_response = await self.query_ollama(enriched_input)
            
            # If Ollama failed, send error via webhook anyway
            if ai_response.startswith("❌"):
                print(f"[Stitch] Ollama error, sending error message")
                await self.speak(ai_response, mode="Error")
                return
                
        except Exception as e:
            print(f"[Stitch] Critical error: {e}")
            await self.speak(f"❌ Критическая ошибка: {str(e)}", mode="Error")
            return
        
        # Step 4: Send via webhook
        await self.speak(ai_response, mode=mode)
