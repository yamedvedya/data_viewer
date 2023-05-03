from petra_viewer.data_sources.p1mscan.p1mscan_data_set import P1MScanDataSet

class DataPool:
    memory_mode = "ram"

if __name__ == "__main__":
    test = P1MScanDataSet(DataPool(), "/home/matveyev/temp_data/p1m/DUT134-DMF-ac-1ml-cap7-run1_03413_00000.cbf")



