import typing, re, itertools

class Forms:
    def __init__(self):
        self._current_values = {}
    def update_form(self, kwargs):
        self._current_values = kwargs
    
    def __getitem__(self, _key):
        return self._current_values[_key]


class Sessions:
    def __init__(self, _initial_values:dict) -> None:
        self._current_values = _initial_values
    @property
    def session(self):
        return self._current_values
    def __contains__(self, _key):
        return _key in self._current_values
    def __getitem__(self, _key):
        return self._current_values[_key]
    def __setitem__(self, _key, _value):
        self._current_values[_key] = _value
    def __call__(self, _new_session:dict) -> None:
        if _new_session:
            self._current_values = _new_session
    def clear_sessions(self):
        self._current_values = {}

class Action:
    def __init__(self, _func:typing.Callable) -> None:
        self._func = _func

    def __call__(self, *args, **kwargs):
        
        return self._func(*args, **kwargs)
        
    def __repr__(self):
        return f'<route action function "{self._func}">'

class _level:
    def __init__(self, level:str):
        self.val = level[1:-1] if level.startswith('<') and level.endswith('>') else level
        self._type = 'user-specified' if level.startswith('<') and level.endswith('>') else 'directory'
    def __str__(self):
        return f'<{self._type} "{self.val}">'
    def __lt__(self, _dir):
        return self.val < _dir.val
    def __bool__(self):
        return self._type == 'directory'
    def __eq__(self, _other_level):
        return self.val == _other_level if self._type == 'directory' else True
    @classmethod
    def cast_to_level(cls, _f):
        pass
    def __repr__(self):
        return f'<{self._type} "{self.val}">'

class Route:
    def __init__(self, _string_route:str, template=None) -> None:
        self._route = _string_route
        self.template_route = template
    def __bool__(self) -> bool:
        '''determines if route is home ("/") route'''
        return not self.route
    def __call__(self) -> typing.List[str]:
        return [b for a, b in zip(self, self.template_route) if not a]
    def __len__(self):
        return len(self.route)
    def __eq__(self, _new_route):
        return len(self) == len(_new_route) and all(c ==d for c, d in zip(self, _new_route))
    def __getitem__(self, _val:int):
        return _level(self._route[_val])
    def __iter__(self):
        yield from self.route
    @property
    def route(self):
        return [_level(i) for i in filter(None, self._route.split('/'))]
    def __repr__(self):
        return '/'.join(str(i) for i in self.route)
    def __str__(self):
        return repr(self)

class Routes:
    def __init__(self) -> None:
        self.app_name = None
        self._full_routes = {}
        self.on_page_missing = None
        self.on_error = None

    def create_tree(self) -> dict:
        def combine_dicts(d1:list) -> dict:
            return {a:(lambda x:[i for [i] in x] if all(len(i) == 1 for i in x) else combine_dicts(x))([c for _, *c in b]) for a, b in itertools.groupby(sorted(d1, key=lambda x:x[0]), key=lambda x:x[0])}

        return combine_dicts([[*a, b] for a, b in self._full_routes.items()])

    def __getitem__(self, _input_route):
        return [[Route(a, template=_input_route), b] for a, b in self._full_routes.items() if Route(a) == _input_route]

    @property
    def _404(self):
        return self.on_page_missing
    @property
    def _error(self):
        return self.on_error
    @_error.setter
    def _error(self, _action):
        self.on_error = Action(_action)
    @_404.setter
    def _404(self, _action):
        self.on_page_missing = Action(_action)
    def __setitem__(self, _packet:typing.NamedTuple, _func:typing.Callable) -> None:
        self.app_name = _packet.appname      
        self._full_routes[_packet.route] = Action(_func)

