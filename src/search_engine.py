from rapidfuzz.fuzz import ratio, partial_ratio
from typing import List, Tuple

from window import Window


def _calculate_score(window: Window, query: str) -> float:
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


def search_windows(windows: List[Window], query: str, min_score: float = 0.0) -> List[Window]:
    if not query or not query.strip():
        return windows
    
    if not windows:
        return []
    
    try:
        scored_windows: List[Tuple[Window, float]] = []
        
        for window in windows:
            score = _calculate_score(window, query)
            scored_windows.append((window, score))
        
        scored_windows.sort(key=lambda x: x[1], reverse=True)
        
        return [window for window, score in scored_windows]
        
    except Exception as e:
        print(f"Error during window search: {e}")
        return []
