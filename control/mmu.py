from model.page import Page

class MMU:
    def __init__(self, algorithm):
        self.pages = []
        self.clock = 0
        self.faults = 0
        self.maxFrames = 100
        self.algorithm = algorithm

    def new(self, pid: int, size: int) -> int:
        pass

    def use(self, ptr: int):
        pass

    def delete(self, ptr: int) -> bool:
        pass

    def kill(self, pid: int) -> bool:
        pass
