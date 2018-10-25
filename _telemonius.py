import re, collections, os
import typing, datetime
import jinja2
import os
import sys

script_dir = os.path.dirname(__file__)

import telemonius_routes, telemonius_wrappers

def load_content(f:typing.Callable) -> typing.Callable:
    def __wrapper(_inst, content:str, javascript:typing.Any=None, css:typing.Any = None):
        return f(_inst, content, javascript=javascript if js is None else open(os.path.join(script_dir, f'templates/{js}')).read(), css=css if css is None else open(os.path.join(script_dir, f'templates/{css}')).read())
    return __wrapper

class TelemoniusEnv:
    @load_content
    def __init__(self, _content:str, javascript=None, css=None):
        self.html = _content
        self.js = javascript
        self.css = css
    def __iter__(self):
        yield from [[i, getattr(self, i)] for i in ['html', 'js', 'css']]
    @property
    def response_type(self):
        return 'env'
    def __eq__(self, _val:str) -> bool:
        return self.response_type == _val
    def __repr__(self):
        return f'{self.__class__.__name__}({self.html}, js={self.js}, css={self.css})'

class TelemoniusJasonify:
    def __init__(self, **kwargs):
        self._jsonified_results = kwargs
    @property
    def response_type(self):
        return 'json'
    def __eq__(self, _val:str) -> bool:
        return self.response_type == _val
    def __iter__(self):
        yield from self._jsonified_results.items()

class RouteResponse(typing.NamedTuple):
    route:str
    content:typing.Any
    isredirect:bool

class _telemonius_redirect:
    def __init__(self, _to:str) -> None:
        self._redirect_to = _to

class RoutePacket(typing.NamedTuple):
    route:str
    actions:list
    appname:str

class Controller:
    @telemonius_wrappers.log()
    def __init__(self, name='defaultTelemoniusApp', **kwargs) -> None:
        '''
        kwargs:default session values
        '''
        self.app_name = name
        self.routes = telemonius_routes.Routes()
        self.send_values = telemonius_routes.Forms()
        self.sessions = telemonius_routes.Sessions(kwargs)
    @telemonius_wrappers.log_build
    def __enter__(self):
        if f'{self.app_name}_log.txt' not in os.listdir(os.getcwd()):
            with open(f'{self.app_name}_log.txt', 'a') as f:
                pass
        return self

    def __exit__(self, *args, **kwargs):
        pass

    def __getitem__(self, _key:str) -> typing.Any:
        return self.send_values[_key]

    def __getattr__(self, _key:str) -> typing.Any:
        return self.send_values[_key]

    @classmethod
    def render_page(cls, _page_link, **kwargs):
        """How should we structure template folders?"""
        return jinja2.Template(open(os.path.join(script_dir, f'templates/{_page_link}')).read()).render(**kwargs)


    def redirect(self, _route:str) -> typing.Callable:
        return _telemonius_redirect(_route)

    @telemonius_wrappers.log()
    def on_404(self, _f):
        self.routes._404 = _f

    @telemonius_wrappers.log()
    def on_error(self, _f):
        self.routes._error = _f

    @telemonius_wrappers.log()
    def action(self, route:str, action_types:list=['']) -> typing.Callable:
        def __wrapper(_operation):
            
            self.routes[RoutePacket(route, action_types, self.app_name)] = _operation
            return _operation
                
            return __action_wrapper
            
        return __wrapper

    @telemonius_wrappers.log()
    def build(self, _route:str, _sessions = {}, **kwargs) -> str:
        _route_handler = self.routes[list(filter(None, _route.split('/')))]
        if not _route_handler:
            return getattr(self.routes._404, '__call__', lambda :TelemoniusEnv('<h1>Page Not Found</h1>'))()

    
        try:
            self.send_values.update_form(kwargs)
            self.sessions(_sessions)
            [route_method, action_handler] = _route_handler[0]
            _action_result = action_handler(*route_method())
            if isinstance(_action_result, _telemonius_redirect):
                return RouteResponse(_action_result._redirect_to, self.build(_action_result._redirect_to).content, True)
            return RouteResponse(_route, _action_result, False)    
        except:
            telemonius_wrappers.log_error(_route, self.app_name)
            return getattr(self.routes._error, '__call__', lambda :TelemoniusEnv('<h1>An error occured</h1>'))()  
        
if __name__ == '__main__':
    with Controller("test_app", logged_in = False) as app:
        @app.action('/home')
        def home_route():
            return TelemoniusEnv("<h1>Welcome!</h1>")

        @app.action('/home/users/<calc>')
        def get_vals(val):
            return TelemoniusEnv(Controller.render_page('home_page.html', result=int(val)+10), javascript='stuff.js')

        @app.action('/greet_user')
        def get_name():
            return f'<h1>Hello, {app["firstname"]} {app["lastname"]}</h1>'

        @app.action('/help/info/terms_of_service')
        def display_terms():
            return "<p>All are welcome</p>"

        @app.action('/dashboard')
        def dashboard():
            if not app.sessions['logged_in']:
                return "<h1>you are not logged in</h1>"
            return f'<h1>Hello {app.sessions["username"]}</h1>'

        @app.action('/login')
        def login():
            app.sessions['username'] = app['username']
            app.sessions['password'] = app['password']
            app.sessions['logged_in'] = True
            return f'<h1>Welcome, {app.sessions["username"]}</h1>'

        @app.action('/logout')
        def logout():
            app.sessions.clear_sessions()
            app.sessions['logged_in'] = False
            return app.redirect('/home')

        
        
        @app.action('/register')
        def register_user():
            if app.sessions['logged_in']:
                return "<h1>You are already logged in</h1>"
            return f"<h1>THanks for registering, {app['username']} </h1>"

        @app.on_404
        def display_missing_page():
            return "<h1>Uh oh, that page does not exist</h1>"

        @app.on_error
        def backup_error():
            return "<h1>Sorry, something went wrong on our end</h1>"

        @app.action('/final_stop')
        def get_page():
            return TelemoniusEnv("<h1>Yes! This works</h1>")

        @app.action('/bounce_off')
        def bounce_off():
            return app.redirect('/final_stop')

        @app.action('/test_redirect')
        def test_redirect():
            return app.redirect('/bounce_off')

        @app.action('/test')
        def test():
            return app.redirect('/home')
        
        @app.action('/new_session_action')
        def second_test():
            return f'<h1>{app.sessions["newname"]}</h1>'

        @app.action('/')
        def testing_real_home():
            return '<h1>This is a true home</h1>'
        print(app.build('/login', **{"username":"Ajax1234", "password":"4ras34asd23"}))
        print(app.build('/final_stop'))
        print(app.build('/new_session_action', _sessions={'newname':'Baby2000'}))
        print(app.build('/'))
