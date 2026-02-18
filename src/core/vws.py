"""
Virtual Workspace System (VWS) for Trinity Context Core.

Provides intelligent file navigation and workspace management:
- Contextual file listing with Qdrant tags
- Focused project tree generation
- File access control via WorkspaceManifest
"""
import os
import pathlib
from typing import List, Dict, Set, Optional, Tuple
from datetime import datetime
from ..memory.service import MemoryService


class GitignoreParser:
    """Parse and apply .gitignore rules."""
    
    def __init__(self, root_path: str):
        """
        Initialize gitignore parser.
        
        Args:
            root_path: Root directory path
        """
        self.root_path = pathlib.Path(root_path)
        self.patterns = self._load_gitignore()
    
    def _load_gitignore(self) -> List[str]:
        """
        Load .gitignore patterns.
        
        Returns:
            List of gitignore patterns
        """
        gitignore_path = self.root_path / ".gitignore"
        patterns = []
        
        if gitignore_path.exists():
            try:
                with open(gitignore_path, 'r', encoding='utf-8') as f:
                    for line in f:
                        line = line.strip()
                        # Skip comments and empty lines
                        if line and not line.startswith('#'):
                            patterns.append(line)
            except Exception as e:
                print(f"[VWS] Could not read .gitignore: {e}")
        
        # Add common patterns if no gitignore
        if not patterns:
            patterns = [
                "__pycache__",
                "*.pyc",
                ".git",
                ".env",
                "node_modules",
                "venv",
                ".venv"
            ]
        
        return patterns
    
    def should_ignore(self, path: str) -> bool:
        """
        Check if path should be ignored.
        
        Args:
            path: File or directory path
            
        Returns:
            True if should be ignored
        """
        path_obj = pathlib.Path(path)
        name = path_obj.name
        
        for pattern in self.patterns:
            # Simple pattern matching
            if pattern.endswith('/'):
                # Directory pattern
                if path_obj.is_dir() and name == pattern[:-1]:
                    return True
            elif '*' in pattern:
                # Wildcard pattern
                if pattern.startswith('*.'):
                    ext = pattern[1:]
                    if name.endswith(ext):
                        return True
            else:
                # Exact match
                if name == pattern:
                    return True
        
        return False


class WorkspaceManifest:
    """
    Manages file access permissions for Mahoraga.
    
    Files in the manifest are "mounted" and can be read fully.
    Other files are only visible (existence known) but not readable.
    """
    
    def __init__(self):
        """Initialize workspace manifest."""
        self.mounted_files: Set[str] = set()
        self.session_start = datetime.utcnow()
        self.active_folders: Set[str] = set()
    
    def mount(self, file_path: str) -> bool:
        """
        Mount a file for full access.
        
        Args:
            file_path: Absolute path to file
            
        Returns:
            True if mounted successfully
        """
        abs_path = os.path.abspath(file_path)
        if os.path.exists(abs_path):
            self.mounted_files.add(abs_path)
            # Track active folder
            folder = os.path.dirname(abs_path)
            self.active_folders.add(folder)
            return True
        return False
    
    def unmount(self, file_path: str):
        """
        Unmount a file.
        
        Args:
            file_path: Absolute path to file
        """
        abs_path = os.path.abspath(file_path)
        self.mounted_files.discard(abs_path)
    
    def is_mounted(self, file_path: str) -> bool:
        """
        Check if file is mounted.
        
        Args:
            file_path: Path to check
            
        Returns:
            True if file has full access
        """
        abs_path = os.path.abspath(file_path)
        return abs_path in self.mounted_files
    
    def get_mounted_files(self) -> List[str]:
        """
        Get list of mounted files.
        
        Returns:
            List of mounted file paths
        """
        return sorted(list(self.mounted_files))
    
    def clear(self):
        """Clear all mounted files."""
        self.mounted_files.clear()
        self.active_folders.clear()


