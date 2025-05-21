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
        # Get the first page in the pages list
        current = pages.popleft()    
        
        # Check if the page is already in memory
        # If the page is already in memory, count as hit
        if current in memory:
            hits += 1
            return memory, hits, faults, pages, None

        # If the memory is not full, add the page
        faults += 1  # Count as fault
        if len(memory) == frameSize:
           removed =  memory.popleft()
        memory.append(current)
        return memory, hits, faults, pages, removed
    
    # -------- Quick test ----------

# #Test Input
# pages = deque([7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1])
# memory = deque()    
# hits = faults = 0
# frameSize = 3  # To match the web example
# stepPages = deque()

# # Max width to format the output
# INCOMING_W = len(str(pages))        # Larger list → max width
# MEMORY_W   = len(str([None]*frameSize)) 

# # Header
# print(f"{'Step':<5} {'Incoming pages':<{INCOMING_W}}   {'Memory':<{MEMORY_W}}   Hits  Faults")
# print('-' * (5 + INCOMING_W + MEMORY_W + 16))


# step = 1
# while pages:
#     incoming_str = str(list(pages))
#     memory, hits, faults, stepPages = FIFO.replace(pages, memory, hits, faults, frameSize)
#     incoming_str = str(list(pages))     
#     memory_str   = str(list(memory))    
#     print(f"{step:<5} {incoming_str:<{INCOMING_W}}   {memory_str:<{MEMORY_W}}   {hits:<4}  {faults}")
#     step += 1

# print("\nFinal summary:")
# print("Page Faults = ", faults)
# print("Hit = ", hits)
# print("Final frame:", list(memory))