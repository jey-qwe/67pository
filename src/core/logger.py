"""
Context Logger for Trinity Context Core.

Automatically logs important conversation events and insights
to the memory system with intelligent importance boosting.
"""
import traceback
import sys
import platform
import psutil
import subprocess
from datetime import datetime
from typing import List, Optional, Callable, Any
from functools import wraps
from ..memory.service import MemoryService


class ContextLogger:
    """
    Intelligent logger that commits conversation context to memory.
    
    Features:
    - Direct MemoryService integration (no HTTP overhead)
    - Automatic importance boosting for key topics
    - Auto-tagging with conversation source
    - Timestamp tracking
    """
    
    # Keywords that trigger importance boost
    HIGH_PRIORITY_KEYWORDS = [
        "Фукуока",
        "Trinity", 
        "Баг",
        "Решение",
        "фукуока",
        "trinity",
        "баг",
        "решение"
    ]
    
    BOOSTED_IMPORTANCE = 9
    
    def __init__(self, memory_service: Optional[MemoryService] = None):
        """
        Initialize the Context Logger.
        
        Args:
            memory_service: Optional MemoryService instance. 
                          If not provided, creates a new one.
        """
        self.memory_service = memory_service or MemoryService()
        
    def commit_to_memory(
        self, 
        content: str, 
        tags: List[str], 
        importance: int = 5
    ) -> bool:
        """
        Commit a conversation event to memory with auto-boosting.
        
        Args:
            content: The text content to log
            tags: List of tags for categorization
            importance: Base importance level (1-10)
            
        Returns:
            True if successfully committed, False otherwise
            
        Example:
            >>> logger = ContextLogger()
            >>> logger.commit_to_memory(
            ...     "User wants to move to Фукуока after graduating",
            ...     ["goal", "location"],
            ...     importance=7
            ... )
            True
        """
        # Auto-boost importance if content contains key topics
        final_importance = self._calculate_importance(content, importance)
        
        # Add the memory card
        card = self.memory_service.add_card(
            content=content,
            tags=tags,
            source="conversation_auto_log",
            importance=final_importance
        )
        
        if card:
            print(f"[ContextLogger] Logged to memory (importance: {final_importance})")
            if final_importance > importance:
                print(f"  [BOOST] Importance raised: {importance} -> {final_importance}")
            return True
        else:
            print(f"[ContextLogger] Failed to log to memory")
            return False
    
    def _calculate_importance(self, content: str, base_importance: int) -> int:
        """
        Calculate final importance with keyword-based boosting.
        
        Args:
            content: Text to analyze
            base_importance: Original importance level
            
        Returns:
            Final importance (max of base or boosted)
        """
        # Check if content contains any high-priority keywords
        for keyword in self.HIGH_PRIORITY_KEYWORDS:
            if keyword in content:
                # Return the higher of base importance or boosted importance
                return max(base_importance, self.BOOSTED_IMPORTANCE)
        
        return base_importance
    
    def log_insight(self, insight: str, tags: List[str] = None) -> bool:
        """
        Convenience method for logging conversation insights.
        
        Args:
            insight: The insight text
            tags: Optional tags (defaults to ["insight"])
            
        Returns:
            True if successful
        """
        if tags is None:
            tags = ["insight"]
        
        return self.commit_to_memory(
            content=insight,
            tags=tags,
            importance=6
        )
    
    def log_bug(self, bug_description: str, tags: List[str] = None) -> bool:
        """
        Convenience method for logging bugs/issues.
        
        Args:
            bug_description: Description of the bug
            tags: Optional tags (defaults to ["bug", "issue"])
            
        Returns:
            True if successful
        """
        if tags is None:
            tags = ["bug", "issue"]
        elif "bug" not in tags:
            tags.append("bug")
        
        return self.commit_to_memory(
            content=f"Баг: {bug_description}",
            tags=tags,
            importance=8
        )
    
    def log_solution(self, solution: str, tags: List[str] = None) -> bool:
        """
        Convenience method for logging solutions.
        
        Args:
            solution: Description of the solution
            tags: Optional tags (defaults to ["solution", "fix"])
            
        Returns:
            True if successful
        """
        if tags is None:
            tags = ["solution", "fix"]
        elif "solution" not in tags:
            tags.append("solution")
        
        return self.commit_to_memory(
            content=f"Решение: {solution}",
            tags=tags,
            importance=8
        )
    
    def get_stats(self) -> dict:
        """
        Get statistics about logged memories.
        
        Returns:
            Dictionary with memory stats
        """
        all_cards = self.memory_service.get_all_cards()
        auto_logged = [c for c in all_cards if c.source == "conversation_auto_log"]
        
        return {
            "total_memories": len(all_cards),
            "auto_logged": len(auto_logged),
            "high_importance": len([c for c in auto_logged if c.importance >= 8])
        }


# ============================================================================
# Error Interceptor System
# ============================================================================

class SystemMonitor:
    """Monitor system state for error context."""
    
    @staticmethod
    def get_system_state() -> dict:
        """
        Get current system state.
        
        Returns:
            Dictionary with system metrics
        """
        try:
            # Get memory info
            memory = psutil.virtual_memory()
            
            # Get Docker status
            docker_status = SystemMonitor._check_docker_status()
            
            return {
                "ram_used_gb": round(memory.used / (1024**3), 2),
                "ram_total_gb": round(memory.total / (1024**3), 2),
                "ram_percent": memory.percent,
                "docker_running": docker_status,
                "platform": platform.system(),
                "python_version": sys.version.split()[0]
            }
        except Exception as e:
            return {
                "error": f"Could not get system state: {e}"
            }
    
    @staticmethod
    def _check_docker_status() -> bool:
        """Check if Docker is running."""
        try:
            result = subprocess.run(
                ["docker", "ps"],
                capture_output=True,
                timeout=2
            )
            return result.returncode == 0
        except Exception:
            return False


