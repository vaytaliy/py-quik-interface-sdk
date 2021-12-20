import zmq
import time
from threading import Thread
from pymitter import EventEmitter
import src.errors as errors
from datetime import datetime

from qlua.rpc import RPC_pb2, datasource
from zmq.sugar.context import Context

from src.event_listener import EventListener

"""
Maps interval indexes from .proto file to amount of milliseconds,
very large intervals aren't included
"""
INTERVAL_DURATION = {
    1: 100,             #INTERVAL_TICK
    2: 1000 * 60,        #INTERVAL_M1
    3: 1000 * 60 * 2,    #INTERVAL_M2
    4: 1000 * 60 * 3,    #INTERVAL_M3
    5: 1000 * 60 * 4,    #INTERVAL_M4
    6: 1000 * 60 * 5,    #INTERVAL_M5
    7: 1000 * 60 * 6,    #INTERVAL_M6
    8: 1000 * 60 * 10,   #INTERVAL_M10
    9: 1000 * 60 * 15   #INTERVAL_M15
}

class Security:
    
    callback_uuid = None

    def __init__(self, class_code, security_code):
        self.class_code = class_code
        self.security_code = security_code
        self.class_code_security_combo = f'{class_code}{security_code}'

class QuikInterface(Thread):
    ctx : Context = None
    socket = None

    def __init__(self, url, user, password, encoding, update_interval, is_daemon = False) -> None:
        Thread.__init__(self)
        self.event_listener = EventListener(EventEmitter())
        self.daemon: bool = is_daemon
        self.prevent_updates : bool = False
        self.update_interval: int = update_interval
        self.url: str = url
        self.user: str = user   
        self.password: str = password
        self.encoding: str = encoding
        self.existing_data_objects : dict[str, Security] = {} 
        self.create_connection()
        self.start()


    def create_connection(self):
        try:
            self.ctx = zmq.Context.instance()
            self.socket = self.ctx.socket(zmq.REQ)  
            self.socket.setsockopt(zmq.RCVTIMEO, 5000) 
            self.socket.plain_username = self.user.encode(self.encoding)
            self.socket.plain_password = self.password.encode(self.encoding)

            self.socket.connect(self.url)
            self.event_listener.event.emit("info", "general", f"Successfully stablished connection to QUIK terminal", self.get_timestamp_now())
        except Exception as e:
            self.event_listener.event.emit("error", errors.ERR_QUIK_CONNECTION, f"Error connecting to QUIK terminal {str(e)}", self.get_timestamp_now())

    """
    Creates new datasource if such is not found in existing datasources dictionary
    Datasource UUID is then sent to create callback for receiving data updates

    Update interval timer is how often the QUIK will send updates from
    its side if there are no error responses

    returns tuple (status: 'ok' | 'error', content: [str datasource_uuid] | [str <error description])
    """

    def create_new_data_source(self, data_object : Security):
        self.event_listener.event.emit("info", "general", f"Attempting to create new data source for {data_object.class_code} class code and {data_object.security_code} security code..", self.get_timestamp_now())
        args = datasource.CreateDataSource_pb2.Args(
            class_code = data_object.class_code,
            sec_code = data_object.security_code,
            interval = self.update_interval
        )

        req = RPC_pb2.Request(
            type = RPC_pb2.CREATE_DATA_SOURCE,
            args = args.SerializeToString()
        )

        data = req.SerializeToString()
        try:          
            self.socket.send(data)

            resp = RPC_pb2.Response()     
            resp.ParseFromString(self.socket.recv())   
            
            msg = datasource.CreateDataSource_pb2.Result()
            msg.ParseFromString(resp.result)

            if msg.error_desc != '':
                self.event_listener.event.emit("error", errors.ERR_DATASOURCE_REGISTRATION, f"Error creating data source listener: {msg.error_desc}", self.get_timestamp_now())
                return

            if msg.datasource_uuid != '' and msg.datasource_uuid is not None:
                
                data_object.callback_uuid = msg.datasource_uuid
                data_object.stop_update_flag = False

                self.set_empty_callback_for_source(data_object)
                self.existing_data_objects[data_object.class_code_security_combo] = data_object
                
            else:
                self.event_listener.event.emit("error", errors.ERR_DATASOURCE_REGISTRATION, f"DataSource couldn't be created, try restarting QUIK. Datasource uuid was empty")
            self.event_listener.event.emit("info", "general", f"Successfully established datasource exchange for {data_object.class_code_security_combo}", self.get_timestamp_now())
        except:       
            self.event_listener.event.emit("error", errors.ERR_DATASOURCE_REGISTRATION, f"Failed fetching info on {data_object.class_code_security_combo}.Unable to interface with QUIK terminal.. Check if QUIK is open and retry to run script", self.get_timestamp_now())

    """
    Gets candle size, takes max element
    """

    def get_candle_size(self, classcode_security_combo):
        
        dtsrc = self.existing_data_objects.get(classcode_security_combo)

        if dtsrc is None:
            return

        args = datasource.Size_pb2.Args(
            datasource_uuid = dtsrc.callback_uuid
        )

        req = RPC_pb2.Request(
            type = RPC_pb2.DS_SIZE,
            args = args.SerializeToString()
        )

        data = req.SerializeToString()
        self.socket.send(data)

        resp = RPC_pb2.Response()
        resp.ParseFromString(self.socket.recv())

        msg = datasource.Size_pb2.Result()
        msg.ParseFromString(resp.result)

        if msg.value is not None:
            return msg.value
        return -1

    def set_empty_callback_for_source(self, data_object : Security):

        args = datasource.SetEmptyCallback_pb2.Args(
            datasource_uuid = data_object.callback_uuid
        )
        
        req = RPC_pb2.Request(
            type = RPC_pb2.DS_SET_EMPTY_CALLBACK,
            args = args.SerializeToString()
        )

        data = req.SerializeToString()
        try:
            self.socket.send(data)

            resp = RPC_pb2.Response()
            resp.ParseFromString(self.socket.recv())

            msg = datasource.SetEmptyCallback_pb2.Result()
            msg.ParseFromString(resp.result)
            self.event_listener.event.emit("info", "general", f"Successfully set callback for datasource {data_object.class_code_security_combo}", self.get_timestamp_now())
        except Exception as e:
            self.event_listener.event.emit("error", errors.ERR_DATASOURCE_REGISTRATION, f"error setting callback for {data_object.class_code_security_combo}. {str(e)}", self.get_timestamp_now())

    """
    Removes datasource obj from dict
    """
    def remove_datasource(self, classcode_security_combo):
        
        if classcode_security_combo in self.existing_data_objects:
            self.existing_data_objects.pop(classcode_security_combo)

    def update_loop(self, data_source_security_combo : str):

        data_source = self.existing_data_objects[data_source_security_combo]
        #self.set_empty_callback_for_source(data_source)

        upd_candle_size = self.get_candle_size(data_source.class_code_security_combo)

        if upd_candle_size == -1:
            self.event_listener.event.emit("error", errors.ERR_INCORRECT_CANDLE, f"Unable to get price range for {data_source.class_code_security_combo}", self.get_timestamp_now())
            return

        args = datasource.O_pb2.Args(
            datasource_uuid = data_source.callback_uuid,
            candle_index = upd_candle_size
        )

        req = RPC_pb2.Request(
            type = RPC_pb2.DS_O,
            args = args.SerializeToString()
        )

        data = req.SerializeToString()

        try:
            self.socket.send(data)
                
            resp = RPC_pb2.Response()
            resp.ParseFromString(self.socket.recv()) # REQ type of socket is blocked on mute, so it waits forever...

            msg = datasource.O_pb2.Result()
            msg.ParseFromString(resp.result)

            self.event_listener.event.emit("ticker-update", data_source.class_code_security_combo, msg.value, self.get_timestamp_now())    
            
        except Exception as e:
            self.event_listener.event.emit("error", errors.ERR_INCORRECT_CANDLE ,f"error updating candle for {data_source.class_code_security_combo} {str(e)}", self.get_timestamp_now())

    def get_timestamp_now(self) -> str:
        upd_time_obj = datetime.now()
        update_timestamp = upd_time_obj.strftime("%Y-%m-%dT%H:%M:%S.%f'")[:-3]
        return update_timestamp

    def run(self):
        self.listen()

    def listen(self):
        while self.prevent_updates is False:              
            for data_object in self.existing_data_objects.values():
                try:
                    security_class = data_object.class_code_security_combo
                    self.update_loop(security_class)
                except KeyboardInterrupt:
                    print("interrupt")
            time.sleep(INTERVAL_DURATION.get(self.update_interval) / 1000)

    def stop_updates(self):
        self.event_listener.event.emit("info", "general", f"Stopped updates for datasources", self.get_timestamp_now())
        self.prevent_updates = True
    
    def start_updates(self):
        self.event_listener.event.emit("info", "general", f"Started updates for datasources", self.get_timestamp_now())
        self.prevent_updates = False
        self.run()