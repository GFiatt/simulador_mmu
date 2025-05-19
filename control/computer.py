from control.instruction import Instruction, Type
from control.mmu import MMU
from model.opt import OPT
from model.process import Process

class Computer:
    def __init__(self, session, algorithm="FIFO"):
        self.process_table = []
        self.session = session
        self.cpu_cores = 1
        self.instructions_per_second = 1
        self.disk_access_time = 5
        self.ram_size_kb = 400
        self.disk_size = float('inf')
        self.page_size_kb = 4
        self.mmu = MMU(OPT)

    def get_process_by_pid(self, pid):
        for process in self.process_table:
            if process.pid == pid:
                return process
        return None

    def run(self):
        """
        Carga la sesión y ejecuta las instrucciones.
        """
        for instruction in self.session:
            if instruction.tipo == Type.NEW:
                process = self.get_process_by_pid(instruction.pid)

                # No existe el proceso
                if process is None:
                    process = self.mmu.new(Process(instruction.pid), instruction.size)

                # Existe el proceso
                else:
                    self.process_table.remove(process)
                    process = self.mmu.new(process, instruction.size)

                self.process_table.append(process)

            elif instruction.tipo == Type.USE:
                self.mmu.use(instruction)

            elif instruction.tipo == Type.DELETE:
                pid = self.mmu.get_process_by_ptr(instruction.ptr)
                process = self.get_process_by_pid(pid)
                if process is not None:
                    self.process_table.remove(process)
                    process = self.mmu.delete(process, instruction.ptr)
                    self.process_table.append(process)

            elif instruction.tipo == Type.KILL:
                self.mmu.kill(instruction.pid)
                process = self.get_process_by_pid(instruction.pid)
                if process is not None:
                    self.process_table.remove(process)
