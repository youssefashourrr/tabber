class Window:
    """Represents a window with its handle, title, and process information."""

    def __init__(self, handle: int, title: str, process_id: int, process_name: str):
        self._handle = handle
        self._title = title
        self._process_id = process_id
        self._process_name = process_name

    @property
    def handle(self) -> int:
        """Returns the window handle."""
        return self._handle

    @property
    def title(self) -> str:
        """Returns the window title."""
        return self._title

    @property
    def process_id(self) -> int:
        """Returns the process ID that owns this window."""
        return self._process_id

    @property
    def process_name(self) -> str:
        """Returns the name of the process that owns this window."""
        return self._process_name

    def __repr__(self) -> str:
        return f"Window({self._handle}, {self._title}, {self._process_id}, {self._process_name})"
    
    def __str__(self) -> str:
        return f"{self._title} ({self._process_name})"