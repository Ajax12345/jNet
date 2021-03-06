from subprocess import PIPE, Popen
import re, platform, warnings, json
import datetime, contextlib, sqlite3
import typing, tigerSqlite
import multiprocessing, itertools
import time, os, jinja2
from bs4 import BeautifulSoup as soup

def test_passcode(_code:str) -> bool:
    '''only supported on Darwin'''
    if platform.system() == 'Darwin':
        text = f'{_code}\n'
        p = Popen(['sudo', '-k', '-S', '-p', '', 'ls'], stdin=PIPE, stderr=PIPE, universal_newlines=True)
        _, b = p.communicate(text)
        return not bool(re.findall('^Sorry, try again', b))
    warnings.warn('System not detected. Cannot check passcode')


def is_configured() -> bool:
    with open('browser_settings/__browser_settings__.json') as f:
        return json.load(f)["configured"]

def setup_browser(passcode:str, _data:dict) -> None:
    with open('browser_settings/__browser_settings__.json', 'w') as f:
        d = datetime.datetime.now()
        json.dump({'configured':True, 'user_info':{'root_password':passcode, 'configured_on':[getattr(d, i) for i in ['year', 'month', 'day', 'hour', 'minute', 'second']], **_data}}, f)


def get_root_passcode() -> str:
    with open('browser_settings/__browser_settings__.json') as f:
        _d = json.load(f)
        if _d['configured']:
            return _d['user_info']['root_password']



def get_full_username() -> str:
    with open('browser_settings/__browser_settings__.json') as f:
        _d = json.load(f)
        if _d['configured']:
            return f"{_d['user_info']['firstname']} {_d['user_info']['lastname']}"


def mute(f):
    return lambda *args, **kwargs:None


def app_exists(_name:str) -> bool:
    return any(_name == re.sub('^app_', '', i) for i in os.listdir('apps'))

@contextlib.contextmanager
def add_server_hosting(name:str, _url:str):
    conn = sqlite3.connect('browser_settings/server_hostings.db')
    _d = datetime.datetime.now()
    _timestamp = '-'.join(str(getattr(_d, i)) for i in ['month', 'day', 'year'])+' '+':'.join(str(getattr(_d, i)) for i in ['hour', 'minute', 'second'])
    conn.execute("INSERT INTO servers VALUES (?, ?, ?)", [name, _url, _timestamp])
    conn.commit()
    conn.close()
    yield _timestamp

class TabRow:
    headers = ['tabid', 'siteip', 'appname', 'url', 'path', 'sessions']
    def __init__(self, *args):
        self.__dict__ = {a:b for a, b in itertools.zip_longest(self.__class__.headers, args)}
    def __bool__(self):
        return any(getattr(self, i, None) for i in self.__class__.headers[1:])
    def __repr__(self):
        return f'{self.__class__.__name__}({self.__dict__})'

def find_tab(tab_num:int) -> typing.NamedTuple:
        #num real, ip text, app text, url text, path text, session text
    tabs = [i for i in tigerSqlite.Sqlite('browser_settings/browser_tabs.db').get_num_ip_app_url_path_session('tabs') if i[0] == tab_num]
    return TabRow(tab_num) if not tabs else TabRow(*tabs[0])
    

def server_loc(_server_name:str) -> str:
    return [i for i in sqlite3.connect('browser_settings/server_hostings.db').cursor().execute("SELECT * FROM servers") if i[0] == _server_name][0][1]

def get_session(_tab_num:int) -> dict:
    return [b for a, b in tigerSqlite.Sqlite('browser_settings/browser_tabs.db').get_num_session('tabs') if a == _tab_num][0]

def _max_history_id() -> int:
    _d = [a for a, *_ in sqlite3.connect('browser_settings/browser_history.db').cursor().execute("SELECT * FROM history")]
    return 1 if not _d else max(_d) + 1
    
def delete_bulk(_files = list(filter(lambda x:x.endswith('.db') and x.startswith('browser_'), os.listdir('browser_settings')))):
    def _wrapper(f):
        def perform_op():
            for i in _files:
                f(filename=i)
        
        def __wrapper(*args, **kwargs):
            perform_op()
        return __wrapper
    return _wrapper

