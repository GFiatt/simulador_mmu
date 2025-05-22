from collections import deque
import random
from page import Page

class rnd():
    @staticmethod
    def replace(pages, memory, hits=0, faults=0, frameSize=100):
        """
        Algoritmo Random: al fallar, reemplaza un marco elegido al azar.
        :param pages:  deque de páginas pendientes (se modifica in-place)
        :param memory: deque con las páginas cargadas
        :param frameSize: tamaño de la memoria
        :param hits: contador de hits
        :param faults: contador de faults
        :return: memory, hits, faults
        """
        removed = None

        current = pages.popleft()            # página referenciada ahora

        if current in memory:
            hits += 1
            return memory, hits, faults, pages, removed

        faults += 1
        if len(memory) < frameSize:          # aún hay hueco
            memory.append(current)
        else:                                # memoria llena → víctima aleatoria
            idx = random.randint(0, frameSize - 1)  # índice aleatorio
            removed = memory[idx]
            memory[idx] = current

        return memory, hits, faults, pages, removed
    
# -------- Quick test ----------
# Crear instancias de páginas para la prueba
p0 = Page(page_id=0, process_id=1, l_addr=0, m_addr=0, d_addr=0)
p1 = Page(page_id=1, process_id=1, l_addr=0, m_addr=0, d_addr=0)
p2 = Page(page_id=2, process_id=1, l_addr=0, m_addr=0, d_addr=0)
p3 = Page(page_id=3, process_id=2, l_addr=0, m_addr=0, d_addr=0)
p4 = Page(page_id=4, process_id=2, l_addr=0, m_addr=0, d_addr=0)
p5 = Page(page_id=5, process_id=2, l_addr=0, m_addr=0, d_addr=0)
p7 = Page(page_id=7, process_id=3, l_addr=0, m_addr=0, d_addr=0)

# Test Input
pages = deque([p7, p0, p1, p2, p0, p3, p0, p4, p2, p3, p0, p3, p2, p1])

memory = deque()    
hits = faults = 0
frameSize = 3  # To match the web example
stepPages = deque()

# Header
print(f"{'Step':<5} {'Incoming':<8} {'Memory':<15}   Hits  Faults")
print("-" * 40)

step = 1
while pages:
    # Obtener la página actual ANTES de procesarla
    current_page = pages[0]

    # Ejecutar el algoritmo FIFO
    memory, hits, faults, _, removed = rnd.replace(pages, memory, hits, faults, frameSize)
    
    # Mostrar resultados del paso actual
    mem_ids = [page.pageID for page in memory]
    print(f"{step:<5} [ {current_page.pageID} ]      {str(mem_ids):<15}   {hits:<4}  {faults}")
    step += 1

print("\nFinal summary:")
print("Page Faults = ", faults)
print("Hit = ", hits)
print("Final frame:", [page.pageID for page in memory])