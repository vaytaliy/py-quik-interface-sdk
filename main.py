import dotenv
from src import reqrep_message as msgr
from dotenv import dotenv_values
config = dotenv_values(".env")

import time

m = msgr.QuikInterface(url=config["CONN_URL"],
        user=config["USER"],
        password=config["PASSWORD"],
        encoding='utf8',
        update_interval=1) #interval 1 doesn't work right for test accounts

"""
This example function allows you to have your custom handlers for price changes/errors
It will receive those updates perpetually until QuikInterface instance receives a command
to stop updates from happening, this can be reverted to get updates again
"""
def handle_securities():
        def on_ticker_update(security_combo : str, price : str, update_timestamp : str):
                print(f"[{update_timestamp}] ticker security update {security_combo} : {price}" )

        def on_ticker_error(error_type : str, error_message : str):
                print(f"error {error_type} : {error_message}" )

        m.event_listener.set_event_listener("ticker-update", on_ticker_update)
        m.event_listener.set_event_listener("error", on_ticker_error)

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

time.sleep(2)

m.remove_datasource('QJSIMMGNT')

"""
tells to stop receiving more updates, this can be reverted later by invoking start_updates function
"""
time.sleep(3)
m.stop_updates() 


print("main thread isn't blocked")