@delete_bulk()
def delete_from(filename='browser_history.db') -> None:
    conn = sqlite3.connect(f'browser_settings/{filename}')
    _tablename = re.sub('^[a-zA-Z]+_|\.db$', '', filename)
    conn.execute(f"DELETE FROM {_tablename}")
    conn.commit()
    conn.close()

def display_tables(filename='browser_history.db') -> typing.List[tuple]:
    _tablename = re.sub('^[a-zA-Z]+_|\.db$', '', filename)
    return list(sqlite3.connect(f'browser_settings/{filename}').cursor().execute(f"SELECT * FROM {_tablename}"))

def log_tab_history(f:typing.Callable) -> typing.Callable:
    def _wrapper(site_obj, url, _tab, request_type, update=False, forms={}) -> typing.Any:
        d = datetime.datetime.now()
        timestamp = '-'.join(str(getattr(d, i)) for i in ['month', 'day', 'year'])+' '+':'.join(str(getattr(d, i)) for i in ['hour', 'minute', 'second'])
        current_id =  _tab.tabid
        #[_max_history_id(), url.app_name, url.path, site_obj.ip, url.server, timestamp]
        headers = ['id', 'app_name', 'url_path', 'ip', 'server', 'timestamp']
        if update:
            _current = [b for a, b in tigerSqlite.Sqlite('browser_settings/browser_tab_history.db').get_id_tabs('tab_history') if a == current_id][0]
            tigerSqlite.Sqlite('browser_settings/browser_tab_history.db').update('tab_history', [['tabs', _current+[dict(zip(headers, [_max_history_id()-1, url.app_name, url.path, site_obj.ip, url.server, timestamp]))]]], [['id', current_id]])
        else:
            tigerSqlite.Sqlite('browser_settings/browser_tab_history.db').insert('tab_history', ('id', current_id), ('tabs', [dict(zip(headers, [_max_history_id(), url.app_name, url.path, site_obj.ip, url.server, timestamp]))]))
        return f(site_obj, url, _tab, request_type, update=update, forms=forms)
    return _wrapper

def log_history(f:typing.Callable):
    def wrapper(site_obj, url, _tab, request_type, update=False, forms={}):
        d = datetime.datetime.now()
        timestamp = '-'.join(str(getattr(d, i)) for i in ['month', 'day', 'year'])+' '+':'.join(str(getattr(d, i)) for i in ['hour', 'minute', 'second'])
        #id real, app text, path text, ip text, server text, timestamp text
        conn = sqlite3.connect('browser_settings/browser_history.db')
        conn.execute("INSERT INTO history VALUES (?, ?, ?, ?, ?, ?)", [_max_history_id(), url.app_name, url.path, site_obj.ip, url.server, timestamp])
        conn.commit()
        conn.close()
        return f(site_obj, url, _tab, request_type, update=update, forms=forms)
    return wrapper


class TimedOut(Exception):
    pass

def terminate_delay(_time):
    def _wrapper(_f:typing.Callable):
        def __test_run(_func:typing.Callable, _queue, args, kwargs):
            _r = _func(*args, **kwargs)
            _queue.put({'_r_result':_r})
        
        def _main_wrapper(*args, **kwargs):
            _respond = multiprocessing.Queue()
            p = multiprocessing.Process(target=__test_run, name="Attempt_connect", args=(_f, _respond, args, kwargs))
            p.start()
            time.sleep(_time)
            p.terminate()
            p.join()
            try:
                _r = _respond.get(False)
            except:
                raise TimedOut(f'"{_f.__name__}" timed out after {_time} second{"s" if _time != 1 else ""}')
            else:
                return _r['_r_result']
        return _main_wrapper
    return _wrapper


