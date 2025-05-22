from model.process import Process
from model.page import Page

from model.fifo import FIFO
from model.secondChance import SecondChance
from model.mru import MRU
from model.random import Random
from model.opt import OPT

import time
from collections import deque

class MMU:
    def __init__(self, algorithm):
        self.pages = [] # Reguero de paginas
        self.memory = deque() # memory (T)
        self.clock = 0
        self.time = 0 #hits + faults
        self.hits = 0
        self.faults = 0
        self.maxFrames = 100
        self.algorithm = algorithm
        self.next_ptr = 0 
        self.next_page_id = 0
        self.fragmentation = 0
    
    def set_algorithm(self):
        if self.algorithm == "FIFO":
            #self.algorithm = OPT()
            self.algorithm = FIFO()

        elif self.algorithm == "SC":
            self.algorithm = SecondChance()
        elif self.algorithm == "MRU":
            self.algorithm = MRU()
        elif self.algorithm == "RND": 
            self.algorithm = Random()
        
    def calc_fragmentation(self):
        fragmentation = 0
        for page in self.pages:
            if page.loaded and 0 < page.size_b < 4*1024:
                fragmentation += 4*1024 - page.size_b
        return fragmentation
    
    def calc_disk_usage(self):
        total_used_bytes = 0
        for page in self.pages:
            if not page.loaded:
                total_used_bytes += page.size_b 
        disk_used_kb = total_used_bytes / 1024
        return disk_used_kb

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
        used_frames = len(self.memory)
        available_frames = self.maxFrames - used_frames
        return available_frames >= size

    def create_pages(self, process: Process, size, add_to_memory=True):
        num_pages, remaining_bytes = self.byte_count(size)
        process_pages = []
        ptr = self.get_next_l_address()
        for i in range(num_pages):
            l_addr = ptr if i == 0 else self.get_next_l_address()
            page_id = self.get_next_page_id()
            page = Page(page_id, process.pid, l_addr, m_addr = l_addr, d_addr= '', loaded=False, loaded_t=self.clock)

            # size <= 4*1024
            if num_pages == 1:
                page.size_b = size
            # size > 4*1024 y hay un sobrante para la ultima pagina
            elif i == num_pages - 1 and remaining_bytes != 0:
                page.size_b = remaining_bytes
            # size > 4*1024 y no hay sobrante para la ultima pagina
            else:
                page.size_b = 4 * 1024

            if add_to_memory:
                self.pages.append(page)
            process_pages.append(page)

        process.new(ptr, process_pages)
        return ptr, process

    def update_memory(self):
        # Reflejar disco
        for page in self.pages:
            page.loaded = False
            page.loaded_t = ''
            page.M_Addr = ''
            page.D_Addr = self.pages.index(page)

        # Actualizar pages con memory
        for idx, page in enumerate(self.memory):
            page.M_Addr = idx
            for p in self.pages:
                if p.pageID == page.pageID:
                    p.loaded = True
                    p.loaded_t = self.clock
                    p.M_Addr = idx
                    p.D_Addr = ''
                    p.mark = page.mark
                    p.refBit = page.refBit
                    break

    def mark_page_loaded(self, page):
        for p in self.pages:
            if p.pageID == page.pageID:
                p.loaded = True
                p.loaded_t = self.clock
                p.M_Addr = self.memory.index(page)
                p.D_Addr = ''
                break

    def mark_page_unloaded(self, page):
        for p in self.pages:
            if p.pageID == page.pageID:
                p.loaded = False
                p.loaded_t = None
                p.M_Addr = None
                p.D_Addr = self.pages.index(p)
                break

    def get_process_by_ptr(self, ptr: int): 
        for page in self.pages:
            if page.L_Addr == ptr:
                return page.processID
        return None 
    




    def new(self, process: Process, size):
        process_ptr, process = self.create_pages(process, size)
        for page in process.symbolTable[process_ptr]:
            is_in_memory = page in self.memory
            if len(self.memory) < self.maxFrames and not is_in_memory:
                page.loaded = True
                page.loaded_t = self.clock
                self.memory.append(page)
                self.faults += 1
                self.time = self.hits + (self.faults * 5)

            else:
                #print(f"MMU: No hay suficiente memoria para el proceso {process.pid}, aplicando reemplazo")
                self.memory, self.hits, self.faults, _, removed = self.algorithm.replace(
                    pages=deque([page]), 
                    memory=self.memory, 
                    hits=self.hits, 
                    faults=self.faults, 
                    frameSize=self.maxFrames
                )

                self.time = self.hits + (self.faults*5)
                if removed:
                    self.mark_page_unloaded(removed)

                self.mark_page_loaded(page)
                self.update_memory()

        return process
    
    def use(self, process, ptr: int):
        if ptr not in process.symbolTable:
            print(f"[ERROR] Ptr -> {ptr} does not exists in PID={process.pid}")
            return
        for page in process.symbolTable[ptr]:
            self.memory, self.hits, self.faults, _, removed = self.algorithm.replace(
                pages=deque([page]), 
                memory=self.memory, 
                hits=self.hits, 
                faults=self.faults, 
                frameSize=self.maxFrames
            )

            self.time = self.hits + (self.faults*5)
            if removed:
                self.mark_page_unloaded(removed)

            self.mark_page_loaded(page)
            self.update_memory()

    def delete(self,process ,ptr: int):
        pages_to_remove = process.symbolTable.get(ptr, [])
        for page in pages_to_remove:
            self.pages.remove(page)
        process.delete(ptr)
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
