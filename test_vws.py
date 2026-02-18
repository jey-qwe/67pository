"""
Test script for Virtual Workspace System (VWS).

Tests ls_contextual, tree_focused, and WorkspaceManifest.
"""
import os
from src.core.vws import VirtualWorkspace, get_workspace


def test_vws():
    """Test VWS functionality."""
    print("=" * 60)
    print("Virtual Workspace System Test")
    print("=" * 60)
    print()
    
    # Get project root (find Quasar directory)
    current_dir = os.path.abspath(__file__)
    while current_dir != os.path.dirname(current_dir):
        if os.path.basename(current_dir) == "Quasar":
            project_root = current_dir
            break
        current_dir = os.path.dirname(current_dir)
    else:
        project_root = os.getcwd()
    
    print(f"Project root: {project_root}")
    print()
    
    # Initialize workspace
    print("--- Initializing VWS ---")
    ws = VirtualWorkspace(project_root)
    print("[SUCCESS] Workspace initialized")
    print(f"Gitignore patterns loaded: {len(ws.gitignore.patterns)}")
    print()
    
    # Test 1: ls_contextual on src directory
    print("--- Test 1: ls_contextual('src') ---")
    src_files = ws.ls_contextual("src", show_tags=False)
    print(f"Found {len(src_files)} items in src/:")
    for item in src_files[:10]:  # Show first 10
        icon = "[DIR]" if item['type'] == 'dir' else "[FILE]"
        mounted = "[MOUNTED]" if item['mounted'] else ""
        print(f"  {icon} {item['name']} {mounted}")
    print()
    
    # Test 2: Mount some files
    print("--- Test 2: Mounting files ---")
    test_files = [
        os.path.join(project_root, "src", "main.py"),
        os.path.join(project_root, "src", "core", "logger.py"),
        os.path.join(project_root, "src", "memory", "service.py")
    ]
    
    for file_path in test_files:
        if os.path.exists(file_path):
            success = ws.manifest.mount(file_path)
            rel_path = os.path.relpath(file_path, project_root)
            print(f"  {'[OK]' if success else '[FAIL]'} {rel_path}")
    
    print(f"\nMounted files: {len(ws.manifest.get_mounted_files())}")
    print(f"Active folders: {len(ws.manifest.active_folders)}")
    print()
    
    # Test 3: ls_contextual with mounted files
    print("--- Test 3: ls_contextual('src/core') with mounted files ---")
    core_files = ws.ls_contextual("src/core", show_tags=False)
    print(f"Found {len(core_files)} items in src/core/:")
    for item in core_files:
        icon = "[DIR]" if item['type'] == 'dir' else ("[FILE+]" if item['mounted'] else "[FILE]")
        mounted = "[MOUNTED]" if item['mounted'] else ""
        print(f"  {icon} {item['name']} {mounted}")
    print()
    
    # Test 4: tree_focused
    print("--- Test 4: tree_focused (depth=3, focus on active) ---")
    tree = ws.tree_focused(max_depth=3, focus_active=True)
    print(tree)
    print()
    
    # Test 5: Check gitignore filtering
    print("--- Test 5: Gitignore filtering ---")
    test_paths = [
        "__pycache__",
        "venv",
        ".git",
        "src/main.py",
        "README.md"
    ]
    
    for path in test_paths:
        ignored = ws.gitignore.should_ignore(path)
        status = "IGNORED" if ignored else "VISIBLE"
        print(f"  {path}: {status}")
    print()
    
    # Test 6: Workspace stats
    print("--- Test 6: Workspace Statistics ---")
    print(f"Root: {ws.root_path}")
    print(f"Mounted files: {len(ws.manifest.mounted_files)}")
    print(f"Active folders: {len(ws.manifest.active_folders)}")
    print(f"Gitignore patterns: {len(ws.gitignore.patterns)}")
    print()
    
    # Test 7: Global workspace instance
    print("--- Test 7: Global workspace instance ---")
    ws_global = get_workspace(project_root)
    print(f"Same instance: {ws_global is get_workspace()}")
    print()
    
    print("=" * 60)
    print("[COMPLETE] VWS test finished")
    print("=" * 60)


if __name__ == "__main__":
    try:
        test_vws()
    except Exception as e:
        print(f"[ERROR] Test failed: {e}")
        import traceback
        traceback.print_exc()