def create_app(_name:str, _description:str, _host:str) -> None:
    d = datetime.datetime.now()
    _ = os.system(f'mkdir apps/app_{_name}')
    _timestamp = '-'.join(str(getattr(d, i)) for i in ['month', 'day', 'year'])+' '+':'.join(str(getattr(d, i)) for i in ['hour', 'minute', 'second'])
    with open(f'apps/app_{_name}/app_config.json', 'w') as f:
        json.dump({'live':False, 'created_on':[getattr(d, i) for i in ['year', 'month', 'day', 'hour', 'minute', 'second']], 'description':_description, 'host':_host, 'deleted':False}, f)
    
    _ = os.system(f'mkdir apps/app_{_name}/templates')
    with open(f'apps/app_{_name}/templates/home.html', 'w') as f:
        f.write(open('jnet_static_folder/jnet_app_template.html').read())
    
    with open(f'apps/app_{_name}/templates/home_style.css', 'w') as f:
        f.write(open('jnet_static_folder/jnet_app_template_style.css').read())

    with open(f'apps/app_{_name}/templates/home_js.js', 'w') as f:
        f.write(open('jnet_static_folder/jnet_app_template_js.js').read())
    
    with open(f'apps/app_{_name}/log.txt', 'w') as f:
        f.write(f'{_timestamp}: app "{_name}" created\n')
    
    with open(f'apps/app_{_name}/app_routes.py', 'w') as f:
        f.write(open('app_main_template.py').read().format(_name))

    for _file in ['telemonius', 'telemonius_routes', 'telemonius_wrappers', 'telemonius_errors']:
        with open(f'apps/app_{_name}/{_file}.py', 'w') as f:
            f.write(open(f'_{_file}.py').read())
    

    conn = sqlite3.connect(f'apps/app_{_name}/__views__.db')
    conn.execute("CREATE TABLE views (timestamp text, ip text, visitor text, path text, server text)")
    conn.commit()
    conn.close()



def browser_app_listing() -> set:
    return {re.sub('^browser_app_|\.py$', '', i) for i in os.listdir(os.getcwd()) if re.findall('^browser_app_', i)}

def added_jnet_servers() -> typing.List[str]:
    return [a for a, *_ in sqlite3.connect('browser_settings/server_hostings.db').cursor().execute("SELECT name FROM servers")]

def time_query(_isinstance=True):
    def _func_wrapper(f):
        def _time_results(_f, args:list, kwargs:dict) -> typing.Tuple[float, typing.Any]:
            _start = time.time()
            _result = _f(*args, **kwargs)
            return [time.time()-_start, _result]

        if _isinstance:
            def _wrapper(_cls, *args, **kwargs) -> typing.Any:
                _time, _returned_result = _time_results(f, [_cls, *args], kwargs)
                return _cls(_time, *args, _returned_result, **kwargs)
        else:
            def _wrapper(*args, **kwargs) -> typing.Any:
                return _time_results(f, args, kwargs)
        return _wrapper
    return _func_wrapper



def log_view(_f:typing.Callable) -> typing.Callable:
    #timestamp text, ip text, visitor text, path text, server text
    def _wrapper(_payload:dict):
        d = datetime.datetime.now()
        _timestamp = '-'.join(str(getattr(d, i)) for i in ['month', 'day', 'year']) + ' '+':'.join(str(getattr(d, i)) for i in ['hour', 'minute', 'second'])
        conn = sqlite3.connect(f'apps/app_{_payload["app"]}/__views__.db')
        conn.execute("INSERT INTO views VALUES (?, ?, ?, ?, ?)", [_timestamp, _payload['ip'], _payload['sender'], _payload['path'], _payload['server']])
        conn.commit()
        conn.close()
        return _f(_payload)
    return _wrapper

def get_attrs(_f:typing.Callable) -> typing.Callable:
    def _wrapper(_url_obj, _response_obj):
        return _f(_url_obj._original_url, _response_obj['route'])
    return _wrapper

def delete_history(_ids = None, by_id = False):
    conn = sqlite3.connect('browser_settings/browser_history.db')
    if not by_id:
        conn.executemany("DELETE FROM history WHERE id=?", [[i] for i in _ids])

    else:
        conn.execute("DELETE FROM history")
    conn.commit()
    conn.close()
    for a, b in tigerSqlite.Sqlite('browser_settings/browser_tab_history.db').get_id_tabs('tab_history'):
        tigerSqlite.Sqlite('browser_settings/browser_tab_history.db').update('tab_history', [['tabs', [] if by_id else [i for i in b if i['id'] not in _ids]]], [['id', a]])

def jsonify_result(f):
    def _wrapper(*args, **kwargs):
        return json.dumps(f(*args, **kwargs))
    return _wrapper


def delete_user_app(_name:str) -> None:
    with open(f'apps/app_{_name}/app_config.json') as f:
        data = json.load(f)
        data['deleted'] = True

    with open(f'apps/app_{_name}/app_config.json', 'w') as f:
        print('deletion_data here', data)
        json.dump(data, f)

