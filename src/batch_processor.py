"""
This serves as an example,
will save logs to a file
"""
import queue, threading

class FileBatchProcessor():
    def __init__(self):
        self.out = "outputs/demo_output.txt"
        self.queue = queue.Queue()
        self.log_items = []

    def write_data(self, text):
        f = open(self.out, "a")
        f.write(text)
        f.close()
    
    def worker(self):
        all_items = ""
        print("start batch save worker")
        while True:
            q_item = self.queue.get()
            for item in q_item:
                all_items += f"{item}\n"
            self.write_data(all_items)
            self.queue.task_done()
    
    def add_text_to_log(self, text_line):
        self.log_items.append(text_line)
        if len(self.log_items) < 4:
            self.queue.put(self.log_items)          
        else:
            self.log_items = []
            self.start_worker()

    def start_worker(self):
        threading.Thread(target=self.worker, daemon=True).start()
        self.queue.join()
        print("worker finished job")
    
