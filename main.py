from control.instruction import Instruction, Type
from control.computer import Computer

# if __name__ == "__main__":
#     app = UI()
#     app.run()

instructions = [Instruction(Type.NEW, 1, None, 250), 
                Instruction(Type.NEW, 1, None, 250),
                Instruction(Type.NEW, 2, None, 500),
                Instruction(Type.DELETE, None, 4096, None),
                Instruction(Type.KILL, 1, None, None)]
computer = Computer(instructions)

computer.run()
