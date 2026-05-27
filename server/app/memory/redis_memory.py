"""
Thin wrapper around Redis for storing per-session chat history.
Falls back gracefully if Redis is unavailable.
"""
import json
import logging
from typing import List, Dict

logger = logging.getLogger(__name__)

_redis_client = None


def _get_redis():
    global _redis_client
    if _redis_client is None:
        import redis
        from app.core.config import settings
        try:
            _redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
            _redis_client.ping()
        except Exception as e:
            logger.warning(f"Redis unavailable, memory disabled: {e}")
            _redis_client = None
    return _redis_client


def save_chat(session_id: str, messages: List[Dict]) -> None:
    r = _get_redis()
    if r:
        try:
            r.setex(session_id, 3600, json.dumps(messages))  # 1-hour TTL
        except Exception as e:
            logger.warning(f"Failed to save chat to Redis: {e}")


def get_chat(session_id: str) -> List[Dict]:
    r = _get_redis()
    if r:
        try:
            data = r.get(session_id)
            if data:
                return json.loads(data)
        except Exception as e:
            logger.warning(f"Failed to get chat from Redis: {e}")
    return []