def cache_request_response(f):
    #_time_completed:float, _tab:int, _url:str, _, _response_obj:BrowserResponse
    def _wrapper(_inst, *args):
        _t =  f(_inst, *args)
        #print('for val in cached ', _t, type(_t))
        #num real, url text, html text, css text, js text
        if any(int(c) == _inst.tab for c, *_ in sqlite3.connect('browser_settings/cached_tabs.db').cursor().execute("SELECT * FROM cached_tabs")):
            tigerSqlite.Sqlite('browser_settings/cached_tabs.db').update('cached_tabs', [['url', _inst.url]]+[[i, _t[i] if i == 'html' else '' if i not in _t else open(f'jnet_static_folder/on_response.{i}').read()] for i in ['html', 'css', 'js']], [['num', _inst.tab]])
        else:
            tigerSqlite.Sqlite('browser_settings/cached_tabs.db').insert('cached_tabs', ('num', _inst.tab), ('url', _inst.url), *[(i, _t[i] if i == 'html' else '' if i not in _t else open(f'jnet_static_folder/on_response.{i}').read()) for i in ['html', 'css', 'js']])
        return _t
    return _wrapper

class jNetHistory:
    headers = ['id', 'app', 'path', 'ip', 'server', 'timestamp']
    class jnetHistoryItem:
        def __init__(self, _row:typing.List[str]) -> None:
            self.__dict__ = dict(zip(jNetHistory.headers, _row))
            self.id = int(self.id)
        @property
        def jnet_url(self):
            return str(self)
        @staticmethod
        def day_stamp(_obj:datetime.datetime) -> str:
            return 'Today' if not getattr(_obj, 'days', None) else 'Yesterday' if _obj.days == 1 else None
        @staticmethod
        def calc_timestamp(*args) -> str:
            _h, _m, _s = args
            return f'{_h%12 if _h%12 else 12}:{str(_m).zfill(2)} {"PM" if _h >= 12 else "AM"}'
        @property
        def day_occured(self):
            _mdy, _hms = self.timestamp.split()
            _m, _d, _y = map(int, re.findall('\d+', _mdy))
            _h, _min, _s = map(int, re.findall('\d+', _hms))
            _day_format = self.__class__.day_stamp(datetime.datetime.now() - datetime.datetime(_y, _m, _d, _h, _min, _s))
            return f'{_day_format if _day_format is not None else _mdy} at {self.__class__.calc_timestamp(_h, _min, _s)}'
        def __repr__(self):
            return f'<history_item({self.id}) jnet_url = {str(self)} timestamp={self.day_occured}>'

        def __contains__(self, _keyword:str) -> bool:
            return _keyword in str(self)
        def __str__(self) -> str:
            return f'{self.server}:@{self.app}{self.path}'
    def __init__(self, _content:typing.List[list]) -> None:
        self._content = _content
    def __bool__(self):
        return bool(self._content)
    def __iter__(self):
        yield from self._content[::-1]
    @classmethod
    def get_history(cls, _filter_keyword = ''):
        _content = list(sqlite3.connect('browser_settings/browser_history.db').cursor().execute("SELECT * FROM history"))
        _all_contents = [cls.jnetHistoryItem(i) for i in _content]
        return cls(list(filter(lambda x:_filter_keyword in x, _all_contents)))
    @classmethod
    def render_history(cls, keyword = ''):
        return jinja2.Template(open('jnet_static_folder/browser_history_listing.html').read()).render(history = cls.get_history(_filter_keyword = keyword))
    @classmethod
    def render_filter_history(cls, keyword):
        return jinja2.Template(open('jnet_static_folder/browser_filter_history_results.html').read()).render(history = cls.get_history(_filter_keyword = keyword))

    
