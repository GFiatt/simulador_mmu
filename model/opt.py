from collections import deque
from page import Page

class OPT():
    def __init__(self, allPages=[]): 
        self.allPages = allPages
        self.pointer = 0 


    def replace(self, pages, memory, hits=0, faults=0, frameSize=100): # pages = [1, 2, 3, 4, 5] - en lista de espera a memoria

        pages = list(pages)     
        memory = deque(memory)

        for current, p in enumerate(pages):
            # La pagina esta en memoria
            if p in memory:
                hits += 1
                continue
            
            # Fallo de página
            faults += 1
            
            # No se encuentra la pagina en memoria
            # Todavia hay espacio en memoria
            if len(memory) < frameSize:
                memory.append(p)
            # Ya no hay espacio en memoria
            elif len(memory) == frameSize:
                # Calcular uso futuro de cada página en memoria
                future = {}
                # Buscamos de la pagina actual en adelante
                future_pages = self.allPages[self.pointer + 1:]
                # Se agregan los indices de la siguiente aparacion de q 
                for q in memory:
                    try:
                        future[q] = future_pages.index(q)
                    # En caso de que ya no se use mas
                    except Exception:
                        future[q] = None 
                
                # Averiguar la pagina abandonada o con uso mas lejano
                victim = None
                max_use = -1
                
                for futurePage, use in future.items():
                    # Página abandonada (no se usará más)
                    if use is None:
                        victim = futurePage
                        break
                    # Página con llamada tardia
                    if use > max_use:
                        max_use = use
                        victim = futurePage
                        
                memory.remove(victim)
                memory.append(p)
                return memory, hits, faults, pages, victim
        return memory, hits, faults, pages, None