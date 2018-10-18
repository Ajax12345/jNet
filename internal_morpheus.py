import socket, pickle
import interal_jnet_port_forwarding as jnet_port_forwarding
import typing

def on_connection(_func:typing.Callable) -> typing.Callable:
    def _wrapper(_cls):
        setattr(_cls, 'on_accept_connection', _func)
        return _cls
    return _wrapper



def my_lan_ip() -> str:
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(('8.8.8.8', 80))
    return s.getsockname()[0]

class _lanOptions:
    def __init__(self):
        *self._main, _ = my_lan_ip().split('.')
    def __iter__(self):
        for i in range(25):
            yield f'{".".join(self._main)}.{i}'


class LanIps:
    '''
    rarity: 1 - 3, most common to least common
    if rarity = 3, all combinations are generated
    '''
    def __init__(self, preface='192', rarity=1):
        self.preface = preface
        self.rarity = rarity
        self.all_ranges = {'192':[168, [0, 256], [0, 256]], '10':[[0, 256], [0, 256], [0, 256]], '172':[[16, 32], [0, 256], [0, 256]]}
    def __repr__(self):
        _r = self.all_ranges[self.preface]
        return f"<{self.preface}.{_r[0] if isinstance(_r[0], int) else '-'.join(map(str, _r[0]))}.{'-'.join(map(str, _r[1]))}.{'-'.join(map(str, _r[2]))}>"
    def __iter__(self):
        _r = self.all_ranges[self.preface]
        if isinstance(_r[0], int):
            if self.rarity == 3:
                for i in range(*_r[1]):
                    for b in range(*_r[-1]):
                        yield f'{self.preface}.{_r[0]}.{i}.{b}'
            else:
                for i in range(25):
                    yield f'{self.preface}.{_r[0]}.0.{i}' if self.rarity == 2 else f'{self.preface}.{_r[0]}.1.{i}'
        
        else:
            if self.rarity == 3 or self.preface == '172':

                for i in range(*_r[0]):
                    for b in range(*_r[1]):
                        for c in range(*_r[2]):
                            yield f'{self.preface}.{i}.{b}.{c}'
            else:
                for i in range(25):
                    yield f'{self.preface}.{1}.{1}.{i}' if self.rarity == 1 else f'{self.preface}.{0}.{0}.{i}'

class Ping:
    def __init__(self, _ip:str, port:int) -> None:
        self.ip, self.port = _ip, port
    def __enter__(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.connect((self.ip, self.port))
        return True
    def __exit__(self, *args):
        pass
    

class Server:
    @jnet_port_forwarding.greet()
    @jnet_port_forwarding.PortManager.forward_port()
    def __enter__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        print(f'listening on {self.port} at "{self.main_host}"')
        self._socket.bind((self.main_host, self.port))
        self._socket.listen(self._max_connections)
        return self
    def accept_connections(self):
        while True:
            try:
                c, addr = self._socket.accept()
            except:
                pass
            else:
                '''
                print(f'Recieved connnection from {addr[0]}')
                _data = c.recv(_rec_size)
                print(f'Got {_data} from {addr[0]}')
                c.sendall(pickle.dumps(on_recieve(pickle.loads(_data))))
                '''
                self.__class__.on_accept_connection(c, addr)
    @jnet_port_forwarding.PortManager.reset_mapping
    def __exit__(self, *args):
        print(self.__dict__)
        self._socket.close()



class Client:
    def __init__(self, _host:str, _port:int) -> None:
        self.host, self.port = _host, _port
    def __enter__(self):
        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._socket.connect((self.host, self.port))
        return self
    def send_data(self, _data):
        print('in here', _data)
        val = pickle.dumps(_data)
        print('val', val)
        self._socket.sendall(val)
        result = self._socket.recv(1024)
        print('got result here', result)
        return pickle.loads(result)
    def __exit__(self, *args):
        pass

if __name__ == '__main__':

    def recieve_connection(_client, addr):
        print('this is new here')
        print(f'Recieved connnection from {addr[0]}')
        _data = _client.recv(1024)
        print(f'Got {_data} from {addr[0]}')
        _client.sendall(pickle.dumps({'echo':pickle.loads(_data)}))
    
    @on_connection(recieve_connection)
    class Manage_Server(Server):
        _max_connections = 5
        main_host = ''
        lan_ip = jnet_port_forwarding.PortManager.get_my_ip()
        root = 'PASSWORD'
        port = 6001
        from_port = 8423
        forward_ports = True

    with Manage_Server() as server:
        server.accept_connections()
