from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, validator
from typing import Optional
from database.interactions import DBInteractions
import logging
import re

router = APIRouter()
logger = logging.getLogger(__name__)

class InteractionEvent(BaseModel):
    user_id: str
    event_type: str
    product_id: Optional[str] = None
    query: Optional[str] = None

    @validator('user_id')
    def validate_user_id(cls, v):
        if not re.match(r'^[a-zA-Z0-9]{1,50}$', v):
            raise ValueError('Invalid user_id format')
        return v

    @validator('event_type')
    def validate_event_type(cls, v):
        valid_types = ['product_click', 'search_query']
        if v not in valid_types:
            raise ValueError(f'Invalid event type. Must be one of {valid_types}')
        return v

    @validator('product_id', always=True)
    def validate_product_id(cls, v, values):
        if values.get('event_type') == 'product_click':
            if not v or not (len(v) == 10 and v.isalnum() and v.isupper()):
                raise ValueError('Product ID must be 10 uppercase alphanumeric characters for product_click events')
        return v

    @validator('query', always=True)
    def validate_query(cls, v, values):
        if values.get('event_type') == 'search_query':
            if not v or not v.strip():
                raise ValueError('Query cannot be empty for search_query events')
        return v.strip() if v else v

@router.post("/interactions", status_code=status.HTTP_204_NO_CONTENT)
async def log_interaction(event: InteractionEvent):
    """
    Log a user interaction event.
    
    This endpoint creates a user-specific interaction table (if not exists) 
    and logs the interaction event.
    """
    try:
        # Use the DBInteractions class method to log the interaction
        await DBInteractions.log_interaction(
            user_id='u'+event.user_id,
            event_type=event.event_type,
            product_id=event.product_id,
            query_text=event.query
        )

    except Exception as e:
        logger.error(f"Error logging interaction: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to log interaction"
        )

@router.get("/interactions/{user_id}")
async def get_user_interactions(user_id: str, days: int = 30):
    """
    Retrieve user interactions for the past specified number of days.
    
    :param user_id: The user's unique identifier
    :param days: Number of days to retrieve interactions for (default 30)
    :return: List of user interactions
    """
    try:
        # Validate user_id format
        if not re.match(r'^[a-zA-Z0-9]{1,50}$', 'u'+user_id):
            raise ValueError('Invalid user_id format')

        # Fetch user interactions using DBInteractions class method
        interactions = await DBInteractions.fetch_user_interactions('u'+user_id, days)
        
        # Convert asyncpg.Record to dict for JSON serialization
        return [dict(interaction) for interaction in interactions]
    
    except ValueError as ve:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail=str(ve)
        )
    except Exception as e:
        logger.error(f"Error fetching user interactions: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve user interactions"
        )