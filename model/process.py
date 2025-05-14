class Process:
    def __init__(self, pid: int, mmu):
        self.pid = pid
        self.mmu = mmu
        self.symbolTable = {}

    def new(self, size: int):
        pass

    def use(self, ptr: int):
        pass

    def delete(self, ptr: int):
        pass

    def kill(self):
        pass
