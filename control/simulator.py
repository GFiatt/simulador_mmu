
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
        self.computer.run()

    def pause(self):
        pass

    def resume(self):
        pass
