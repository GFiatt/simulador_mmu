import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import os
import re
from control.instruction import Instruction, Type
from control.computer import Computer
import tkinter.font as font

colors = [
    "#ADD8E6", "#AFEEEE", "#B0E0E6", "#B0E57C", "#B2FF66", "#B3FFB3", "#B4F8C8", "#B5EAD7",
    "#B6FFFA", "#B9FBC0", "#BAF2E9", "#BBE2EC", "#BBFF99", "#BDFCC9", "#BEFFF7", "#C0FDFB",
    "#C1F0F6", "#C2F9BB", "#C3FDB8", "#C4FAF8", "#C5E384", "#C6FFDD", "#C7F9E5", "#C8E6C9",
    "#C9FFE5", "#CAEFD1", "#CBFF99", "#CCE5FF", "#CCFFCC", "#CCFFDD", "#CDFFEB", "#CEFFF9",
    "#CFFFE5", "#D0F0C0", "#D1FFBD", "#D2F5E3", "#D3FFCE", "#D4F1F4", "#D5FFD9", "#D6F5D6",
    "#D7F9F1", "#D8FCF8", "#D9FFFC", "#DAF7A6", "#DBFFEA", "#DCFFEF", "#DDFFCC", "#DEFFF2",
    "#DFFFFF", "#E0FFFF", "#E1FFB1", "#E2F0CB", "#E3F9E5", "#E4FFE1", "#E5FFCC", "#E6FFFA",
    "#E7FFDB", "#E8F6EF", "#E9FFE1", "#EAFFF4", "#EBFFFA", "#ECFFDC", "#EDFFF5", "#EEFFEB",
    "#EFFFE0", "#F0FFF0", "#F1FFEB", "#F2FFE8", "#F3F9D2", "#F4FFED", "#F5FFFA", "#F6FDC3",
    "#F7FFE2", "#F8FBAF", "#F9FFE5", "#FAFAD2", "#FBFFE2", "#FCF7BB", "#FDFFB6", "#FEF9E7",
    "#FFB6C1", "#FFC0CB", "#FFDAB9", "#FFE0B2", "#FFE4B5", "#FFE4E1", "#FFECB3", "#FFEFD5",
    "#FFF0F5", "#FFF5E1", "#FFF8DC", "#FFF9C4", "#FFFACD", "#FFFBCC", "#FFFCF5", "#FFFDFA",
    "#FFFEF0", "#FFFFCC", "#FFFFE0", "#FFFFF0", "#FFFFF5", "#FFFFF7"
]
  

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulación MMU")
        self.root.geometry("1280x800")
        self.root.configure(bg="#C0C0C0")
        self.root.resizable(True, True)

        default_font = font.nametofont("TkDefaultFont")
        default_font.configure(family="MS Sans Serif", size=9)

        self.instructions = []
        self.instruction_objects = []
        self.computer = None
        self.mmu = None

        self._init_config_screen()

    def _init_config_screen(self):
        self._clear_window()

        self.config_frame = tk.Frame(self.root, bg="#C0C0C0", relief="ridge", borderwidth=2, padx=20, pady=20)
        self.config_frame.place(relx=0.5, rely=0.5, anchor="center")

        tk.Label(self.config_frame, text="Datos para la Simulación", bg="#C0C0C0",
                 font=("MS Sans Serif", 12, "bold")).grid(row=0, column=0, columnspan=2, pady=(0, 15))

        self._add_labeled_entry("Semilla para random:", 1, "seed_entry")
        self._add_algorithm_dropdown("Algoritmo a simular:", 2)
        self._add_file_selector("Archivo de instrucciones (opcional):", 3)
        self._add_labeled_entry("Número de procesos (P):", 4, "processes_entry")
        self._add_labeled_entry("Cantidad de operaciones (N):", 5, "operations_entry")

        tk.Button(self.config_frame, text="Iniciar Simulación", command=self._start_simulation,
                  relief="raised", bd=2, font=("MS Sans Serif", 9)).grid(row=6, columnspan=2, pady=20)

    def _add_labeled_entry(self, label, row, attr_name):
        opts = {"bg": "#C0C0C0", "font": ("MS Sans Serif", 9)}
        tk.Label(self.config_frame, text=label, **opts).grid(row=row, column=0, sticky="e", padx=(0, 10), pady=5)
        entry = tk.Entry(self.config_frame, font=("MS Sans Serif", 9), width=30, relief="sunken", bd=2)
        entry.grid(row=row, column=1, sticky="w", pady=5)
        setattr(self, attr_name, entry)

    def _add_algorithm_dropdown(self, label, row):
        opts = {"bg": "#C0C0C0", "font": ("MS Sans Serif", 9)}
        tk.Label(self.config_frame, text=label, **opts).grid(row=row, column=0, sticky="e", padx=(0, 10), pady=5)
        self.algorithm_var = tk.StringVar()
        dropdown = ttk.Combobox(self.config_frame, textvariable=self.algorithm_var, state="readonly", width=28)
        dropdown['values'] = ("FIFO", "SC", "MRU", "RND")
        dropdown.current(0)
        dropdown.grid(row=row, column=1, sticky="w", pady=5)

    def _add_file_selector(self, label, row):
        opts = {"bg": "#C0C0C0", "font": ("MS Sans Serif", 9)}
        tk.Label(self.config_frame, text=label, **opts).grid(row=row, column=0, sticky="e", padx=(0, 10), pady=5)
        self.file_path = tk.StringVar()
        file_frame = tk.Frame(self.config_frame, bg="#C0C0C0")
        file_frame.grid(row=row, column=1, sticky="w", pady=5)
        tk.Entry(file_frame, textvariable=self.file_path, width=23, relief="sunken", bd=2).grid(row=0, column=0)
        tk.Button(file_frame, text="Seleccionar...", relief="raised", bd=2, command=self._select_file).grid(row=0, column=1, padx=(5, 0))

    def _select_file(self):
        path = filedialog.askopenfilename(filetypes=[("Archivos de texto", "*.txt"), ("Todos los archivos", "*.*")])
        if path:
            self.file_path.set(path)

    def _clear_window(self):
        for widget in self.root.winfo_children():
            widget.destroy()

    def _start_simulation(self):
        try:
            seed = self._validate_inputs()
            self.seed = seed
        except ValueError as ve:
            messagebox.showerror("Error en los datos", str(ve))
            return

        self._clear_window()

        if self.instructions_file:
            if not self._load_instructions_from_file():
                return
        else:
            self._generate_instructions()

        self.computer = Computer(session=self.instruction_objects, algorithm=self.selected_algorithm)
        self.computer.run()
        self.mmu = self.computer.mmu

        self._build_layout()

    def _validate_inputs(self):
        seed_str = self.seed_entry.get()
        algorithm = self.algorithm_var.get()
        file_path = self.file_path.get()
        p_str = self.processes_entry.get()
        n_str = self.operations_entry.get()

        if not seed_str.isdigit(): raise ValueError("La semilla debe ser un número entero.")
        if not p_str.isdigit(): raise ValueError("El número de procesos debe ser un entero.")
        if not n_str.isdigit(): raise ValueError("La cantidad de operaciones debe ser un entero.")

        self.selected_algorithm = algorithm
        self.instructions_file = file_path if file_path else None
        self.num_processes = int(p_str)
        self.num_operations = int(n_str)

        return int(seed_str)

    def _load_instructions_from_file(self):
        try:
            with open(self.instructions_file, "r") as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]

            if not lines: raise ValueError("El archivo no contiene instrucciones.")

            for line in lines:
                if not self._validate_instruction_format(line):
                    raise ValueError(f"Formato inválido en línea:\n{line}")

            self.instructions = lines
            print("Instrucciones cargadas desde archivo:")
            for inst in self.instructions:
                print(inst)

            self._parse_instructions()
            return True

        except Exception as e:
            messagebox.showerror("Error al leer archivo", str(e))
            self.file_path.set("")
            self.instructions_file = None
            return False

    def _validate_instruction_format(self, line):
        line = line.strip().lower()
        patterns = [
            r"^new\(\d+,\d+\)$",
            r"^use\(\d+\)$",
            r"^delete\(\d+\)$",
            r"^kill\(\d+\)$"
        ]
        return any(re.fullmatch(p, line) for p in patterns)

    def _generate_instructions(self):
        random.seed(self.seed)
        self.instructions = []
        symbol_tables = {pid: [] for pid in range(1, self.num_processes + 1)}
        kill_done = set()
        total_ops = 0

        while total_ops < self.num_operations:
            pid = random.randint(1, self.num_processes)
            if pid in kill_done: continue

            table = symbol_tables[pid]
            if not table:
                self.instructions.append(f"new({pid},{random.randint(50, 1000)})")
                table.append(len(table) + 1)
            else:
                op_type = random.choices(["use", "delete", "new", "kill"], weights=[40, 10, 35, 5])[0]
                if op_type == "new":
                    self.instructions.append(f"new({pid},{random.randint(50, 1000)})")
                    table.append(len(table) + 1)
                elif op_type == "use":
                    ptr = random.choice(table)
                    self.instructions.append(f"use({ptr})")
                elif op_type == "delete":
                    ptr = random.choice(table)
                    self.instructions.append(f"delete({ptr})")
                    table.remove(ptr)
                elif op_type == "kill":
                    self.instructions.append(f"kill({pid})")
                    kill_done.add(pid)
                    table.clear()

            total_ops += 1

        self._save_generated_instructions_to_file()
        self._parse_instructions()

    def _save_generated_instructions_to_file(self):
        try:
            os.makedirs("generated_instructions", exist_ok=True)
            path = os.path.join("generated_instructions", f"instrucciones_seed_{self.seed}.txt")
            with open(path, "w") as f:
                for line in self.instructions:
                    f.write(line + "\n")
            messagebox.showinfo("Archivo guardado", f"Instrucciones guardadas en:\n{path}")
        except Exception as e:
            messagebox.showerror("Error al guardar archivo", str(e))

    def _parse_instructions(self):
        self.instruction_objects = []
        for line in self.instructions:
            if line.startswith("new"):
                parts = line.strip("new()").split(",")
                self.instruction_objects.append(Instruction(Type.NEW, pid=int(parts[0]), size=int(parts[1])))
            elif line.startswith("use"):
                ptr = int(line.strip("use()"))
                self.instruction_objects.append(Instruction(Type.USE, pid=None, ptr=ptr))
            elif line.startswith("delete"):
                ptr = int(line.strip("delete()"))
                self.instruction_objects.append(Instruction(Type.DELETE, pid=None, ptr=ptr))
            elif line.startswith("kill"):
                pid = int(line.strip("kill()"))
                self.instruction_objects.append(Instruction(Type.KILL, pid=pid))

    def _build_layout(self):
        top_frame = tk.Frame(self.root, bg="#C0C0C0")
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="RAM - OPT", font=("MS Sans Serif", 9, "bold"), bg="#C0C0C0").pack()
        self.canvas_opt = tk.Canvas(top_frame, height=25, width=1200, bg="white", relief="sunken", bd=2)
        self.canvas_opt.pack()

        tk.Label(top_frame, text=f"RAM - [{self.selected_algorithm}]", font=("MS Sans Serif", 9, "bold"), bg="#C0C0C0").pack(pady=(10, 0))
        self.canvas_alg = tk.Canvas(top_frame, height=25, width=1200, bg="white", relief="sunken", bd=2)
        self.canvas_alg.pack()

        self._draw_ram_canvas(self.canvas_opt, [])
        self._draw_ram_canvas(self.canvas_alg, [])

        middle_frame = tk.Frame(self.root, bg="#C0C0C0")
        middle_frame.pack(pady=10, fill="x")
        self._create_table_with_scroll(middle_frame, "MMU - OPT").pack(side="left", padx=10)
        self._create_table_with_scroll(middle_frame, f"MMU - [{self.selected_algorithm}]").pack(side="right", padx=10)

        bottom_frame = tk.Frame(self.root, bg="#C0C0C0")
        bottom_frame.pack(pady=10, fill="x")
        self._create_statistics_block(bottom_frame, "OPT").pack(side="left", padx=40)
        self._create_statistics_block(bottom_frame, self.selected_algorithm).pack(side="right", padx=40)

    def _draw_ram_canvas(self, canvas, pages):
        canvas.delete("all")
        x = 5
        for i in range(60):
            canvas.create_rectangle(x, 5, x + 18, 20, fill="gray", outline="black")
            canvas.create_text(x + 9, 12, text="", font=("MS Sans Serif", 6))
            x += 20

    def _create_table_with_scroll(self, parent, title):
        frame = tk.LabelFrame(parent, text=title, bg="#C0C0C0")
        tree = ttk.Treeview(frame, columns=("PAGE ID", "PID", "LOADED", "L-ADDR", "M-ADDR", "D-ADDR", "LOADED-T", "MARK"), show="headings", height=15)
        for col in tree["columns"]:
            tree.heading(col, text=col)
            tree.column(col, width=80, anchor="center")
        for i, process in enumerate(self.computer.process_table):
            color = colors[i % len(colors)]
            tag_name = f"process_{process.pid}"
            tree.tag_configure(tag_name, background=color)

            for page_list in process.symbolTable.values():
                for page in page_list:
                    tree.insert(
                        "", "end",
                        values=(
                            page.pageID,
                            process.pid,
                            page.loaded,
                            page.L_Addr,
                            page.M_Addr,
                            page.D_Addr,
                            getattr(page, "loaded_t", ""),
                            getattr(page, "mark", ""),
                        ),
                        tags=(tag_name,)  # Esto aplica el color configurado
                    )

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)
        tree.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")
        return frame

    def _create_statistics_block(self, parent, label):
        container = tk.Frame(parent, bg="#C0C0C0")

        table1 = tk.Frame(container, bg="white", relief="solid", bd=1)
        for i, text in enumerate(["Processes", "Sim-Time"]):
            tk.Label(table1, text=text, bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=i)
            tk.Label(table1, text="", bg="white", borderwidth=1, relief="solid", width=20).grid(row=1, column=i)
        table1.pack(pady=2)

        table2 = tk.Frame(container, bg="white", relief="solid", bd=1)
        for i, text in enumerate(["RAM KB", "RAM %", "V-RAM KB", "V-RAM %"]):
            tk.Label(table2, text=text, bg="white", borderwidth=1, relief="solid", width=15).grid(row=0, column=i)
            tk.Label(table2, text="", bg="white", borderwidth=1, relief="solid", width=15).grid(row=1, column=i)
        table2.pack(pady=2)

        table3 = tk.Frame(container, bg="white", relief="solid", bd=1)
        tk.Label(table3, text="PAGES", bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=0, columnspan=2)
        tk.Label(table3, text="LOADED", bg="white", borderwidth=1, relief="solid", width=10).grid(row=1, column=0)
        tk.Label(table3, text="UNLOADED", bg="white", borderwidth=1, relief="solid", width=10).grid(row=1, column=1)
        tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=10).grid(row=2, column=0)
        tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=10).grid(row=2, column=1)
        tk.Label(table3, text="Thrashing", bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=2, columnspan=2)
        tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=10).grid(row=1, column=2)
        tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=10).grid(row=1, column=3)
        tk.Label(table3, text="Fragmentación", bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=4, rowspan=2)
        tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=20).grid(row=2, column=4)
        table3.pack(pady=2)

        #Adding info
        process_count = self.computer.get_process_count() if self.computer else 0
        tk.Label(table1, text=str(process_count), bg="white", borderwidth=1, relief="solid", width=20).grid(row=1, column=0)
        

        return container

    def run(self):
        self.root.mainloop()