class ErrorInterceptor:
    """
    Error interceptor with automatic memory logging.
    
    Captures exceptions with full system context and logs them
    as high-priority error cards.
    """
    
    # Keywords indicating mentor sync issues
    MENTOR_SYNC_KEYWORDS = [
        "race condition",
        "concurrent",
        "context compression",
        "duplicate",
        "conflict",
        "sync",
        "lock",
        "deadlock",
        "timeout"
    ]
    
    def __init__(self, logger: ContextLogger = None):
        """
        Initialize error interceptor.
        
        Args:
            logger: ContextLogger instance
        """
        self.logger = logger or ContextLogger()
    
    def catch_logic_error(
        self, 
        agent_name: str = "Mahoraga",
        phase_ref: Optional[str] = None
    ) -> Callable:
        """
        Decorator to catch and log logic errors.
        
        Args:
            agent_name: Name of the agent (Mahoraga, Muezzin, etc.)
            phase_ref: Optional phase reference for async tasks
            
        Usage:
            @catch_logic_error(agent_name="Mahoraga", phase_ref="task_123")
            def process_data(arg1, arg2):
                # Your code here
                pass
        """
        def decorator(func: Callable) -> Callable:
            @wraps(func)
            def wrapper(*args, **kwargs) -> Any:
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    self._handle_error(
                        exception=e,
                        func_name=func.__name__,
                        agent_name=agent_name,
                        phase_ref=phase_ref,
                        args=args,
                        kwargs=kwargs
                    )
                    # Re-raise the exception after logging
                    raise
            
            @wraps(func)
            async def async_wrapper(*args, **kwargs) -> Any:
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    self._handle_error(
                        exception=e,
                        func_name=func.__name__,
                        agent_name=agent_name,
                        phase_ref=phase_ref,
                        args=args,
                        kwargs=kwargs
                    )
                    # Re-raise the exception after logging
                    raise
            
            # Return async wrapper if function is async
            if sys.version_info >= (3, 10):
                import inspect
                if inspect.iscoroutinefunction(func):
                    return async_wrapper
            
            return wrapper
        
        return decorator
    
    def _handle_error(
        self,
        exception: Exception,
        func_name: str,
        agent_name: str,
        phase_ref: Optional[str],
        args: tuple,
        kwargs: dict
    ):
        """
        Handle caught error and log to memory.
        
        Args:
            exception: The caught exception
            func_name: Name of the function
            agent_name: Name of the agent
            phase_ref: Phase reference
            args: Function arguments
            kwargs: Function keyword arguments
        """
        try:
            # Get error trace
            error_trace = traceback.format_exc()
            
            # Get system state
            system_state = SystemMonitor.get_system_state()
            
            # Build error content
            content_parts = [
                f"[ERROR] {agent_name}.{func_name}",
                f"Exception: {type(exception).__name__}: {str(exception)}",
                f"",
                f"System State:",
                f"  RAM: {system_state.get('ram_used_gb', '?')}/{system_state.get('ram_total_gb', '?')} GB ({system_state.get('ram_percent', '?')}%)",
                f"  Docker: {'Running' if system_state.get('docker_running') else 'Not Running'}",
                f"  Platform: {system_state.get('platform', 'Unknown')}",
                f"",
                f"Function Arguments:",
                f"  Args: {self._format_args(args)}",
                f"  Kwargs: {self._format_args(kwargs)}",
            ]
            
            if phase_ref:
                content_parts.insert(2, f"Phase: {phase_ref}")
            
            content_parts.append("")
            content_parts.append("Traceback:")
            content_parts.append(error_trace)
            
            content = "\n".join(content_parts)
            
            # Detect mentor sync issues
            tags = ["error", "intercepted", agent_name.lower()]
            if phase_ref:
                tags.append("async_task")
            
            # Check for mentor sync keywords
            error_text = f"{str(exception)} {error_trace}".lower()
            if any(keyword in error_text for keyword in self.MENTOR_SYNC_KEYWORDS):
                tags.append("mentor_sync_issue")
            
             # Log to memory with maximum importance
            self.logger.commit_to_memory(
                content=content,
                tags=tags,
                importance=10  # Critical errors always get max importance
            )
            
            print(f"[ErrorInterceptor] Error logged to memory with importance 10")
            
        except Exception as log_error:
            # Fail silently - don't let logging errors break the application
            print(f"[ErrorInterceptor] Failed to log error: {log_error}")
    
    def _format_args(self, args_data: Any) -> str:
        """
        Format arguments for logging.
        
        Args:
            args_data: Arguments to format
            
        Returns:
            Formatted string
        """
        try:
            if isinstance(args_data, dict):
                if not args_data:
                    return "{}"
                return str({k: str(v)[:100] for k, v in args_data.items()})
            elif isinstance(args_data, (list, tuple)):
                if not args_data:
                    return "[]"
                return str([str(x)[:100] for x in args_data])
            else:
                return str(args_data)[:200]
        except Exception:
            return "<unable to format>"


# Global error interceptor instance
_error_interceptor = ErrorInterceptor()


def catch_logic_error(
    agent_name: str = "Mahoraga",
    phase_ref: Optional[str] = None
):
    """
    Decorator to catch and automatically log logic errors.
    
    Args:
        agent_name: Name of the agent (default: "Mahoraga")
        phase_ref: Optional phase reference for async tasks
        
    Example:
        @catch_logic_error(agent_name="Mahoraga", phase_ref="task_001")
        def risky_function(data):
            # Code that might raise exceptions
            return process(data)
    """
    return _error_interceptor.catch_logic_error(
        agent_name=agent_name,
        phase_ref=phase_ref
    )
