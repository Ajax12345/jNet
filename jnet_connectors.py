import internal_morpheus as morpheus
import re, jnet_utilities, json, requests
import datetime, typing, tigerSqlite


class ResponseTypes:
    class jNetEnv:
        def __eq__(self, _val:[int, str]) -> bool:
            if isinstance(_val, int):
                return self.int_name == _val
            return self.name_type == _val
        @property
        def name_type(self):
            return 'env'
        @property
        def int_name(self):
            return 2

    class jnetJson:
        def __eq__(self, _val:[int, str]) -> bool:
            if isinstance(_val, int):
                return self.int_name == _val
            return self.name_type == _val
        @property
        def name_type(self):
            return 'json'
        @property
        def int_name(self):
            return 1
    

class BrowserResponse:
    def __init__(self, response_type, **kwargs):
        self.response_type = response_type
        self.__dict__.update(kwargs)
    @staticmethod
    @jnet_utilities.get_attrs
    def join_path(url_obj:str, response_obj:str) -> str:
        return re.findall('^\w+:@\w+', url_obj)[0] + response_obj
    @classmethod
    def _to_browser_response(cls, server_response_type, _returned_payload:dict, on_error = False) -> typing.Callable:
        print('returned payload here', _returned_payload)
        if server_response_type == 'json':
            return cls(server_response_type, **{'isredirect':_returned_payload['is_redirect'], 'route':_returned_payload['route'], 'payload':_returned_payload['payload']})
        return cls(server_response_type, **({'payload':ReadFrom(html='url_name_error.html', js=None, css=None), 'is_error':True} if on_error else {'isredirect':_returned_payload['is_redirect'], 'route':_returned_payload['route'], 'payload':ReadFrom(html='on_response.html', js=_returned_payload['payload']['js'], css=_returned_payload['payload']['css'])}))
        #ReadFrom(html='on_response.html', js=_server_result['js'], css=_server_result['css'])

class ErrorSiteLookup:
    def __init__(self, bad_url:str) -> None:
        self.faulty_url = bad_url
        self.occurance = datetime.datetime.now()

class ReadFrom:
    def __init__(self, html = 'on_response.html', js='on_response.js', css='on_response.css'):
        self.html, self.js, self.css = html, js, css
    def __repr__(self):
        return f'{self.__class__.__name__}(html={self.html}, css={self.css}, js={self.js})'

class ServerLookupResponse:
    def __init__(self, _full_data:dict):
        self.__dict__ = _full_data
    @property
    def last_updated(self):
        return datetime.datetime(*map(int, self.updated.split()))
    @property
    def live_port(self):
        return int(self.port)

class jNetUrl:
    def __init__(self, _url:str) -> None:
        self._original_url = _url
        self.server, self.app_name = re.findall('^\w+(?=:@)|(?<=@)\w+(?=/)|(?<=@)\w+$', _url)
        self.path = re.sub('^\w+:@\w+', '', _url)
    def __repr__(self):
        return f'<URL: server={self.server}, appname={self.app_name}, path={self.path}>'

def lookup_site(url:str) -> dict:
    try:
        parsed_url = jNetUrl(url)
        full_location = ServerLookupResponse(json.loads(requests.get(jnet_utilities.server_loc(parsed_url.server)+f'app_stats/{parsed_url.app_name}').text))
    except:
        return ErrorSiteLookup(url), None
    else:
        return full_location, parsed_url



@jnet_utilities.terminate_delay(1)
def connect_hosting_node(_ip, app_name):
    try:
        with morpheus.Client(_ip, 8423) as c:
            r = c.send_data({'request-type':0, 'payload':{'app':app_name}})
            if r['contains_app']:
                return _ip
    except:
        return 'failed'
        

def find_lan_hosting_node(appname) -> typing.Any:
    for i in morpheus._lanOptions():
        print(i)
        try:
            _r = connect_hosting_node(i, appname)
        except:
            pass
        else:
            if _r != 'failed':
                return _r  
    for r in range(1, 4):
        for i in ['192', '172', '10']:
            for _ip in morpheus.LanIps(i, r):
                try:
                    _r = connect_hosting_node(_ip, appname)
                except:
                    pass
                else:
                    if _r != 'failed':
                        return _r
    


