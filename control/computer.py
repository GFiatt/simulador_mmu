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
        self.used_ram = 0
        self.disk_size = float('inf')
        self.disk = []
        self.page_size_kb = 4
        self.mmu = MMU(algorithm)

        if isinstance(self.mmu.algorithm, OPT):
            self.prepare_all_pages_for_opt()

    def prepare_all_pages_for_opt(self):
        if isinstance(self.mmu.algorithm, OPT):
            all_pages = []
            for instruction in self.session:
                if instruction.tipo == Type.NEW:
                    temp_process = Process(instruction.pid)
                    _, created_process = self.mmu.create_pages(temp_process, instruction.size, add_to_memory=False)

                    # Extraer las listas de páginas desde el symbolTable
                    for page_list in created_process.symbolTable.values():
                        all_pages.extend(page_list)

            self.mmu.algorithm.allPages = all_pages
            print(f"[OPT] Total páginas precargadas: {len(all_pages)}")



    def get_process_by_pid(self, pid):
        for process in self.process_table:
            if process.pid == pid:
                return process
        return None
    
    def get_process_count(self):
        return len(self.process_table)
    
    

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
    
                if process:
                    self.process_table.append(process)
                else:
                    process_disk = self.mmu.create_pages(Process(instruction.pid), instruction.size, add_to_memory=False)
                    self.process_table.append(process_disk)
                    print(f"No se pudo crear el proceso {pid} (sin memoria) \nAgregando pagina en  disco..." )

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


        #print("PROCESOS EN LA COMPU",self.process_table)
        print(f"[DEBUG] Algoritmo usado: {type(self.mmu.algorithm)}")
        print(f"[DEBUG] Páginas en MMU: {len(self.mmu.pages)}")
        print(f"[DEBUG] Tiene allPages? {'allPages' in dir(self.mmu.algorithm)}")
