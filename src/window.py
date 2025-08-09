class Window:
    def __init__(self, handle, title, process_id, process_name):
        self.handle = handle
        self.title = title
        self.process_id = process_id
        self.process_name = process_name

    def __repr__(self):
        return f"Window({self.handle}, {self.title}, {self.process_id}, {self.process_name})"