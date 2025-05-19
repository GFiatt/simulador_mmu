from enum import Enum

class Type(Enum):
    NEW = "new"
    USE = "use"
    DELETE = "delete"
    KILL = "kill"

class Instruction:
    def __init__(self, tipo: Type, pid=None, ptr=None, size=None):
        self.tipo = tipo
        self.pid = pid
        self.ptr = ptr
        self.size = size

    def __str__(self):
        return f"{self.tipo} - pid: {self.pid}, ptr: {self.ptr}, size: {self.size}"
