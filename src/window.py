class Window:

    def __init__(self, handle: int, title: str, process_id: int, process_name: str):
        self._handle = handle
        self._title = title
        self._process_id = process_id
        self._process_name = process_name

    @property
    def handle(self) -> int:
        return self._handle

    @property
    def title(self) -> str:
        return self._title

    @property
    def process_id(self) -> int:
        return self._process_id

    @property
    def process_name(self) -> str:
        return self._process_name

    def __repr__(self) -> str:
        return f"Window({self._handle}, {self._title}, {self._process_id}, {self._process_name})"
    
    def __str__(self) -> str:
        return f"{self._title} ({self._process_name})"