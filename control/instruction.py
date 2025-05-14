from enum import Enum

class Type(Enum):
    NEW = "new"
    USE = "use"
    DELETE = "delete"
    KILL = "kill"

class Instruction:
    def __init__(self, tipo: Type, pid: int, ptr: int = None, size: int = None):
        self.tipo = tipo
        self.pid = pid
        self.ptr = ptr
        self.size = size
