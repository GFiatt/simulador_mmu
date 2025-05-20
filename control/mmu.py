from model.process import Process
from model.page import Page

class MMU:
    def __init__(self, algorithm):
        self.pages = []
        self.clock = 0
        self.faults = 0
        self.maxFrames = 100
        self.algorithm = algorithm
        self.next_ptr = 0 
        self.next_page_id = 0
        self.fragmentation = 0

    def calc_fragmentation(self):
        pass

    def get_next_l_address(self):
        ptr = self.next_ptr
        self.next_ptr += 1
        #self.next_ptr += 4 * 1024 
        return ptr
    
    def get_next_page_id(self):
        page_id = self.next_page_id
        self.next_page_id += 1
        return page_id

    def byte_count(self, size):
        if size <= 4*1024:
            return 1, 0
        else:
            return size//(4*1024), size%(4*1024)

    def enough_memory(self, size):
        return self.maxFrames >= size

    def new(self, process: Process, size):
        print(f"MMU: new {process.pid} {size} \n")
        num_pages, remaining_bytes = self.byte_count(size)
        process_pages = []
        ptr = self.get_next_l_address()
        if self.enough_memory(num_pages):
            for i in range(num_pages):
                l_addr = ptr if i == 0 else self.get_next_l_address()
                page_id = self.get_next_page_id()
                page = Page(page_id, process.pid, l_addr, None, None)

                # size <= 4*1024
                if num_pages == 1:
                    page.size_b = size
                # size > 4*1024 y hay un sobrante para la ultima pagina
                elif i == num_pages - 1 and remaining_bytes != 0:
                    page.size_b = remaining_bytes
                # size > 4*1024 y no hay sobrante para la ultima pagina
                else:
                    page.size_b = 4 * 1024

                self.pages.append(page)
                process_pages.append(page)

            process.new(ptr, process_pages)
            print(f"MMU pages: {self.pages} \n")
        else:
            print(f"MMU: No hay suficiente memoria para el proceso {process.pid}")
            return None
        return process

    def use(self, ptr: int):
        # Revisar las paginas fragmentadas
        print(f"MMU: use {ptr}")

    def get_process_by_ptr(self, ptr: int): 
        for page in self.pages:
            if page.L_Addr == ptr:
                return page.processID
        return None 

    def delete(self,process ,ptr: int):
        print(f"MMU: delete {ptr}")
        print(f"MMU CURRENT PROCESS PAGES: {process.symbolTable} \n")
        pages_to_remove = process.symbolTable.get(ptr, [])
        for page in pages_to_remove:
            self.pages.remove(page)
        process.delete(ptr)
        print(f"MMU NEW CURRENT PROCESS PAGES: {process.symbolTable} \n")
        print(f"MMU CURRENT PAGES: {self.pages} \n")
        return process
        
    def kill(self, pid: int):
        print(f"MMU: kill {pid}")
        print(f"MMU NEW CURRENT PAGES: {self.pages} \n")
        temp = self.pages.copy()
        for page in self.pages:
            if page.processID == pid:
                temp.remove(page)
        self.pages = temp
        print(f"MMU NEW CURRENT PAGES: {self.pages} \n")

    def __str__(self):
        return f"MMU: {self.pages}"
