from rapidfuzz.fuzz import ratio, partial_ratio
from rapidfuzz import process

from window import Window
from window_manager import WindowManager


def _calculate_score(window: Window, query: str) -> float:
    title_score = ratio(query, window.title)
    process_score = partial_ratio(query, window.process_name)
    return (title_score + process_score) / 2


def search_windows(windows: list[Window], query: str) -> list[Window]:
    scored_windows = []
    for window in windows:
        score = _calculate_score(window, query)
        scored_windows.append((window, score))
    scored_windows.sort(key=lambda x: x[1], reverse=True)
    return [window for window, score in scored_windows]
