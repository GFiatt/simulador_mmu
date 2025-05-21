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
        fragmentation = 0
        for page in self.pages:
            if page.loaded and 0 < page.size_b < 4*1024:
                fragmentation += 4*1024 - page.size_b
        return fragmentation
    
    def count_loaded_pages(self):
        loaded_count = 0
        for page in self.pages:
            if page.loaded:
                loaded_count += 1
        return loaded_count

    def count_not_loaded_pages(self):
        not_loaded_count = 0
        for page in self.pages:
            if not page.loaded:
                not_loaded_count += 1
        return not_loaded_count

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
        full_pages = size // (4 * 1024)
        remainder = size % (4 * 1024)
        total_pages = full_pages + (1 if remainder > 0 else 0)
        return total_pages, remainder

    def get_ram_usage(self, total_ram_kb):
        total_used_bytes = 0

        for page in self.pages:
            if page.loaded:
                total_used_bytes += page.size_b 
        ram_used_kb = total_used_bytes / 1024
        # 
        if total_ram_kb > 0:
            ram_percentage = (ram_used_kb / total_ram_kb) * 100
        else:
            ram_percentage = 0

        return ram_used_kb, ram_percentage

    def enough_memory(self, size):
        used_frames = 0
        for page in self.pages:
            if page.loaded:
                used_frames += 1

        available_frames = self.maxFrames - used_frames
        return available_frames >= size

    def create_pages(self, process: Process, size, add_to_memory=True):
        num_pages, remaining_bytes = self.byte_count(size)
        process_pages = []
        ptr = self.get_next_l_address()
        for i in range(num_pages):
            l_addr = ptr if i == 0 else self.get_next_l_address()
            page_id = self.get_next_page_id()
            page = None
            if add_to_memory:
                page = Page(page_id, process.pid, l_addr, l_addr, l_addr, loaded=True, loaded_t=self.clock)
            else:
                page = Page(page_id, process.pid, l_addr, l_addr, l_addr, loaded=False, loaded_t=self.clock)

            # size <= 4*1024
            if num_pages == 1:
                page.size_b = size
            # size > 4*1024 y hay un sobrante para la ultima pagina
            elif i == num_pages - 1 and remaining_bytes != 0:
                page.size_b = remaining_bytes
            # size > 4*1024 y no hay sobrante para la ultima pagina
            else:
                page.size_b = 4 * 1024

            #if add_to_memory:
            self.pages.append(page)
            process_pages.append(page)

        process.new(ptr, process_pages)
        return process

    def new(self, process: Process, size):
        #print(f"MMU: new {process.pid} {size} \n")
        num_pages, remaining_bytes = self.byte_count(size)
        process_pages = []
        ptr = self.get_next_l_address()
        if self.enough_memory(num_pages):
            self.create_pages(process, size)
            #print(f"MMU pages: {self.pages} \n")
        else:
            print(f"MMU: No hay suficiente memoria para el proceso {process.pid}")
            return None
        return process

    def use(self, ptr: int):
        # Revisar las paginas fragmentadas
        #print(f"MMU: use {ptr}")
        pass

    def get_process_by_ptr(self, ptr: int): 
        for page in self.pages:
            if page.L_Addr == ptr:
                return page.processID
        return None 

    def delete(self,process ,ptr: int):
        #print(f"MMU: delete {ptr}")
        #print(f"MMU CURRENT PROCESS PAGES: {process.symbolTable} \n")
        pages_to_remove = process.symbolTable.get(ptr, [])
        for page in pages_to_remove:
            self.pages.remove(page)
        process.delete(ptr)
        #print(f"MMU NEW CURRENT PROCESS PAGES: {process.symbolTable} \n")
        #print(f"MMU CURRENT PAGES: {self.pages} \n")
        return process
        
    def kill(self, pid: int):
        #print(f"MMU: kill {pid}")
        #print(f"MMU NEW CURRENT PAGES: {self.pages} \n")
        temp = self.pages.copy()
        for page in self.pages:
            if page.processID == pid:
                temp.remove(page)
        self.pages = temp
        #print(f"MMU NEW CURRENT PAGES: {self.pages} \n")

    def __str__(self):
        return f"MMU: {self.pages}"
