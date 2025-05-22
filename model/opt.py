from collections import deque

class OPT():
    def __init__(self, allPages=[]): 
        self.allPages = allPages
        self.pointer = 0 

    def replace(self, pages, memory, hits=0, faults=0, frameSize=100):
        pages = list(pages)     
        memory = deque(memory)

        for current, p in enumerate(pages):
            # Verificar si la página ya está en memoria (comparando por ID)
            in_memory = any(p.pageID == m.pageID for m in memory)
            if in_memory:
                hits += 1
                continue

            # Página no está en memoria → fallo de página
            faults += 1

            # Hay espacio libre → no aplicar reemplazo
            if len(memory) < frameSize:
                memory.append(p)
                continue

            # No hay espacio libre → aplicar algoritmo OPT
            # Buscar próximos usos de cada página actual en memoria
            future_pages = self.allPages[self.pointer + 1:]  # desde la siguiente instrucción
            future_usage = {}

            for m_page in memory:
                try:
                    # Buscar la primera aparición futura de esta página
                    index = next(
                        i for i, future_p in enumerate(future_pages)
                        if future_p.pageID == m_page.pageID
                    )
                    future_usage[m_page.pageID] = index
                except StopIteration:
                    # No se volverá a usar
                    future_usage[m_page.pageID] = None

            # Elegir víctima: la página con uso más lejano o nunca usada
            victim_page_id = None
            max_future_index = -1

            for pid, idx in future_usage.items():
                if idx is None:
                    # Página abandonada
                    victim_page_id = pid
                    break
                elif idx > max_future_index:
                    max_future_index = idx
                    victim_page_id = pid

            # Buscar la instancia real de esa página en memoria
            victim = None
            for m_page in memory:
                if m_page.pageID == victim_page_id:
                    victim = m_page
                    break

            # Reemplazar víctima por la nueva página
            if victim:
                memory.remove(victim)
            memory.append(p)

            return memory, hits, faults, pages, victim

        return memory, hits, faults, pages, None
