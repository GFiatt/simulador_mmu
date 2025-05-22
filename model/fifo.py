from collections import deque

class FIFO:
    def __init__(self): 
        pass
    
    @staticmethod
    def replace(pages, memory, hits=0, faults=0, frameSize=100):
        """
        Replace the first page in memory with the first page in the pages list. Also counts hits and faults.
        :param pages: Page List which is waiting to be loaded into memory.
        :param memory: Actual page list in memory.
        :param frameSize: Tamaño máximo de la memoria.
        :param hits: Hits counter.
        :param faults: Faults counter.
        :return: memory, hits, faults
        """
        removed = None
        
        # Get the first page in the pages list
        current = pages.popleft()    
        
        # Check if the page is already in memory
        # If the page is already in memory, count as hit
        if current in memory:
            hits += 1
            return memory, hits, faults, pages, removed

        # If the memory is not full, add the page
        faults += 1  # Count as fault
        if len(memory) == frameSize:
            removed = memory.popleft()
        memory.append(current)
        return memory, hits, faults, pages, removed
    
