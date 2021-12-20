from threading import Thread

from pymitter import EventEmitter

class EventListener(Thread): 
    def __init__(self, event : EventEmitter) -> None:
        Thread.__init__(self)
        self.daemon : bool = False 
        self.event : EventEmitter = event
        self.update_func = self.handle_ticker_update
        self.error_func = self.handle_error_message
        self.info_func = self.handle_info_message
        self.start()
        self.join()
        
    """
    Default event, does nothing
    any update on registered class code security
    and price change goes here
    """
    def handle_ticker_update(self, security_combo : str, price : str, update_timestamp : str) -> None:
        pass

    """
    Default event, does nothing
    any error associated with updating 
    specific class code security
    """
    def handle_error_message(self, error_type : str, error_message : str, error_timestamp : str) -> None:
        pass

    """
    Default event, does nothing
    gets any information messages
    """
    def handle_info_message(self, info_type : str, message : str, info_timestamp : str) -> None:
        pass

    def run(self):
        self.event.off("ticker-update", self.update_func)
        self.event.off("error", self.error_func)
        self.event.off("info", self.info_func)

        self.event.on("ticker-update", self.update_func)
        self.event.on("error", self.error_func)
        self.event.on("info", self.info_func)


    def set_event_listener(self, event_to_listen : str, cb_func):
        if event_to_listen == "ticker-update":      
            self.update_func = cb_func       
        elif event_to_listen == "error":       
            self.error_func = cb_func         
        elif event_to_listen == "info": 
            self.info_func = cb_func
        self.run()
