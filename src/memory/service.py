"""
Memory Service for managing context cards in Qdrant vector database.
"""
import uuid
from datetime import datetime
from typing import List, Optional
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
    SearchRequest
)

from ..core.config import settings
from ..core.gemini_client import get_embedding, get_query_embedding
from .schemas import ContextCard, CreateCardRequest


class MemoryService:
    """
    Service for managing context cards in Qdrant vector database.
    
    Handles storage, retrieval, and semantic search of memory cards
    using Gemini embeddings for similarity-based queries.
    """
    
    def __init__(self, client: Optional[QdrantClient] = None):
        """
        Initialize the Memory Service.
        
        Args:
            client: Optional QdrantClient instance. If not provided, attempts to connect to
                   configured Qdrant or falls back to in-memory mode.
        """
        # Initialize Qdrant client
        if client:
            self.client = client
            self.collection_name = settings.COLLECTION_NAME
        else:
            # Try to connect to Docker Qdrant first
            try:
                self.client = QdrantClient(
                    host=settings.QDRANT_HOST,
                    port=settings.QDRANT_PORT,
                    api_key=settings.QDRANT_API_KEY if settings.QDRANT_API_KEY else None,
                    timeout=5.0  # Short timeout to fail fast if Docker isn't running
                )
                # Test the connection
                self.client.get_collections()
                print(f"[INFO] Connected to Qdrant at {settings.QDRANT_HOST}:{settings.QDRANT_PORT}")
                self.collection_name = settings.COLLECTION_NAME
            except Exception as e:
                # Fall back to in-memory mode
                print(f"[WARNING] Could not connect to Qdrant Docker: {e}")
                print("[INFO] Using in-memory Qdrant (data will not persist)")
                self.client = QdrantClient(":memory:")
                self.collection_name = settings.COLLECTION_NAME
        
        # Create collection if it doesn't exist
        self._ensure_collection_exists()
    
    def _ensure_collection_exists(self):
        """Create the Qdrant collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        collection_names = [col.name for col in collections]
        
        if self.collection_name not in collection_names:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=3072,  # Gemini embedding-001 actual dimension
                    distance=Distance.COSINE
                )
            )
            print(f"Created collection: {self.collection_name}")
    
    def add_card(
        self,
        content: str,
        tags: List[str],
        source: str = "manual",
        importance: int = 5,
        logic_logs: Optional[dict] = None,
        system_state: Optional[dict] = None,
        vws_metadata: Optional[dict] = None,
        decision_context: str = ""
    ) -> Optional[ContextCard]:
        """
        Add a new context card to the memory.
        
        Args:
            content: Text content of the memory/fact
            tags: List of tags for categorization
            source: Source of the information (default: "manual")
            importance: Importance weight (1-10, default: 5)
            logic_logs: Optional error tracking (error_trace, failed_attempts, code_diff, phase_ref_state)
            system_state: Optional system environment (os_version, resources, hardware)
            vws_metadata: Optional VWS data (related_files, dependencies)
            decision_context: Optional architectural reasoning (default: "")
            
        Returns:
            ContextCard object if successful, None otherwise
        """
        # Generate embedding for the content
        embedding = get_embedding(content)
        
        if embedding is None:
            print(f"Failed to generate embedding for content: {content[:50]}...")
            return None
        
        # Create unique ID
        card_id = str(uuid.uuid4())
        
        # Create timestamp
        created_at = datetime.utcnow()
        
        # Prepare payload
        payload = {
            "content": content,
            "tags": tags,
            "source": source,
            "importance": importance,
            "created_at": created_at.isoformat(),
            "decision_context": decision_context
        }
        
        # Add optional fields if provided
        if logic_logs is not None:
            payload["logic_logs"] = logic_logs
        if system_state is not None:
            payload["system_state"] = system_state
        if vws_metadata is not None:
            payload["vws_metadata"] = vws_metadata
        
        # Create point
        point = PointStruct(
            id=card_id,
            vector=embedding,
            payload=payload
        )
        
        # Insert into Qdrant
        try:
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            # Create and return ContextCard object
            card = ContextCard(
                id=uuid.UUID(card_id),
                content=content,
                tags=tags,
                source=source,
                importance=importance,
                created_at=created_at,
                embedding=embedding,
                logic_logs=logic_logs,
                system_state=system_state,
                vws_metadata=vws_metadata,
                decision_context=decision_context
            )
            
            print(f"Successfully added card: {card_id}")
            return card
            
        except Exception as e:
            print(f"Error adding card to Qdrant: {e}")
            return None
    
    def add_memory(self, card: ContextCard) -> Optional[ContextCard]:
        """
        Add a memory using a complete ContextCard object.
        
        This method accepts a ContextCard object and stores it in Qdrant,
        using model_dump() to preserve all nested structures.
        
        Args:
            card: ContextCard object with all fields populated
            
        Returns:
            The same ContextCard object if successful, None otherwise
        """
        try:
            # Generate embedding if not provided
            if card.embedding is None:
                card.embedding = get_embedding(card.content)
                if card.embedding is None:
                    print(f"Failed to generate embedding for content")
                    return None
            
            # Use model_dump to get all fields as dict
            payload = card.model_dump(exclude={'id', 'embedding'})
            
            # Convert datetime to ISO string
            if 'created_at' in payload and isinstance(payload['created_at'], datetime):
                payload['created_at'] = payload['created_at'].isoformat()
            
            # Create point
            point = PointStruct(
                id=str(card.id),
                vector=card.embedding,
                payload=payload
            )
            
            # Insert into Qdrant
            self.client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )
            
            print(f"Successfully added memory: {card.id}")
            return card
            
        except Exception as e:
            print(f"Error adding memory to Qdrant: {e}")
            return None
    
    def verify_execution(
        self,
        card_id: str,
        success: bool,
        output: str = ""
    ) -> bool:
        """
        Verify execution of a card and mark it with success seal.
        
        Updates the logic_logs.execution_verified field.
        Success = "Печать Успеха" (Success Seal)
        
        Args:
            card_id: UUID string of the card
            success: Whether execution was successful
            output: Optional execution output/result
            
        Returns:
            True if update successful, False otherwise
        """
        try:
            # Retrieve the card
            card = self.get_card_by_id(card_id)
            if not card:
                print(f"Card {card_id} not found")
                return False
            
            # Update logic_logs
            if card.logic_logs is None:
                card.logic_logs = {}
            
            card.logic_logs["execution_verified"] = "Печать Успеха" if success else "Failed"
            
            if output:
                card.logic_logs["execution_output"] = output
            
            card.logic_logs["verified_at"] = datetime.utcnow().isoformat()
            
            # Update in Qdrant using set_payload
            self.client.set_payload(
                collection_name=self.collection_name,
                payload={"logic_logs": card.logic_logs},
                points=[card_id]
            )
            
            print(f"{'[OK]' if success else '[FAIL]'} Execution verified for card {card_id}")
            return True
            
        except Exception as e:
            print(f"Error verifying execution for card {card_id}: {e}")
            return False
    
    def search(
        self,
        query: str,
        limit: int = 10,
        score_threshold: float = 0.5,
        min_importance: Optional[int] = None,
        verified_only: bool = False
    ) -> List[ContextCard]:
        """
        Search for context cards using semantic similarity with optional filtering.
        
        Args:
            query: Search query text
            limit: Maximum number of results to return
            score_threshold: Minimum similarity score (0-1)
            min_importance: Optional minimum importance level (1-10)
            verified_only: If True, only return cards with "Печать Успеха"
            
        Returns:
            List of matching ContextCard objects
        """
        # Generate query embedding
        query_embedding = get_query_embedding(query)
        
        if query_embedding is None:
            print(f"Failed to generate embedding for query: {query}")
            return []
        
        # Build query filter if needed
        query_filter = None
        if min_importance is not None or verified_only:
            from qdrant_client.models import Range
            
            conditions = []
            if min_importance is not None:
                conditions.append(
                    FieldCondition(
                        key="importance",
                        range=Range(gte=min_importance)
                    )
                )
            
            if verified_only:
                conditions.append(
                    FieldCondition(
                        key="logic_logs.execution_verified",
                        match=MatchValue(value="Печать Успеха")
                    )
                )
            
            if conditions:
                query_filter = Filter(must=conditions)
        
        # Search in Qdrant using query_points (new API)
        try:
            search_results = self.client.query_points(
                collection_name=self.collection_name,
                query=query_embedding,
                limit=limit,
                score_threshold=score_threshold,
                query_filter=query_filter
            )
            
            # Convert results to ContextCard objects
            cards = []
            for result in search_results.points:
                card = self._point_to_card(result)
                if card:
                    cards.append(card)
            
            return cards
            
        except Exception as e:
            print(f"Error searching Qdrant: {e}")
            return []
    
    def get_card_by_id(self, card_id: str) -> Optional[ContextCard]:
        """
        Retrieve a specific card by its ID.
        
        Args:
            card_id: UUID string of the card
            
        Returns:
            ContextCard object if found, None otherwise
        """
        try:
            result = self.client.retrieve(
                collection_name=self.collection_name,
                ids=[card_id],
                with_vectors=True
            )
            
            if not result:
                return None
            
            point = result[0]
            card = self._point_to_card(point)
            
            return card
            
        except Exception as e:
            print(f"Error retrieving card {card_id}: {e}")
            return None
    
    def get_cards_by_tag(self, tag: str, limit: int = 50) -> List[ContextCard]:
        """
        Retrieve cards filtered by a specific tag.
        
        Args:
            tag: Tag to filter by
            limit: Maximum number of results
            
        Returns:
            List of matching ContextCard objects
        """
        try:
            # Use scroll to get all matching cards
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                scroll_filter=Filter(
                    must=[
                        FieldCondition(
                            key="tags",
                            match=MatchValue(value=tag)
                        )
                    ]
                ),
                limit=limit,
                with_vectors=False
            )
            
            # Convert to ContextCard objects
            cards = []
            for point in results:
                card = self._point_to_card(point)
                if card:
                    cards.append(card)
            
            return cards
            
        except Exception as e:
            print(f"Error getting cards by tag '{tag}': {e}")
            return []
    
    def delete_card(self, card_id: str) -> bool:
        """
        Delete a card by its ID.
        
        Args:
            card_id: UUID string of the card to delete
            
        Returns:
            True if successful, False otherwise
        """
        try:
            self.client.delete(
                collection_name=self.collection_name,
                points_selector=[card_id]
            )
            print(f"Deleted card: {card_id}")
            return True
            
        except Exception as e:
            print(f"Error deleting card {card_id}: {e}")
            return False
    
    def get_all_cards(self, limit: int = 100) -> List[ContextCard]:
        """
        Retrieve all cards (up to limit).
        
        Args:
            limit: Maximum number of cards to return
            
        Returns:
            List of ContextCard objects
        """
        try:
            results, _ = self.client.scroll(
                collection_name=self.collection_name,
                limit=limit,
                with_vectors=False
            )
            
            cards = []
            for point in results:
                card = self._point_to_card(point)
                if card:
                    cards.append(card)
            
            return cards
            
        except Exception as e:
            print(f"Error getting all cards: {e}")
            return []
    
    def _point_to_card(self, point) -> Optional[ContextCard]:
        """
        Helper method to convert a Qdrant point to a ContextCard.
        
        Properly deserializes all optional fields including logic_logs,
        system_state, vws_metadata, and decision_context.
        
        Args:
            point: Qdrant point object
            
        Returns:
            ContextCard object or None if conversion fails
        """
        try:
            return ContextCard(
                id=uuid.UUID(point.id),
                content=point.payload["content"],
                tags=point.payload.get("tags", []),
                source=point.payload.get("source", "manual"),
                importance=point.payload.get("importance", 5),
                created_at=datetime.fromisoformat(point.payload["created_at"]),
                embedding=point.vector if hasattr(point, 'vector') else None,
                logic_logs=point.payload.get("logic_logs"),
                system_state=point.payload.get("system_state"),
                vws_metadata=point.payload.get("vws_metadata"),
                decision_context=point.payload.get("decision_context", "")
            )
        except Exception as e:
            print(f"Error converting point to card: {e}")
            return None
