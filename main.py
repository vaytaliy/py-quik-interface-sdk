from src import reqrep_message as msgr
from dotenv import dotenv_values
from src.batch_processor import FileBatchProcessor
config = dotenv_values(".env")

import time

m = msgr.QuikInterface(url=config["CONN_URL"],
        user=config["USER"],
        password=config["PASSWORD"],
        encoding='utf8',
        update_interval=2) #interval 1 doesn't work right for test accounts

"""
Example batch processor which will save ticker update logs into .txt
"""
batch_processor = FileBatchProcessor()
"""
This example function allows you to have your custom handlers for price changes/errors
It will receive those updates perpetually until QuikInterface instance receives a command
to stop updates from happening, this can be reverted to get updates again
"""
def handle_securities():
        
        def on_ticker_update(security_combo : str, price : str, update_timestamp : str):
                print(f"UPDATE [{update_timestamp}] {security_combo} : {price}" )
                batch_processor.add_text_to_log(f"[{update_timestamp}]:{security_combo}:{price} ")

        def on_ticker_error(error_type : str, error_message : str, error_timestamp : str):
                print(f"ERROR [{error_timestamp}] {error_type} : {error_message}" )

        def on_info(info_type : str, info_details : str, info_timestamp: str):
                print(f"INFO [{info_timestamp}] {info_type} : {info_details}")

        m.event_listener.set_event_listener("ticker-update", on_ticker_update)
        m.event_listener.set_event_listener("error", on_ticker_error)
        m.event_listener.set_event_listener("info", on_info)

handle_securities()

m.create_new_data_source(
        msgr.Security(
                class_code = 'QJSIM',
                security_code = 'GLTR')
)

m.create_new_data_source(
        msgr.Security(
                class_code = 'QJSIM',
                security_code = 'MGNT')
)

time.sleep(180)
"""
After 3 mins of execution this stock will be removed and will no longer receive new updates
"""
m.remove_datasource('QJSIMMGNT')

while True:
        print("main thread isn't blocked and you can still receive updates")
        time.sleep(45)

