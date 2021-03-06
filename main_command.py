import eel, random
import pickle, internal_morpheus
import gevent
import gevent.monkey
gevent.monkey.patch_all()
import socket, requests
from bs4 import BeautifulSoup as soup
import contextlib, typing, json
import jnet_utilities, jnet_connectors
import on_connection_actions, jinja2

#NOTE: will need to adjust recv_size in interal_morpheus
#TODO: build local routing object under the "jnet-browser" server
#TODO: create program to detect HTML id and class names that are not valid. Build a feature in app page to scan app source for such keywords
#TODO: for all id and classnames in browser_window.html, add "__" at the end of each
#TODO: build scanner anyway
#UPDATED: jnet_utilities.py, jnet_connectors.py
#TODO: cache tab content
#TODO: update app creation function to include server hosting of app
#TODO: add the ability to update internal server listing
#TODO: build form posting with element data attributes
#TODO: change app views to total views, rather than monthly views
#TOUPDATE:
#   jnet_utilities.py
#   browser_style.css
#   full_app_listing.html
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

@eel.expose
def get_browser_history():
    return jnet_utilities.jNetHistory.render_history()

@eel.expose
def filter_browser_history(keyword):
    return jnet_utilities.jNetHistory.render_filter_history(keyword)

@eel.expose
def delete_selected_history(deletion_ids):
    jnet_utilities.delete_history(_ids = [int(i) for [i] in json.loads(deletion_ids)])
    return 'done'

@eel.expose
def delete_all_history():
    jnet_utilities.delete_history(by_id=True)
    return 'done'

@eel.expose
def get_app_listing():
    return open('jnet_static_folder/full_app_listing.html').read()

@eel.expose
def accept_query(jnet_url, _tab):
    _parsed = jnet_connectors.jNetUrl(jnet_url)
    if _parsed.server == 'jnet-browser':
        _full_result = jnet_connectors.jnet_browser_url(_parsed, _tab)
        print('full result', _full_result)
        return _full_result
    return jnet_connectors._NewBrowserQuery.accept_query(_tab, jnet_url, {}).jsonify


@eel.expose
def accept_query_form(jnet_url, _tab, _form):
    _parsed = jnet_connectors.jNetUrl(jnet_url)
    if _parsed.server == 'jnet-browser':
        _full_result = jnet_connectors.jnet_browser_url(_parsed, int(_tab), _forms=json.loads(_form))
        print('in form query, ', _full_result)
        return _full_result
    return 

@eel.expose
def accept_dynamic_query_form(jnet_url, _tab, _form):
    _parsed = jnet_connectors.jNetUrl(jnet_url)
    if _parsed.server == 'jnet-browser':
        _result = jnet_connectors.jnet_dynamic_url(_parsed, int(_tab), _forms=_form)
        print('for app creation ', type(_result))
        return _result

@eel.expose
def delete_app(_title):
    jnet_utilities.delete_user_app(_title)
    return "done"


@eel.expose
def enable_app_check(_name):
    _invalid = jnet_utilities.invalid_tag_names(_name)
    _classes = [i for i in _invalid if i.attr_type == 'class']
    _ids = [i for i in _invalid if i.attr_type == 'id']
    return jinja2.Template(open('jnet_static_folder/invalid_app_tag_display.html').read()).render(classes = jnet_utilities._tag_templating(_classes), ids = jnet_utilities._tag_templating(_ids))
#eel.start('main_window.html')
eel.start('browser_window.html')
