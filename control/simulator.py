
class Simulator:
    def __init__(self, computer, alg1, alg2, ui, mmu):
        self.computer = computer
        self.reloj = 0
        self.thrashing = 0
        self.alg1 = alg1
        self.alg2 = alg2
        self.ui = ui
        self.mmu = mmu

    def run(self):
        # Asuminos que las instrucciones han sido procesadas y cargadas
        # new(1, 250) //suponga que devuelve el ptr 1
        # new(1, 50) //suponga que devuelve el ptr 2
        # new(2, 5320) //suponga que devuelve el ptr 3
        # new(3, 345) //suponga que devuelve el ptr 4
        # use(1)
        # use(3)
        # use(2)
        # use(1)
        # delete(1) //a partir de este punto ya no se puede volver a usar el
        # ptr 1
        # kill(1) // ya no se pueden volver a usar los punteros 1 y 2, a partir
        # de este punto no puede hacerse new(1,x)
        # kill(2)
        # kill(3)

        self.mmu.new(1, 250)


        self.mmu.new(1, 50)
        self.mmu.new(2, 5320)
        self.mmu.new(3, 345)
        self.mmu.use(1)
        self.mmu.use(3)
        self.mmu.use(2) # 1
        self.mmu.use(1)
        self.mmu.delete(1)
        self.mmu.kill(1)
        self.mmu.kill(2)
        self.mmu.kill(3)
        pass

    def pause(self):
        pass

    def resume(self):
        pass
