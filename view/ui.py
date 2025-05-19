import tkinter as tk
from tkinter import ttk, filedialog
import random
import os
from control.instruction import Instruction, Type
import re
import tkinter.font as font


class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulación MMU")
        self.root.geometry("800x600")
        self.root.configure(bg="#C0C0C0")
        self.root.resizable(False, False)

        import tkinter.font as font
        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="MS Sans Serif", size=9)

        self.init_config_screen()



    # ----------- PRIMERA PANTALLA: ENTRADA DE DATOS -----------
    def init_config_screen(self):
        self.clear_window()
        self.root.geometry("800x600")
        self.root.configure(bg="#C0C0C0")

        self.config_frame = tk.Frame(self.root, bg="#C0C0C0", relief="ridge", borderwidth=2, padx=20, pady=20)
        self.config_frame.place(relx=0.5, rely=0.5, anchor="center")

        label_opts = {"bg": "#C0C0C0", "font": ("MS Sans Serif", 9)}
        entry_opts = {"font": ("MS Sans Serif", 9), "width": 30, "relief": "sunken", "bd": 2}

        tk.Label(self.config_frame, text="Datos para la Simulación", bg="#C0C0C0",
                font=("MS Sans Serif", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        tk.Label(self.config_frame, text="Semilla para random:", **label_opts).grid(row=1, column=0, sticky="e", padx=(0, 10), pady=5)
        self.seed_entry = tk.Entry(self.config_frame, **entry_opts)
        self.seed_entry.grid(row=1, column=1, sticky="w", pady=5)

        tk.Label(self.config_frame, text="Algoritmo a simular:", **label_opts).grid(row=2, column=0, sticky="e", padx=(0, 10), pady=5)
        self.algorithm_var = tk.StringVar()
        self.algorithm_dropdown = ttk.Combobox(self.config_frame, textvariable=self.algorithm_var, state="readonly", width=28)
        self.algorithm_dropdown['values'] = ("FIFO", "SC", "MRU", "RND")
        self.algorithm_dropdown.current(0)
        self.algorithm_dropdown.grid(row=2, column=1, sticky="w", pady=5)

        tk.Label(self.config_frame, text="Archivo de instrucciones (opcional):", **label_opts).grid(row=3, column=0, sticky="e", padx=(0, 10), pady=5)
        self.file_path = tk.StringVar()
        file_frame = tk.Frame(self.config_frame, bg="#C0C0C0")
        file_frame.grid(row=3, column=1, sticky="w", pady=5)
        tk.Entry(file_frame, textvariable=self.file_path, width=23, relief="sunken", bd=2).grid(row=0, column=0)
        tk.Button(file_frame, text="Seleccionar...", relief="raised", bd=2, command=self.select_file).grid(row=0, column=1, padx=(5, 0))

        tk.Label(self.config_frame, text="Número de procesos (P):", **label_opts).grid(row=4, column=0, sticky="e", padx=(0, 10), pady=5)
        self.processes_entry = tk.Entry(self.config_frame, **entry_opts)
        self.processes_entry.grid(row=4, column=1, sticky="w", pady=5)

        tk.Label(self.config_frame, text="Cantidad de operaciones (N):", **label_opts).grid(row=5, column=0, sticky="e", padx=(0, 10), pady=5)
        self.operations_entry = tk.Entry(self.config_frame, **entry_opts)
        self.operations_entry.grid(row=5, column=1, sticky="w", pady=5)

        tk.Button(self.config_frame, text="Iniciar Simulación", command=self.start_simulation,
                relief="raised", bd=2, font=("MS Sans Serif", 9)).grid(row=6, columnspan=2, pady=20)




    def select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if path:
            self.file_path.set(path)

    def clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    # ----------- SEGUNDA PANTALLA: SIMULACIÓN -----------
    def start_simulation(self):
        try:
            seed_str = self.seed_entry.get()
            algorithm = self.algorithm_var.get()
            file_path = self.file_path.get()
            p_str = self.processes_entry.get()
            n_str = self.operations_entry.get()

            if not seed_str.isdigit():
                raise ValueError("La semilla debe ser un número entero.")
            if not p_str.isdigit():
                raise ValueError("El número de procesos debe ser un entero.")
            if not n_str.isdigit():
                raise ValueError("La cantidad de operaciones debe ser un entero.")

            self.seed = int(seed_str)
            self.selected_algorithm = algorithm
            self.instructions_file = file_path if file_path else None
            self.num_processes = int(p_str)
            self.num_operations = int(n_str)

        except ValueError as ve:
            tk.messagebox.showerror("Error en los datos", str(ve))
            return

        self.clear_window()
        self.root.geometry("800x600")
        self.root.configure(bg="#C0C0C0")

        if self.instructions_file:
            if not self.load_instructions_from_file():
                return
        else:
            self.generate_instructions()

        self.setup_ram_display()
        self.setup_mmu_tables()
        self.setup_stats_panels()



    def load_instructions_from_file(self):
        try:
            with open(self.instructions_file, "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            if not lines:
                raise ValueError("El archivo no contiene instrucciones.")

            valid_lines = []
            for line in lines:
                if self.validate_instruction_format(line):
                    valid_lines.append(line)
                else:
                    raise ValueError(f"Formato inválido en línea:\n{line}")

            self.instructions = valid_lines
            print("Instrucciones cargadas desde archivo:")
            for inst in self.instructions:
                print(inst)

            self.parse_instructions()
            return True  # ✅ Éxito

        except Exception as e:
            tk.messagebox.showerror("Error al leer archivo", str(e))
            self.file_path.set("")
            self.instructions_file = None
            return False  # ✅ Error
    
    def validate_instruction_format(self, line: str) -> bool:
        line = line.strip().lower()
        patterns = [
            r"^new\(\d+,\d+\)$",          # new(pid, size)
            r"^use\(\d+\)$",              # use(ptr)
            r"^delete\(\d+\)$",           # delete(ptr)
            r"^kill\(\d+\)$"              # kill(pid)
        ]

        return any(re.fullmatch(p, line) for p in patterns)

    def generate_instructions(self):
        random.seed(self.seed)

        self.instructions = []
        symbol_tables = {pid: [] for pid in range(1, self.num_processes + 1)}
        kill_done = set()
        total_ops = 0

        while total_ops < self.num_operations:
            pid = random.randint(1, self.num_processes)

            if pid in kill_done:
                continue

            table = symbol_tables[pid]
            op = None

            if not table:
                op = f"new({pid},{random.randint(50, 1000)})"
                ptr_id = len(table) + 1
                table.append(ptr_id)
            else:
                op_type = random.choices(["use", "delete", "new", "kill"], weights=[40, 20, 30, 10])[0]
                if op_type == "new":
                    op = f"new({pid},{random.randint(50, 1000)})"
                    ptr_id = len(table) + 1
                    table.append(ptr_id)
                elif op_type == "use":
                    ptr = random.choice(table)
                    op = f"use({ptr})"
                elif op_type == "delete":
                    ptr = random.choice(table)
                    op = f"delete({ptr})"
                    table.remove(ptr)
                elif op_type == "kill":
                    op = f"kill({pid})"
                    kill_done.add(pid)
                    table.clear()

            self.instructions.append(op)
            total_ops += 1

        print("Instrucciones generadas automáticamente:")
        for inst in self.instructions:
            print(inst)
        self.save_generated_instructions_to_file()
        self.parse_instructions()

    def save_generated_instructions_to_file(self):
        try:
            output_dir = "generated_instructions"
            os.makedirs(output_dir, exist_ok=True)

            file_path = os.path.join(output_dir, f"instrucciones_seed_{self.seed}.txt")

            with open(file_path, "w") as f:
                for line in self.instructions:
                    f.write(line + "\n")

            tk.messagebox.showinfo("Archivo guardado", f"Instrucciones guardadas en:\n{file_path}")
        except Exception as e:
            tk.messagebox.showerror("Error al guardar archivo", str(e))
        
    def parse_instructions(self):
        self.instruction_objects = []

        for line in self.instructions:
            if line.startswith("new"):
                parts = line.strip("new()").split(",")
                pid = int(parts[0])
                size = int(parts[1])
                self.instruction_objects.append(Instruction(Type.NEW, pid=pid, size=size))

            elif line.startswith("use"):
                ptr = int(line.strip("use()"))
                self.instruction_objects.append(Instruction(Type.USE, pid=None, ptr=ptr))

            elif line.startswith("delete"):
                ptr = int(line.strip("delete()"))
                self.instruction_objects.append(Instruction(Type.DELETE, pid=None, ptr=ptr))

            elif line.startswith("kill"):
                pid = int(line.strip("kill()"))
                self.instruction_objects.append(Instruction(Type.KILL, pid=pid))
            
        self.setup_ram_display()
        self.setup_mmu_tables()
        self.setup_stats_panels()


    def setup_ram_display(self):
        label_style = {"bg": "#C0C0C0", "font": ("MS Sans Serif", 9)}
        
        tk.Label(self.root, text="RAM - OPT", **label_style).pack()
        self.canvas_opt = tk.Canvas(self.root, height=20, width=800, bg="white", relief="sunken", bd=2)
        self.canvas_opt.pack()

        tk.Label(self.root, text="RAM - [ALG]", **label_style).pack()
        self.canvas_alg = tk.Canvas(self.root, height=20, width=800, bg="white", relief="sunken", bd=2)
        self.canvas_alg.pack()


    def setup_mmu_tables(self):
        frame = tk.Frame(self.root, bg="#C0C0C0")
        frame.pack(pady=10)

        self.mmu_opt_frame = self.create_mmu_table(frame, "MMU - OPT")
        self.mmu_opt_frame.grid(row=0, column=0, padx=20)

        self.mmu_alg_frame = self.create_mmu_table(frame, "MMU - [ALG]")
        self.mmu_alg_frame.grid(row=0, column=1, padx=20)


    def create_mmu_table(self, parent, title):
        frame = tk.LabelFrame(parent, text=title, bg="#C0C0C0")
        tree = ttk.Treeview(frame, columns=("page_id", "pid", "loaded", "l_addr", "m_addr", "d_addr", "loaded_t", "mark"), show="headings", height=15)

        for col in tree["columns"]:
            tree.heading(col, text=col.upper())
            tree.column(col, width=80, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        return tree

    def setup_stats_panels(self):
        container = tk.Frame(self.root, bg="#C0C0C0")
        container.pack(pady=10)

        self.stats_opt = self.create_stats_table(container, "OPT")
        self.stats_opt.grid(row=0, column=0, padx=40)

        self.stats_alg = self.create_stats_table(container, "ALG")
        self.stats_alg.grid(row=0, column=1, padx=40)


    def create_stats_table(self, parent, label):
        frame = tk.LabelFrame(parent, text=f"Estadísticas - {label}", bg="white")

        rows = [
            ("Processes", "---"),
            ("Sim-Time", "---"),
            ("RAM KB", "---"),
            ("RAM %", "---"),
            ("V-RAM KB", "---"),
            ("V-RAM %", "---"),
            ("PAGES LOADED", "---"),
            ("PAGES UNLOADED", "---"),
            ("Thrashing", "---"),
            ("Fragmentación", "---")
        ]

        self.stats_vars = {}

        for i, (text, default) in enumerate(rows):
            tk.Label(frame, text=text, bg="white").grid(row=i, column=0, sticky="w")
            var = tk.StringVar(value=default)
            self.stats_vars[text] = var
            lbl = tk.Label(frame, textvariable=var, bg="white")
            lbl.grid(row=i, column=1, sticky="w")

            if text == "Thrashing":
                lbl.configure(fg="red", font=("Arial", 10, "bold"))

        return frame

    def insert_page_row(self, table, row_data: dict):
        values = (
            row_data["page_id"],
            row_data["pid"],
            "X" if row_data["loaded"] else "",
            row_data["l_addr"],
            row_data["m_addr"],
            row_data["d_addr"],
            f"{row_data['loaded_t']}s" if row_data["loaded_t"] else "",
            row_data["mark"]
        )
        table.insert("", "end", values=values)

    def run(self):
        self.root.mainloop()

    run()

    """
    def showRAM(self):
        pass

    def showMMU(self):
        pass

    def showProcesses(self):
        pass

    def showStatistics(self):
        pass
    """
