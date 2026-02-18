"""
Pydantic models for Trinity Context Core memory system.

Ultimate schema with comprehensive error tracking, system state,
VWS integration, and architectural decision documentation.
"""
from datetime import datetime
from typing import List, Optional, Dict, Any
from uuid import UUID, uuid4
from pydantic import BaseModel, Field, ConfigDict


class ContextCard(BaseModel):
    """
    Ultimate data model for storing context/memory cards.
    
    Comprehensive tracking for:
    - Core knowledge and solutions
    - Error traces with code diffs and phase states
    - System environment and resources
    - VWS file relationships and dependencies
    - Architectural decision context
    """
    # ========================================================================
    # Core Fields
    # ========================================================================
    
    id: UUID = Field(
        default_factory=uuid4,
        description="Unique identifier for the context card"
    )
    
    content: str = Field(
        ...,
        description="Core solution or knowledge (required)"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Categorization tags (e.g., ['rust', 'mcp', 'fukuoka'])"
    )
    
    source: str = Field(
        default="manual",
        description="Information source: 'manual', 'autonomous_logger', 'user', 'system'"
    )
    
    importance: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority weight (1-10)"
    )
    
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        description="Creation timestamp"
    )
    
    embedding: Optional[List[float]] = Field(
        default=None,
        description="Vector representation for semantic search"
    )
    
    # ========================================================================
    # Logic Logs - Enhanced Error Tracking
    # ========================================================================
    
    logic_logs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="""Error tracking and debugging data:
        - error_trace (str): Full stack trace
        - failed_attempts (List[str]): What didn't work
        - code_diff (str): Before/After changes (Logic Diffs)
        - phase_ref_state (str): Async task state (Ghost State protection)
        """
    )
    
    # ========================================================================
    # System State - Environment Tracking
    # ========================================================================
    
    system_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="""System environment data:
        - os_version (str): e.g., 'WSL 2.6.3', 'Windows 11'
        - resources (str): e.g., 'RAM 4GB limit'
        - hardware (str): e.g., 'Thunderobot'
        """
    )
    
    # ========================================================================
    # VWS Metadata - File Relationships
    # ========================================================================
    
    vws_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="""Virtual Workspace System metadata:
        - related_files (List[str]): File paths (VWS anchors)
        - dependencies (List[str]): Related modules (Dependency Awareness)
        """
    )
    
    # ========================================================================
    # Decision Context - Architectural Reasoning
    # ========================================================================
    
    decision_context: str = Field(
        default="",
        description="Architect's reasoning and decision rationale"
    )
    
    # ========================================================================
    # Pydantic Configuration
    # ========================================================================
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "content": "Fixed Qdrant search API compatibility issue",
                "tags": ["qdrant", "api", "fix", "search"],
                "source": "manual",
                "importance": 9,
                "created_at": "2026-02-17T18:00:00Z",
                "embedding": None,
                "logic_logs": {
                    "error_trace": "'QdrantClient' object has no attribute 'search'",
                    "failed_attempts": [
                        "Tried updating qdrant-client version",
                        "Checked for deprecated methods"
                    ],
                    "code_diff": "- results = client.search(...)\n+ results = client.query_points(...)",
                    "phase_ref_state": "search_implementation_v2"
                },
                "system_state": {
                    "os_version": "Windows 11",
                    "resources": "16GB RAM (75% used)",
                    "hardware": "Thunderobot"
                },
                "vws_metadata": {
                    "related_files": ["src/memory/service.py", "test_memory.py"],
                    "dependencies": ["qdrant-client", "pytest"]
                },
                "decision_context": "API changed in Qdrant v1.x. query_points() is the new method with results in .points attribute"
            }
        }
    )


class CreateCardRequest(BaseModel):
    """
    Request model for creating a new context card.
    
    Excludes auto-generated fields (id, embedding, created_at).
    All fields except 'content' have defaults for flexibility.
    """
    
    content: str = Field(
        ...,
        min_length=1,
        description="Core solution or knowledge (required)"
    )
    
    tags: List[str] = Field(
        default_factory=list,
        description="Categorization tags"
    )
    
    source: str = Field(
        default="manual",
        description="Information source"
    )
    
    importance: int = Field(
        default=5,
        ge=1,
        le=10,
        description="Priority weight (1-10)"
    )
    
    # Optional advanced fields
    logic_logs: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Error trace, failed attempts, code diff, phase state"
    )
    
    system_state: Optional[Dict[str, Any]] = Field(
        default=None,
        description="OS version, resources, hardware"
    )
    
    vws_metadata: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Related files and dependencies"
    )
    
    decision_context: str = Field(
        default="",
        description="Architectural reasoning"
    )
    
    model_config = ConfigDict(
        populate_by_name=True,
        json_schema_extra={
            "example": {
                "content": "Implemented autonomous middleware for API logging",
                "tags": ["middleware", "fastapi", "logging"],
                "source": "manual",
                "importance": 8,
                "logic_logs": {
                    "error_trace": "Request body consumed, endpoint received empty data",
                    "failed_attempts": ["Simple await request.body()", "Middleware after routing"],
                    "code_diff": "+ async def receive():\n+     return {'type': 'http.request', 'body': body_bytes}",
                    "phase_ref_state": "middleware_v3_stable"
                },
                "system_state": {
                    "os_version": "Windows 11",
                    "resources": "16GB RAM available",
                    "hardware": "Thunderobot"
                },
                "vws_metadata": {
                    "related_files": ["src/api/middleware.py", "src/main.py"],
                    "dependencies": ["fastapi", "starlette"]
                },
                "decision_context": "Cache body before routing, recreate receive callable to preserve for endpoint"
            }
        }
    )


class SearchRequest(BaseModel):
    """Request model for searching context cards."""
    
    query: str = Field(
        ...,
        min_length=1,
        description="Search query text"
    )
    
    limit: int = Field(
        default=10,
        ge=1,
        le=100,
        description="Maximum number of results"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "query": "python error handling strategies",
                "limit": 5
            }
        }
    )


class SearchResponse(BaseModel):
    """Response model for search results."""
    
    results: List[ContextCard] = Field(
        default_factory=list,
        description="Matching context cards"
    )
    
    total: int = Field(
        ...,
        description="Total results found"
    )
    
    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "results": [],
                "total": 0
            }
        }
    )
