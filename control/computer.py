class Computer:
    def __init__(self, process_table, session):
        self.process_table = process_table
        self.session = session
        self.cpu_cores = 1
        self.instructions_per_second = 1
        self.disk_access_time = 5
        self.ram_size_kb = 400
        self.disk_size = float('inf')
        self.page_size_kb = 4
