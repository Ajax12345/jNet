import eel, random
import pickle, internal_morpheus
import gevent
import gevent.monkey
gevent.monkey.patch_all()
import socket, requests
from bs4 import BeautifulSoup as soup
import contextlib, typing, json
import jnet_utilities, jnet_connectors
import on_connection_action

#NOTE: will need to adjust recv_size in interal_morpheus

eel.init('jnet_static_folder')

class TaskManager:
    def __init__(self):
        self.all_tasks = {}
    def __contains__(self, _task_id):
        return _task_id in self.all_tasks
    @staticmethod
    def generate_task_id(_tasks):
        import random, string
        _id = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(6, random.randint(10, 20)))
        while _id in _tasks:
            _id = ''.join(random.choice(string.ascii_letters+string.digits) for _ in range(6, random.randint(10, 20)))
        return _id
    def __getitem__(self, _task_id):
        return None if _task_id not in self else self.all_tasks[_task_id]
    def __setitem__(self, _task_id, _result):
        self.all_tasks[_task_id] = _result

def update_app_manager() -> None:
    @contextlib.contextmanager
    def _communicate() -> typing.Generator[dict, None, None]:
        yield json.loads(requests.get(f'http://jamespetullo.pythonanywhere.com/refresh_apps/firstapp/{random.randint(1, 100)}').text)

    while True:
        with _communicate() as _response:
            print(f'command result: {_response}')

        eel.sleep(2)

def server_thread() -> None:
    print('in server_thread')
    def handle_connection(c, addr):
        print(f'Recieved connnection from {addr[0]}')
        _data = c.recv(1024)
        print(f'Got {_data} from {addr[0]}')
        c.sendall(pickle.dumps({'echo':pickle.loads(_data)}))

    @internal_morpheus.on_connection(on_connection_action.on_connection)
    class MainServer(internal_morpheus.Server):
        _max_connections = 100
        main_host = ''
        lan_ip = internal_morpheus.jnet_port_forwarding.PortManager.get_my_ip()
        root = jnet_utilities.get_root_passcode()
        #NOTE: both ports will be determined at run time of the app
        port = 6000
        from_port = 8423
        forward_ports = True

    with MainServer() as server:
        server.accept_connections()


@jnet_utilities.mute
def set_spawns():
    eel.spawn(update_app_manager)
    #check to ensure the browser is configured
    eel.spawn(server_thread)

if jnet_utilities.is_configured():
    set_spawns()

@eel.expose
def scraper():
    d = soup(requests.get('https://www.newsmax.com/').text, 'html.parser')
    results = [i.find('div', {'class':'nmNewsfrontT'}).find('div', {'class':'nmNewsfrontHead'}).h2.text  for i in d.find_all('div', {'class':'nmNewsfrontStory'})]
    return '<ul>{}</ul>'.format('\n'.join(f'<li>{i}</li>' for i in results))

@eel.expose
def verify_passcode(_passcode):
    return 'true' if jnet_utilities.test_passcode(_passcode) else 'false'

@eel.expose
def setup_main_browser(passcode, _vals:dict):

    jnet_utilities.setup_browser(passcode, _vals)
    set_spawns()
    return 'done'

@eel.expose
def is_setup():
    return "true" if jnet_utilities.is_configured() else "false"

@eel.expose
def get_browser_body():
    return open('jnet_static/browser_essential.html').read()
    
@eel.expose
def get_setup_body():
    return open('jnet_static/welcome_html.html').read()

@eel.expose
def testing():
    return "hi"

@eel.expose
def get_full_username():
    return jnet_utilities.get_full_username()


@eel.expose
def get_home_search():
    return open('jnet_static_folder/home_search_bar.html').read()
#eel.start('main_window.html')

eel.start('browser_window.html')
