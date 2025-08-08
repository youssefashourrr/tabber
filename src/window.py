class Window:
    def __init__(self, handle, title, process_name, is_visible):
        self.handle = handle
        self.title = title
        self.process_name = process_name
        self.is_visible = is_visible

    def __repr__(self):
        return f"Window({self.handle}, {self.title}, {self.process_name}, {self.is_visible})"