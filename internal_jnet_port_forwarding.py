import subprocess, contextlib
import warnings, platform
import typing, os, string, random, socket

def greet(suppress = False):
    def _greet(f):
        def wrapper(_inst, *args, **kwargs):
            if not suppress:
                print(f'*{"+"*80}*')
                print(''.join(random.choice(string.printable) if random.choice(([0]*1)+([1]*9)) else ' ' for i in range(80))+('\n'*3))
                b = " Welcome to Morpheus "
                print(f'*{" "*int((78-len(b))/2)}{b}{" "*int((78-len(b))/2)}*')
                c = " for info, see here "
                print(f'*{" "*int((78-len(c))/2)}{c}{" "*int((78-len(c))/2)}*')
            return f(_inst, *args, **kwargs)
        return wrapper
    return _greet

class PortMap:
    def __init__(self, lan, _to, _from) -> None:
        self.lan, self._to, self._from = lan, _to, _from
    def __repr__(self):
        return f'<{self.__class__.__name__} machine={self.lan}, {self._to} => {self._from}>'


def forward_ports(root:str, _ip:str, _from:str, _to:str) -> None:
    cmd = ['sudo', '-k', '-S', '-p', '', 'pfctl', '-ef', '-']
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True) 
    text = f'{root}\n'
    text += f'rdr pass inet proto tcp from any to any port {_from} -> {_ip} port {_to}\n'
    _ = p.communicate(text)


def clear_mapping(root:str) -> None:
    p = subprocess.Popen(['sudo', '-S']+'pfctl -F all -f /etc/pf.conf'.split(), stdin=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
    text = f'{root}\n'
    _ = p.communicate(text)


class PortManager:
    _reset_mapping = False
    _warnings = [['forward_ports', 'Port forwarding not enabled'], ['root', 'Root access not attained. Ports not forwarded'], ['lan_ip', 'LAN IP not specified. Ports not forwarded'], ['from_port', 'No target port specified for port forwarding']]
    @classmethod
    def get_my_ip(cls, routerip=None):
        '''
        from https://github.com/jfdelgad/port-forward/blob/master/port-forward_3.py
        '''
        if routerip==None:
            routerip="8.8.8.8" #default route
        ret = None
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect((routerip,80))
            ret = s.getsockname()[0]
            s.close()
        except:
            pass
        return ret
    @classmethod
    def forward_port(cls, reset=False):
        cls._reset_mapping = reset
        def _forward_ports(_f:typing.Callable) -> typing.Callable:
            def __wrapper(_inst):
                _flag = True
                for a, b in cls._warnings:
                    if not getattr(_inst, a, False):
                        print(a, _inst)
                        _flag = False
                        warnings.warn(b)
                if _flag and getattr(_inst, 'forward_ports'):
                    print(f'Forwarding port {getattr(_inst, "from_port")} to port {getattr(_inst, "port")}')
                    forward_ports(getattr(_inst, 'root'), getattr(_inst, 'lan_ip'), getattr(_inst, 'from_port'), getattr(_inst, 'port'))
                
                return _f(_inst)

            return __wrapper
        return _forward_ports
    @classmethod
    def reset_mapping(cls, _f):
        def __wrapper(_inst, *args):
            if cls._reset_mapping:
                clear_mapping(_inst.root)
            return _f(_inst, *args)
        return __wrapper

if __name__ == '__main__':
   

    class NetVals:
        root = 'zorro16'
        lan_ip = '192.168.0.5'
        forward_ports = True
        port = 6000
        from_port = 8423

    @PortManager.forward_port(reset = False)
    def _wrap_ports(_self):
        return 

    print(_wrap_ports(NetVals))