class UserApps:
    class App:
        @classmethod
        def snapshot(cls, _name:str) -> typing.Callable:
            with open(f'apps/app_{_name}/app_config.json') as f:
                _config = json.load(f)
            _db_views = list(sqlite3.connect(f'apps/app_{_name}/__views__.db').cursor().execute("SELECT * FROM views"))
            return cls(_name, _config, _db_views)
        def __init__(self, _name:str, _config:dict, _db_views:list) -> None:
            self.app_name = _name
            self.__dict__.update(_config)
            self.db_views = _db_views
        @property
        def browser_url(self):
            return f'jnet-browser:@apps/app/{self.app_name}'
        @property
        def timestamp(self):
            _y, _m, _d, _hh, _mm, _ss = self.created_on
            return f'{_m}/{_d}/{_y} at {_hh%12}:{_mm} {"AM" if _hh < 12 else "PM"}'
        @property
        def monthly_views(self):
            _d = datetime.datetime.now()
            _val = sum(i[0] == _d.year and i[1] == _d.month for i in self.db_views)
            return _val
        @property
        def view_format(self):
            return 'views' if self.monthly_views != 1 else 'view'
            
        @property
        def status_color(self):
            return ['red', 'green'][bool(self.live)]

        @property
        def status_text(self):
            return ['Not deployed', 'Live'][bool(self.live)]

        def __repr__(self):
            return f'{self.__class__.__name__}({self.app_name})'
    def __init__(self, _listing:list) -> None:
        self._listing = _listing
    def __bool__(self):
        return bool(self._listing)
    def __contains__(self, _app:str) -> bool:
        return _app in self._listing
    @classmethod
    def is_deleted(cls, _name:str) -> bool:
        with open(f'apps/app_{_name}/app_config.json') as f:
            d = json.load(f)
            return d.get('deleted', False)

    @property
    def num(self):
        return sum(not self.__class__.is_deleted(i) for i in self._listing)

    def __iter__(self):
        for _app in self._listing:
            if not self.__class__.is_deleted(_app):
                yield self.__class__.App.snapshot(_app)

    @classmethod
    def display_apps(cls) -> typing.Callable:
        return cls([re.sub('^app_', '', i) for i in os.listdir('apps')])
    

class _tag:
    def __init__(self, _rule:typing.Callable[[str], bool]) -> None:
        self._rule = _rule
    def __call__(self, _tag_id_class:str) -> bool:
        return self._rule(_tag_id_class)
    
class _class:
    def __init__(self, _class_name:str) -> None:
        self._attr = _class_name
    @property
    def attr_type(self):
        return self.__class__.__name__[1:]
    def __eq__(self, _val:str) -> bool:
        return self._attr == _val._attr
    def __repr__(self):
        return f'<{self.attr_type} attribute "{self._attr}">'

class _id:
    def __init__(self, _id_name:str) -> None:
        self._attr = _id_name
    @property
    def attr_type(self):
        return self.__class__.__name__[1:]
    def __eq__(self, _val:str) -> bool:
        return self._attr == _val._attr
    def __repr__(self):
        return f'<{self.attr_type} attribute "{self._attr}">'

class _tag_templating:
    def __init__(self, _listing:typing.List[typing.Callable]) -> None:
        self._tags = _listing
    @property
    def num(self):
        return len(self._tags)
    def __bool__(self):
        return bool(self._tags)
    @property
    def display_content(self):
        return ', '.join(self)
    @property
    def text(self):
        _preface = self._tags[0].__class__.__name__[1:]
        return _preface if self.num == 1 else f'{_preface}s' if _preface == 'id' else 'classes'
    def __iter__(self):
        for i in self._tags:
            yield f'<strong class="__invalid_tag__">{i._attr}</strong>'

def invalid_tag_names(_app:str) -> typing.List[str]:
    def all_tags(d):
        _attrs = getattr(d, 'attrs', {})
        yield from map(_class, _attrs.get('class', []))
        yield from map(_id, ([] if 'id' not in _attrs else [_attrs['id']]))
        for i in getattr(d, 'contents', []):
            if not isinstance(d, str):
                yield from all_tags(i)

    _keep = [_tag(lambda x:x._attr in ['col', 'row', 'container', 'col-md-auto']), _tag(lambda x:bool(re.findall('^fa\-|^fas', x._attr)))]
    _html_files = [i for i in os.listdir('jnet_static_folder') if re.findall('\.html$', i)]
    _forbidden = [i for b in _html_files for i in all_tags(soup(open(f'jnet_static_folder/{b}').read(), 'html.parser'))]
    _filtered_forbidden = [i for i in _forbidden if all(not _k(i) for _k in _keep)]
    _app_tags = [i for b in os.listdir(f'apps/app_{_app}/templates') for i in all_tags(soup(open(f'apps/app_{_app}/templates/{b}').read(), 'html.parser')) if re.findall('\.html$', b)]
    return [i for i in _app_tags if any(c == i for c in _filtered_forbidden)]
