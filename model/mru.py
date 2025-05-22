from collections import deque

class MRU():
    @staticmethod
    def replace(pages, memory, hits=0, faults=0, frameSize=100):
        # pages [p1, p2, p3,..., p1] 
        # current = p1 <- refBit = 1
        # memory [p1, p8, p7,...]
        """
        Algoritmo MRU (Most Recently Used).
        pages   : deque con las páginas restantes por atender (se modifica in-place).
        memory  : deque con las páginas en memoria.
        hits    : contador de aciertos.
        faults  : contador de fallos.
        frameSize: tamaño máximo de la memoria.
        """
        removed = None
        
        # Get the first page in the pages list
        current = pages.popleft()    
        
        # Check if the page is already in memory
        # If the page is already in memory, count as hit
        if current in memory:
            hits += 1
            memory.remove(current)  # Remove the page from its current position
            memory.append(current)  # Add it to the end of the queue
            return memory, hits, faults, pages, removed

        # If the memory is not full, add the page
        faults += 1  # Count as fault

        if len(memory) >= frameSize:
            # Memory is full, need to remove the most recently used page
            removed = memory.pop()
            memory.append(current)
        else:
            # Memory is not full, just add the new page
            memory.append(current)

        # Return the updated memory, hits, faults, pages, and removed page
        return memory, hits, faults, pages, removed