class VirtualWorkspace:
    """
    Virtual Workspace System with intelligent file management.
    
    Liar's Requiem: Files are tagged with context from Qdrant.
    """
    
    def __init__(
        self, 
        root_path: str,
        memory_service: Optional[MemoryService] = None
    ):
        """
        Initialize VWS.
        
        Args:
            root_path: Project root directory
            memory_service: Optional MemoryService for tag retrieval
        """
        self.root_path = os.path.abspath(root_path)
        self.gitignore = GitignoreParser(self.root_path)
        self.manifest = WorkspaceManifest()
        self.memory_service = memory_service or MemoryService()
    
    def ls_contextual(
        self, 
        path: str = ".",
        show_tags: bool = True
    ) -> List[Dict[str, any]]:
        """
        List directory with contextual information.
        
        Filters based on .gitignore and adds Qdrant tags.
        
        Args:
            path: Directory path (relative to root or absolute)
            show_tags: Whether to fetch and show tags from Qdrant
            
        Returns:
            List of file info dicts with name, type, mounted status, tags
        """
        # Resolve path
        if os.path.isabs(path):
            target_path = path
        else:
            target_path = os.path.join(self.root_path, path)
        
        if not os.path.exists(target_path):
            return []
        
        if not os.path.isdir(target_path):
            return []
        
        results = []
        
        try:
            entries = os.listdir(target_path)
        except PermissionError:
            return []
        
        for entry in sorted(entries):
            entry_path = os.path.join(target_path, entry)
            
            # Apply gitignore filter
            if self.gitignore.should_ignore(entry_path):
                continue
            
            # Get file info
            is_dir = os.path.isdir(entry_path)
            is_mounted = self.manifest.is_mounted(entry_path)
            
            file_info = {
                "name": entry,
                "type": "dir" if is_dir else "file",
                "path": entry_path,
                "mounted": is_mounted,
                "tags": []
            }
            
            # Add tags from Qdrant (Liar's Requiem)
            if show_tags and not is_dir:
                tags = self._get_file_tags(entry_path)
                file_info["tags"] = tags
            
            results.append(file_info)
        
        return results
    
    def tree_focused(
        self,
        max_depth: int = 3,
        focus_active: bool = True
    ) -> str:
        """
        Generate focused project tree.
        
        Args:
            max_depth: Maximum depth to traverse
            focus_active: Prioritize active folders from session
            
        Returns:
            Tree structure as string
        """
        lines = []
        lines.append(f"[ROOT] {os.path.basename(self.root_path)}/")
        
        # Build tree
        self._build_tree(
            self.root_path,
            lines,
            prefix="",
            depth=0,
            max_depth=max_depth,
            focus_active=focus_active
        )
        
        return "\n".join(lines)
    
    def _build_tree(
        self,
        path: str,
        lines: List[str],
        prefix: str,
        depth: int,
        max_depth: int,
        focus_active: bool
    ):
        """Recursively build tree structure."""
        if depth >= max_depth:
            return
        
        try:
            entries = sorted(os.listdir(path))
        except PermissionError:
            return
        
        # Filter ignored files
        entries = [
            e for e in entries 
            if not self.gitignore.should_ignore(os.path.join(path, e))
        ]
        
        # If focusing on active folders, prioritize them
        if focus_active:
            active_entries = [
                e for e in entries
                if os.path.join(path, e) in self.manifest.active_folders
            ]
            other_entries = [e for e in entries if e not in active_entries]
            entries = active_entries + other_entries
        
        for i, entry in enumerate(entries):
            entry_path = os.path.join(path, entry)
            is_last = i == len(entries) - 1
            is_dir = os.path.isdir(entry_path)
            is_mounted = self.manifest.is_mounted(entry_path)
            is_active = entry_path in self.manifest.active_folders
            
            # Tree characters (ASCII only for Windows compatibility)
            connector = "+-- " if is_last else "|-- "
            
            # Icon and formatting using ASCII
            if is_dir:
                icon = "[DIR*]" if is_active else "[DIR]"
                name = f"{entry}/"
            else:
                icon = "[FILE+]" if is_mounted else "[FILE]"
                name = entry
            
            lines.append(f"{prefix}{connector}{icon} {name}")
            
            # Recurse for directories
            if is_dir:
                new_prefix = prefix + ("    " if is_last else "|   ")
                self._build_tree(
                    entry_path,
                    lines,
                    new_prefix,
                    depth + 1,
                    max_depth,
                    focus_active
                )
    
    def _get_file_tags(self, file_path: str) -> List[str]:
        """
        Get tags for a file from Qdrant.
        
        This is the "Liar's Requiem" - files reveal their nature
        through tags stored in memory.
        
        Args:
            file_path: Path to file
            
        Returns:
            List of tags associated with this file
        """
        try:
            # Search for cards mentioning this file
            filename = os.path.basename(file_path)
            cards = self.memory_service.search(filename, limit=5)
            
            # Collect unique tags
            tags = set()
            for card in cards:
                tags.update(card.tags)
            
            return sorted(list(tags))
        except Exception:
            return []


# Global workspace instance
_workspace: Optional[VirtualWorkspace] = None


def get_workspace(root_path: str = None) -> VirtualWorkspace:
    """
    Get or create global workspace instance.
    
    Args:
        root_path: Project root path
        
    Returns:
        VirtualWorkspace instance
    """
    global _workspace
    
    if _workspace is None:
        if root_path is None:
            root_path = os.getcwd()
        _workspace = VirtualWorkspace(root_path)
    
    return _workspace
