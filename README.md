# quik-trading-bot
# This is an SDK to support development of trading bots for QUIK terminal

## Features:
1. Tracking price changes of multiple securities in real time at a specified update rate
2. Securities can be removed and added from tracking
3. Price changes are sent to event listener function specified by user, so that user can listen to these events and execute logic on top
4. Error messages are also received as events, so that user can understand what went wrong in the code
5. Event emitter and security tracker run in parallel without blocking the main thread
6. Security tracker constructor accepts optional is_daemon property, which will signal end of refresh execution once main thread is not alive. By default it is false, the only way to stop updates from executing is by invoking stop_updates method

## Prerequisites:

1. Python 3 +
2. QUIK terminal
3. Active QUIK account: quik junior or regular account (quick junior is used for learning/trading with imaginary money, can be obtained here https://arqatech.com/en/support/demo/)
4. All the necessary scripts to allow QUIK to work with external scripts. More information on how to set that up : https://github.com/Enfernuz/quik-lua-rpc/blob/master/docs/python_zmq_protobuf.md

## Example output (powershell):

![PS output](/assets/py_quik.PNG "Output sample")
