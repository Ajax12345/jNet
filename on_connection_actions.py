import jnet_server_connector, pickle


def on_connection(c, addr) -> dict:
    '''
    print(f'Recieved connnection from {addr[0]}')
    _data = c.recv(1024)
    print(f'Got {_data} from {addr[0]}')
    c.sendall(pickle.dumps({'echo':pickle.loads(_data)}))
    '''
    payload = {**{'ip':addr[0]}, **pickle.loads(c.recv(1024))}
    _new_payload = getattr(jnet_server_connector, f'request_{payload["request-type"]}')(payload['payload'])
    return c.sendall(pickle.dumps(_new_payload))
