from collections import deque
import random
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
    
