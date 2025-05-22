from collections import deque

class SecondChance():
    @staticmethod
    def replace(pages, memory, hits=0, faults=0, frameSize=100):
        """
        Algoritmo Second-Chance (Clock).
        pages   : deque con las páginas restantes por atender (se modifica in-place).
        memory  : deque con las páginas en memoria.
        refs    : deque paralela con bits R (0/1) de cada marco.
        pointer : índice circular que apunta al candidato a reemplazo.
        """
        removed = None
        
        # Get the first page in the pages list
        current = pages.popleft()    
        
        # Check if the page is already in memory
        # If the page is already in memory, count as hit
        if current in memory:
            hits += 1
            current.refBit = 1
            return memory, hits, faults, pages, removed

        # If the memory is not full, add the page
        faults += 1  # Count as fault

        if len(memory) >= frameSize:
            iteraciones = 0
            removed = None
            while iteraciones < len(memory):
                candidate = memory.popleft()
                # Check if the candidate page has a reference bit set to 1
                if candidate.refBit == 1:
                    # Set the reference bit to 0 and move to the end of the queue
                    candidate.refBit = 0
                    memory.append(candidate)
                    iteraciones += 1
                else:
                    # This page will be removed
                    removed = candidate
                    break
            if removed is None:
                # If we have cycled through all pages and none were removed, we can add the new page
                removed = memory.popleft()
            # Add the new page to memory
            memory.append(current)
        else:
            # Memory is not full, just add the new page
            memory.append(current)
        
        # Mark as newly referenced
        current.refBit = 1

        # Return the updated memory, hits, faults, pages, and removed page
        return memory, hits, faults, pages, removed