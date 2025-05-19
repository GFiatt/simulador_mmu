import tkinter as tk
from tkinter import ttk

class UI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Simulación MMU")
        self.root.configure(bg="white")

        self.setup_ram_display()
        self.setup_mmu_tables()
        self.setup_stats_panels()

    def setup_ram_display(self):
        tk.Label(self.root, text="RAM - OPT", bg="white").pack()
        self.canvas_opt = tk.Canvas(self.root, height=20, width=800, bg="white")
        self.canvas_opt.pack()

        tk.Label(self.root, text="RAM - [ALG]", bg="white").pack()
        self.canvas_alg = tk.Canvas(self.root, height=20, width=800, bg="white")
        self.canvas_alg.pack()

    def setup_mmu_tables(self):
        frame = tk.Frame(self.root, bg="white")
        frame.pack(pady=10)

        self.mmu_opt_frame = self.create_mmu_table(frame, "MMU - OPT")
        self.mmu_opt_frame.grid(row=0, column=0, padx=20)

        self.mmu_alg_frame = self.create_mmu_table(frame, "MMU - [ALG]")
        self.mmu_alg_frame.grid(row=0, column=1, padx=20)

    def create_mmu_table(self, parent, title):
        frame = tk.LabelFrame(parent, text=title, bg="white")
        tree = ttk.Treeview(frame, columns=("page_id", "pid", "loaded", "l_addr", "m_addr", "d_addr", "loaded_t", "mark"), show="headings", height=15)

        for col in tree["columns"]:
            tree.heading(col, text=col.upper())
            tree.column(col, width=80, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
        tree.configure(yscrollcommand=scrollbar.set)

        tree.grid(row=0, column=0)
        scrollbar.grid(row=0, column=1, sticky="ns")

        return tree

    def setup_stats_panels(self):
        container = tk.Frame(self.root, bg="white")
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

            # Color destacado para Thrashing (opcional)
            if text == "Thrashing":
                lbl.configure(fg="red", font=("Arial", 10, "bold"))

        return frame

    def insert_page_row(self, table, row_data: dict):
        """
        table: Treeview (self.mmu_opt_frame or self.mmu_alg_frame)
        row_data: dict con claves: page_id, pid, loaded, l_addr, m_addr, d_addr, loaded_t, mark
        """
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
