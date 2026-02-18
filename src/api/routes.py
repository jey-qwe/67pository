"""
API routes for Trinity Context Core memory operations.
"""
from fastapi import APIRouter, HTTPException, status
from typing import List

from ..memory.schemas import (
    ContextCard,
    CreateCardRequest,
    SearchRequest,
    SearchResponse
)
from ..memory.service import MemoryService

# Create API router
router = APIRouter(tags=["Memory"])

# Initialize memory service (singleton pattern)
memory_service = MemoryService()


@router.post(
    "/memory/add",
    response_model=ContextCard,
    status_code=status.HTTP_201_CREATED,
    summary="Add a new context card",
    description="Creates a new memory card with automatic embedding generation using Gemini"
)
async def add_memory_card(request: CreateCardRequest) -> ContextCard:
    """
    Add a new context card to memory.
    
    The content will be automatically converted to a vector embedding
    using Google Gemini API and stored in Qdrant for semantic search.
    
    Args:
        request: CreateCardRequest with content, tags, source, and importance
        
    Returns:
        The created ContextCard with generated ID and timestamp
        
    Raises:
        HTTPException: If embedding generation or storage fails
    """
    try:
        card = memory_service.add_card(
            content=request.content,
            tags=request.tags,
            source=request.source,
            importance=request.importance
        )
        
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to generate embedding or store card. Please check API key and Qdrant connection."
            )
        
        return card
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding memory card: {str(e)}"
        )


@router.post(
    "/memory/search",
    response_model=SearchResponse,
    summary="Search memory cards",
    description="Search for similar context cards using semantic similarity"
)
async def search_memory_cards(request: SearchRequest) -> SearchResponse:
    """
    Search for context cards using semantic similarity.
    
    Converts the query to a vector embedding and finds the most similar
    cards in the Qdrant database using cosine similarity.
    
    Args:
        request: SearchRequest with query text and limit
        
    Returns:
        SearchResponse with matching cards and total count
        
    Raises:
        HTTPException: If search fails
    """
    try:
        cards = memory_service.search(
            query=request.query,
            limit=request.limit
        )
        
        return SearchResponse(
            results=cards,
            total=len(cards)
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error searching memory cards: {str(e)}"
        )


@router.get(
    "/memory/card/{card_id}",
    response_model=ContextCard,
    summary="Get card by ID",
    description="Retrieve a specific context card by its UUID"
)
async def get_card(card_id: str) -> ContextCard:
    """
    Retrieve a specific card by its ID.
    
    Args:
        card_id: UUID string of the card
        
    Returns:
        The requested ContextCard
        
    Raises:
        HTTPException: If card not found
    """
    try:
        card = memory_service.get_card_by_id(card_id)
        
        if card is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID {card_id} not found"
            )
        
        return card
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving card: {str(e)}"
        )


@router.get(
    "/memory/tags/{tag}",
    response_model=List[ContextCard],
    summary="Get cards by tag",
    description="Retrieve all cards with a specific tag"
)
async def get_cards_by_tag(tag: str, limit: int = 50) -> List[ContextCard]:
    """
    Retrieve cards filtered by a specific tag.
    
    Args:
        tag: Tag to filter by
        limit: Maximum number of results (default: 50)
        
    Returns:
        List of matching ContextCard objects
    """
    try:
        cards = memory_service.get_cards_by_tag(tag, limit=limit)
        return cards
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cards by tag: {str(e)}"
        )


@router.get(
    "/memory/all",
    response_model=List[ContextCard],
    summary="Get all cards",
    description="Retrieve all context cards (up to limit)"
)
async def get_all_cards(limit: int = 100) -> List[ContextCard]:
    """
    Retrieve all cards.
    
    Args:
        limit: Maximum number of cards to return (default: 100)
        
    Returns:
        List of all ContextCard objects
    """
    try:
        cards = memory_service.get_all_cards(limit=limit)
        return cards
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving cards: {str(e)}"
        )


@router.delete(
    "/memory/card/{card_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete card",
    description="Delete a context card by its UUID"
)
async def delete_card(card_id: str):
    """
    Delete a card by its ID.
    
    Args:
        card_id: UUID string of the card to delete
        
    Raises:
        HTTPException: If deletion fails
    """
    try:
        success = memory_service.delete_card(card_id)
        
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Card with ID {card_id} not found or could not be deleted"
            )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting card: {str(e)}"
        )
