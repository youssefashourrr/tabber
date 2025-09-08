from rapidfuzz.fuzz import ratio, partial_ratio
from typing import List, Tuple

from .window import Window
from ..utils.logger import get_logger, log_exception, SearchEngineError


def _calculate_score(window: Window, query: str) -> float:
    """Calculates a relevance score for a window based on the search query."""
    try:
        if not query.strip():
            return 0.0
            
        query_lower = query.lower().strip()
        title_lower = window.title.lower()
        process_lower = window.process_name.lower()
        
        title_score = ratio(query_lower, title_lower)
        process_score = partial_ratio(query_lower, process_lower)
        
        final_score = (title_score * 0.75) + (process_score * 0.25)
        
        if query_lower in title_lower:
            final_score = min(100.0, final_score + 10)
        elif query_lower in process_lower:
            final_score = min(100.0, final_score + 5)
        
        return final_score
    except Exception as e:
        logger = get_logger("search_engine")
        logger.error(f"Score calculation failed for window '{window.title}': {e}")
        return 0.0


def search_windows(windows: List[Window], query: str, min_score: float = 0.0) -> List[Window]:
    """Searches and ranks windows by relevance to the query string."""
    logger = get_logger("search_engine")
    
    if not query or not query.strip():
        logger.debug("Empty query, returning all windows")
        return windows
    
    if not windows:
        logger.debug("No windows to search")
        return []
    
    try:
        logger.info(f"Searching {len(windows)} windows: '{query}'")
        scored_windows: List[Tuple[Window, float]] = []
        
        for window in windows:
            try:
                score = _calculate_score(window, query)
                if score >= min_score:
                    scored_windows.append((window, score))
            except Exception as e:
                logger.error(f"Failed to score window {window.handle}: {e}")
                continue
        
        scored_windows.sort(key=lambda x: x[1], reverse=True)
        
        result = [window for window, score in scored_windows]
        logger.info(f"Found {len(result)} matches")
        return result
        
    except Exception as e:
        log_exception(logger, e, "window search")
        raise SearchEngineError("Failed to search windows") from e
