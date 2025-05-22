import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import random
import os
import re
import threading
from control.instruction import Instruction, Type
from control.computer import Computer
from model.opt import OPT
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
        self.computer_opt = None
        self.computer_alg = None

        self.simulation_index = 0
        self.simulation_delay = 100  # milisegundos
        self.simulation_running = True  

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

        self.computer_opt = Computer(session=self.instruction_objects, algorithm=OPT())
        self.computer_opt.prepare_all_pages_for_opt()
        self.computer_alg = Computer(session=self.instruction_objects, algorithm=self.selected_algorithm)
        self.computer_alg.mmu.set_algorithm()
        
        t1 = threading.Thread(target=self.computer_opt.run)
        t2 = threading.Thread(target=self.computer_alg.run)
        t1.start()
        t2.start()
        t1.join()
        t2.join()

        self._build_layout()
        self._update_statistics_threaded()
        self.simulation_index = 0
        self._run_next_instruction()

    def _update_statistics_threaded(self):
        t_opt = threading.Thread(target=self._update_statistics, args=(self.computer_opt,))
        t_alg = threading.Thread(target=self._update_statistics, args=(self.computer_alg,))
        t_opt.start()
        t_alg.start()
        t_opt.join()
        t_alg.join()
   
    def _run_next_instruction(self):
        if not self.simulation_running:
            self.root.after(self.simulation_delay, self._run_next_instruction)
            return

        if self.simulation_index < len(self.computer_alg.session):
            instruction = self.computer_alg.session[self.simulation_index]

            # Crear dos hilos para ejecutar la instrucción en ambas computadoras
            t1 = threading.Thread(target=self.computer_opt.run_single_instruction, args=(instruction,))
            t2 = threading.Thread(target=self.computer_alg.run_single_instruction, args=(instruction,))
            t1.start()
            t2.start()
            t1.join()
            t2.join()

            # Actualizar interfaz visual
            self._draw_ram_canvas(self.canvas_opt, self.computer_opt)
            self._draw_ram_canvas(self.canvas_alg, self.computer_alg)
            self._update_statistics_threaded()

            self.simulation_index += 1
            self.root.after(self.simulation_delay, self._run_next_instruction)

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
            # print("Instrucciones cargadas desde archivo:")
            # for inst in self.instructions:
            #     print(inst)

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
                op_type = random.choices(["use", "delete", "new", "kill"], weights=[54, 3, 40, 3])[0]
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
    # ---------- TOP ----------
        top_frame = tk.Frame(self.root, bg="#C0C0C0")
        top_frame.pack(pady=10)

        tk.Label(top_frame, text="RAM - OPT", font=("MS Sans Serif", 9, "bold"), bg="#C0C0C0").pack()
        self.canvas_opt = tk.Canvas(top_frame, height=40, width=2000, bg="white", relief="sunken", bd=2)
        self.canvas_opt.pack()

        tk.Label(top_frame, text=f"RAM - [{self.selected_algorithm}]", font=("MS Sans Serif", 9, "bold"), bg="#C0C0C0").pack(pady=(10, 0))
        self.canvas_alg = tk.Canvas(top_frame, height=50, width=2000, bg="white", relief="sunken", bd=2)
        self.canvas_alg.pack()

        self._draw_ram_canvas(self.canvas_opt, [])
        self._draw_ram_canvas(self.canvas_alg, [])

        # ---------- MIDDLE ----------
        self.middle_frame = tk.Frame(self.root, bg="#C0C0C0")
        self.middle_frame.pack(pady=10, fill="x")

        self.opt_table = self._create_table_with_scroll(self.middle_frame, "MMU - OPT")
        self.opt_table.pack(side="left", padx=10)

        self.table_frame = self._create_table_with_scroll(self.middle_frame, f"MMU - [{self.selected_algorithm}]")
        self.table_frame.pack(side="right", padx=10)

        # ---------- BOTTOM ----------
        self.bottom_frame = tk.Frame(self.root, bg="#C0C0C0")
        self.bottom_frame.pack(pady=10, fill="x")

        self.opt_statistics = self._create_statistics_block(self.bottom_frame, "OPT")
        self.opt_statistics.pack(side="left", padx=40)

        self.statistics_frame = self._create_statistics_block(self.bottom_frame, self.selected_algorithm)
        self.statistics_frame.pack(side="right", padx=40)

        # ---------- CONTROL ----------
        controls_frame = tk.Frame(self.root, bg="#C0C0C0")
        controls_frame.pack(pady=10)

        self.pause_button = tk.Button(controls_frame, text="Pausar", command=self._toggle_simulation, width=10)
        self.pause_button.pack(side="left", padx=10)

        reset_button = tk.Button(controls_frame, text="Reiniciar", command=self._reset_simulation, width=10)
        reset_button.pack(side="left", padx=10)

    def _toggle_simulation(self):
        self.simulation_running = not self.simulation_running
        new_text = "▶ Reanudar" if not self.simulation_running else "⏸ Pausar"
        self.pause_button.config(text=new_text)
  
    def _reset_simulation(self):
        self.simulation_running = True
        self._init_config_screen()

    def _draw_ram_canvas(self, canvas, computer):
        canvas.delete("all")

        total_blocks = 100
        blocks_per_row = 50
        box_width = 18
        box_height = 20
        spacing = 2
        start_x = 5
        start_y = 5

        # --- DIBUJAR CUADRITOS BASE (vacíos, grises) ---
        for i in range(total_blocks):
            row = i // blocks_per_row
            col = i % blocks_per_row
            x = start_x + col * (box_width + spacing)
            y = start_y + row * (box_height + spacing)

            canvas.create_rectangle(x, y, x + box_width, y + box_height, fill="gray", outline="black")
            canvas.create_text(x + box_width // 2, y + box_height // 2, text="", font=("MS Sans Serif", 6))

        # --- DIBUJAR PÁGINAS CARGADAS ---
        pages_in_ram = []

        for i, process in enumerate(computer.process_table):
            color = colors[i % len(colors)]
            for page_list in process.symbolTable.values():
                for page in page_list:
                    if page.loaded:
                        pages_in_ram.append((page, color))

        for i, (page, color) in enumerate(pages_in_ram[:100]):
            row = i // blocks_per_row
            col = i % blocks_per_row
            x = start_x + col * (box_width + spacing)
            y = start_y + row * (box_height + spacing)

            canvas.create_rectangle(x, y, x + box_width, y + box_height, fill=color, outline="black")
            canvas.create_text(x + box_width // 2, y + box_height // 2, text=str(page.pageID), font=("MS Sans Serif", 6))

    def _create_table_with_scroll(self, parent, title, computer):
        frame = tk.LabelFrame(parent, text=title, bg="#C0C0C0")
        
        self.treeview = ttk.Treeview(
            frame,
            columns=("PAGE ID", "PID", "LOADED", "L-ADDR", "M-ADDR", "D-ADDR", "LOADED-T", "MARK"),
            show="headings",
            height=15
        )

        for col in self.treeview["columns"]:
            self.treeview.heading(col, text=col)
            self.treeview.column(col, width=80, anchor="center")

        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=self.treeview.yview)
        self.treeview.configure(yscrollcommand=scrollbar.set)
        self.treeview.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        return frame

    def _create_statistics_block(self, parent, label):
        container = tk.Frame(parent, bg="#C0C0C0")

        # -------- TABLE 1: Processes & Sim-Time --------
        table1 = tk.Frame(container, bg="white", relief="solid", bd=1)
        for i, text in enumerate(["Processes", "Sim-Time"]):
            tk.Label(table1, text=text, bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=i)

        self.process_count_label = tk.Label(table1, text="0", bg="white", borderwidth=1, relief="solid", width=20)
        self.process_count_label.grid(row=1, column=0)

        sim_time_label = tk.Label(table1, text="0", bg="white", borderwidth=1, relief="solid", width=20)
        sim_time_label.grid(row=1, column=1)

        if label == "OPT":
            self.sim_time_label_opt = sim_time_label
        else:
            self.sim_time_label_alg = sim_time_label



        table1.pack(pady=2)

        # -------- TABLE 2: RAM & V-RAM --------
        table2 = tk.Frame(container, bg="white", relief="solid", bd=1)
        for i, text in enumerate(["RAM KB", "RAM %", "V-RAM KB", "V-RAM %"]):
            tk.Label(table2, text=text, bg="white", borderwidth=1, relief="solid", width=15).grid(row=0, column=i)

        self.ram_kb_label = tk.Label(table2, text="0", bg="white", borderwidth=1, relief="solid", width=15)
        self.ram_kb_label.grid(row=1, column=0)

        self.ram_percent_label = tk.Label(table2, text="0%", bg="white", borderwidth=1, relief="solid", width=15)
        self.ram_percent_label.grid(row=1, column=1)

        self.vram_kb_label = tk.Label(table2, text="0", bg="white", borderwidth=1, relief="solid", width=15)
        self.vram_kb_label.grid(row=1, column=2)

        self.vram_percent_label = tk.Label(table2, text="0%", bg="white", borderwidth=1, relief="solid", width=15)
        self.vram_percent_label.grid(row=1, column=3)

        table2.pack(pady=2)

        # -------- TABLE 3: Pages & Fragmentation --------
        table3 = tk.Frame(container, bg="white", relief="solid", bd=1)

        tk.Label(table3, text="PAGES", bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=0, columnspan=2)
        tk.Label(table3, text="LOADED", bg="white", borderwidth=1, relief="solid", width=10).grid(row=1, column=0)
        tk.Label(table3, text="UNLOADED", bg="white", borderwidth=1, relief="solid", width=10).grid(row=1, column=1)

        self.loaded_pages_label = tk.Label(table3, text="0", bg="white", borderwidth=1, relief="solid", width=10)
        self.loaded_pages_label.grid(row=2, column=0)

        self.unloaded_pages_label = tk.Label(table3, text="0", bg="white", borderwidth=1, relief="solid", width=10)
        self.unloaded_pages_label.grid(row=2, column=1)

        tk.Label(table3, text="Thrashing", bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=2, columnspan=2)
        self.thrashing_label_1 = tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=10)
        self.thrashing_label_1.grid(row=1, column=2)
        self.thrashing_label_2 = tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=10)
        self.thrashing_label_2.grid(row=1, column=3)

        tk.Label(table3, text="Fragmentación", bg="white", borderwidth=1, relief="solid", width=20).grid(row=0, column=4, rowspan=2)
        self.fragmentation_label = tk.Label(table3, text="", bg="white", borderwidth=1, relief="solid", width=20)
        self.fragmentation_label.grid(row=2, column=4)

        table3.pack(pady=2)

        return container

    def _update_statistics(self, computer):
        #print(f"[DEBUG] update_statistics() called | sim_time={self.computer.mmu.time}, faults={self.computer.mmu.faults}")

        self._draw_ram_canvas(self.canvas_alg, [])

        # Procesos
        self.process_count_label.config(text=str(computer.get_process_count()))
        
        # Sim-time 
        sim_time = computer.mmu.time
        sim_time_text = f"{sim_time} s"
        self.sim_time_label_alg.config(text=sim_time_text)

       # Thrashing
        faults = computer.mmu.faults
        thrashing_percentage = (faults / sim_time) * 100 if sim_time > 0 else 0

        text1 = f"{faults} s"
        text2 = f"{thrashing_percentage:.2f} %"

        bg_color = "red" if thrashing_percentage > 50 else "white"
        self.thrashing_label_1.config(text=text1, bg=bg_color)
        self.thrashing_label_2.config(text=text2, bg=bg_color)

        # Fragmentación
        fragmentation_count = (computer.mmu.calc_fragmentation())/ 1024
        total_ram_bytes = 400 
        fragmentation_percentage = (fragmentation_count / total_ram_bytes) * 100 if total_ram_bytes else 0
        text = f"{fragmentation_count:.1f} KB ({fragmentation_percentage:.1f}%)"
        bg_color = "red" if fragmentation_count > total_ram_bytes / 2 else "white"
        self.fragmentation_label.config(text=text, bg=bg_color)

        # RAM
        ram_kb, ram_percent = computer.mmu.get_ram_usage(self.computer.ram_size_kb)
        self.ram_kb_label.config(text=f"{ram_kb:.1f} KB")
        self.ram_percent_label.config(text=f"{ram_percent:.1f} %")

        # VRAM 
        disk_usage = computer.mmu.calc_disk_usage()
        disk_percentage = (disk_usage / total_ram_bytes) * 100 if total_ram_bytes else 0
        self.vram_kb_label.config(text=f"{disk_usage:.1f} KB")
        self.vram_percent_label.config(text=f"{disk_percentage:.1f} %")

        # Páginas
        loaded_pages = computer.mmu.count_loaded_pages()
        not_loaded_pages = computer.mmu.count_not_loaded_pages()
        self.loaded_pages_label.config(text=str(loaded_pages))
        self.unloaded_pages_label.config(text=str(not_loaded_pages))

        if hasattr(self, "treeview"):
            self.treeview.delete(*self.treeview.get_children())  # Vaciar

            for i, process in enumerate(computer.process_table):
                color = colors[i % len(colors)]
                tag_name = f"process_{process.pid}"
                self.treeview.tag_configure(tag_name, background=color)

                for page_list in process.symbolTable.values():
                    for page in page_list:
                        self.treeview.insert(
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
                            tags=(tag_name,)
                        )

    def run(self):
        self.root.mainloop()