@jnet_utilities.log_history
def request_site_data(site_lookup, parsed_url, _tab_info, request_response_type, update=False, forms={}):
    print('in here')
    target_node = site_lookup.ip if site_lookup.ip != site_lookup.sender_ip else find_lan_hosting_node(parsed_url.app_name)
    print('got target node:', target_node)
    if target_node is None:
        return_error_result = None
        if request_response_type == 'env':
            with open('jnet_static_folder/url_name_error.html', 'w') as f:
                f.write(open('url_name_error_template.html').read().format(parsed_url._original_url))
            if update:
                #num real, ip text, app text, url text, path text, session text
                tigerSqlite.Sqlite('browser_settings/browser_tabs.db').update('tabs', [['ip', None], ['app', None], ['url', parsed_url._original_url], ['path', None], ['session', {}]], [['num', _tab_info.tabid]])
            else:
                tigerSqlite.Sqlite('browser_settings/browser_tabs.db').insert('tabs', ('num', _tab_info.tabid), ('ip', None), ('app', None), ('url', parsed_url._original_url), ('path', None), ('session', {}))
            return_error_result = BrowserResponse._to_browser_response(request_response_type, None, on_error=True)
        else:
            return_error_result = {'status':'url name error'.replace(' ', '_').upper()}
        return return_error_result
 
    print('target node', target_node)
    session = {} if not update else jnet_utilities.get_session(_tab_info.tabid)
    '''
    session = {}
    if update:
        session = jnet_utilities.get_session(_tab_info.tabid)
    '''
    try:
        with morpheus.Client(target_node, 8423) as client:
            _server_result = client.send_data({"request-type":1, 'payload':{'app':parsed_url.app_name, 'server':parsed_url.server, 'path':parsed_url.path, 'session':session, 'sender':jnet_utilities.get_full_username(), 'forms':forms}})
    except:
        if request_response_type == 'env':
            with open('jnet_static_folder/url_name_error.html', 'w') as f:
                f.write(open('url_name_error_template.html').read().format(parsed_url._original_url))
            if update:
                #num real, ip text, app text, url text, path text, session text
                tigerSqlite.Sqlite('browser_settings/browser_tabs.db').update('tabs', [['ip', None], ['app', None], ['url', parsed_url._original_url], ['path', None], ['session', {}]], [['num', _tab_info.tabid]])
            else:
                tigerSqlite.Sqlite('browser_settings/browser_tabs.db').insert('tabs', ('num', _tab_info.tabid), ('ip', None), ('app', None), ('url', parsed_url._original_url), ('path', None), ('session', {}))
            return BrowserResponse._to_browser_response(request_response_type, None, on_error=True)
            
        return {'status':'url name error'.replace(' ', '_').upper()}
    
    if request_response_type == 'json':
        if update:
            tigerSqlite.Sqlite('browser_settings/browser_tabs.db').update('tabs', [['ip', site_lookup.ip], ['app', parsed_url.app_name], ['url', BrowserResponse.join_path(parsed_url, _server_result)], ['path', _server_result['route']], ['session', _server_result['session']]], [['num', _tab_info.tabid]])
        else:
            tigerSqlite.Sqlite('browser_settings/browser_tabs.db').insert('tabs', ('num', _tab_info.tabid), ('ip', site_lookup.ip), ('app', parsed_url.app_name), ('url', BrowserResponse.join_path(parsed_url, _server_result)), ('path', _server_result['route']), ('session', _server_result['session']))
        return BrowserResponse._to_browser_response(request_response_type, _server_result)
        


    with open('jnet_static_folder/on_response.html', 'w') as f:
        f.write(_server_result['payload']['html'])
    if _server_result['payload']['js']:
        with open('jnet_static_folder/on_response.js', 'w') as f:
            f.write(_server_result['payload']['js'])
        
    if _server_result['payload']['css']:
        with open('jnet_static_folder/on_response.css', 'w') as f:
            f.write(_server_result['payload']['css'])

    if update:
        tigerSqlite.Sqlite('browser_settings/browser_tabs.db').update('tabs', [['ip', site_lookup.ip], ['app', parsed_url.app_name], ['url', BrowserResponse.join_path(parsed_url, _server_result)], ['path', _server_result['route']], ['session', _server_result['session']]], [['num', _tab_info.tabid]])

    else:
        tigerSqlite.Sqlite('browser_settings/browser_tabs.db').insert('tabs', ('num', _tab_info.tabid), ('ip', site_lookup.ip), ('app', parsed_url.app_name), ('url', BrowserResponse.join_path(parsed_url, _server_result)), ('path', _server_result['route']), ('session', _server_result['session']))
    
    return BrowserResponse._to_browser_response(request_response_type, _server_result)
    
def get_site_resources(tab:int, url:str, request_response_type, forms={}) -> typing.NamedTuple:
    _tab = jnet_utilities.find_tab(tab)
    current_site, parsed = lookup_site(url)
    if isinstance(current_site, ErrorSiteLookup) or not current_site.found:
        if request_response_type == 'env':
            with open('jnet_static_folder/url_name_error.html', 'w') as f:
                f.write(open('jnet_static_folder/url_name_error_template.html').read().format(url))
            tigerSqlite.Sqlite('browser_settings/browser_tabs.db').insert('tabs', ('num', tab), ('ip', None), ('app', None), ('url', url), ('path', None), ('session', {}))
            return ReadFrom(html='url_name_error.html', js=None, css=None)
            #num real, ip text, app text, url text, path text, session text
        tigerSqlite.Sqlite('browser_settings/browser_tabs.db').insert('tabs', ('num', tab), ('ip', None), ('app', None), ('url', url), ('path', None), ('session', {}))
        return {'status':'url name error'.replace(' ', '_').upper()}
        
    return request_site_data(current_site, parsed, _tab, request_response_type, update=bool(_tab), forms=forms)
    

def lookup_tab(tab:int, request_response_type, forms={}) -> typing.Callable:
    _tab = jnet_utilities.find_tab(tab)
    if not any(getattr(_tab, i) for i in ['siteip', 'appname', 'path']):
        if request_response_type == 'env':
            with open('jnet_static_folder/url_name_error.html', 'w') as f:
                f.write(open('jnet_static_folder/url_name_error_template.html').read().format(_tab.url))
            return ReadFrom(html='url_name_error.html', js=None, css=None)
        return {'status':'url name error'.replace(' ', '_').upper()}
    return get_site_resources(tab, _tab.url, request_response_type, forms=forms)


