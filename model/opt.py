class OPT():

    def run(self, pages, memory, allPages, frameSize=100): # pages = [1, 2, 3, 4, 5] - en lista de espera a memoria
        fault = 0 
        hits = 0 
        for current, p in enumerate(pages):
            # La pagina esta en memoria
            if p in queue:
                continue
            
            # Fallo de página
            fault += 1
            
            # No se encuentra la pagina en memoria
            # Todavia hay espacio en memoria
            if len(queue) < frameSize:
                queue.append(p)
            # Ya no hay espacio en memoria
            elif len(queue) == frameSize:
                # Calcular uso futuro de cada página en memoria
                future = {}
                # Buscamos de la pagina actual en adelante
                futurePages = pages[current+1:]
                # Se agregan los indices de la siguiente aparacion de q 
                for q in queue:
                    try:
                        future[q] = futurePages.index(q)
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
                        
                queue.remove(victim)
                queue.append(p)
                
            print("Este es el queue: ", queue) #queue = [7]
            print("Este es el pages: ", pages) #pages = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2, 1]
            print(f"El fault es: {fault}")      #fault = 1
        pages = queue
        return fault, pages
                    
