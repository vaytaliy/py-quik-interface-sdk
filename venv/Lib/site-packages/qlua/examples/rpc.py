"""
Коммуникация с сервером, посредствам zmq и protobuf.
"""

import logging
import zmq

from qlua.rpc import RPC_pb2, getInfoParam_pb2


log = logging.getLogger(__name__)
# Включение отображения сообщений отладки:
# log.setLevel(logging.DEBUG)


def main(url: str, user: str, passwd: str,
         encoding: str = 'utf8') -> bool:
    """Получение версии Quik."""

    # Пример вызова:
    # Активировать venv.
    # python -m qlua.examples.rpc

    # Создание подключения Quik.
    ctx = zmq.Context.instance()
    socket = ctx.socket(zmq.REQ)
    socket.plain_username = user.encode(encoding)
    socket.plain_password = passwd.encode(encoding)
    socket.connect(url)

    # Создание и отправка запроса.
    args = getInfoParam_pb2.Args()
    args.param_name = 'VERSION'
    req = RPC_pb2.Request()
    req.type = RPC_pb2.GET_INFO_PARAM
    req.args = args.SerializeToString()
    log.debug('Содержимое запроса:\n%s', req)
    data = req.SerializeToString()
    socket.send(data)

    # Получение ответа.
    resp = RPC_pb2.Response()
    resp.ParseFromString(socket.recv())
    log.debug('Содержимое ответа: %s', resp.result)
    msg = getInfoParam_pb2.Result()
    msg.ParseFromString(resp.result)
    print('Ответ Quik:', msg.info_param)

    # Отключение от Quik.
    ctx.destroy()

    return True


if __name__ == '__main__':
    main(
        url='tcp://127.0.0.1:5560',
        user='myUser',
        passwd='myPassWord',
    )
