class Page:
    def __init__(self, page_id: int, process_id: int, l_addr: int, m_addr: int, d_addr: int, 
                 loaded: bool = False, loaded_t: int = 0, size_b: int = 0, mark: int = 0):
        self.pageID = page_id
        self.processID = process_id
        self.L_Addr = l_addr
        self.M_Addr = m_addr
        self.D_Addr = d_addr
        self.loaded = loaded
        self.loaded_t = loaded_t
        self.size_b = size_b
        self.mark =  mark
    def __str__(self):
        return (f"Page(ID={self.pageID}, PID={self.processID}, "
                f"L_Addr={self.L_Addr}, M_Addr={self.M_Addr}, "
                f"D_Addr={self.D_Addr}, Size={self.size_b}, Loaded={self.loaded})")

    def __repr__(self):
        return self.__str__()
