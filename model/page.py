class Page:
    def __init__(self, page_id: int, process_id: int, l_addr: int, m_addr: int, d_addr: int):
        self.pageID = page_id
        self.processID = process_id
        self.L_Addr = l_addr
        self.M_Addr = m_addr
        self.D_Addr = d_addr
        self.loaded = False
        self.loaded_t = 0
        self.size_b = 0
        self.mark = 0

    def __str__(self):
        return (f"Page(ID={self.pageID}, PID={self.processID}, "
                f"L_Addr={self.L_Addr}, M_Addr={self.M_Addr}, "
                f"D_Addr={self.D_Addr}, Size={self.size_b}, Loaded={self.loaded})")

    def __repr__(self):
        return self.__str__()
