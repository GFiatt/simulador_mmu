from model.page import Page

class Process:
    def __init__(self, pid: int):
        self.pid = pid
        self.symbolTable = {}

    def new(self, ptr: int, pages):
        self.symbolTable[ptr] = pages


    def use(self, ptr: int):
        pass

    def delete(self, ptr: int):
        if ptr in self.symbolTable:
            print(f"Deleting pointer {ptr} from process {self.pid}")
            del self.symbolTable[ptr]
        else:
            print(f"Error: Pointer {ptr} not found in process {self.pid}")
        

    def kill(self):
        pass

    def __str__(self):
        return f"Process ID: {self.pid}, Symbol Table: {self.symbolTable}"
    
    def __repr__(self):
        return self.__str__()