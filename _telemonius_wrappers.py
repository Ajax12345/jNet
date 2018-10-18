import os, datetime, typing

class Logging:
    def __init__(self, _route:str, app_name:str) -> None:
        self._route = _route
        self.app_name = app_name
        self._types = {'build':'{}: building route for app "{}"\n', '__init__':'{}: controller for app "{}" initialized\n', 'on_404':'{}: 404 (page missing) error handler added for app "{}"\n', 'on_error':'{}: on-error page handler created for app "{}"\n'}
    def __getitem__(self, _func:typing.Callable) -> str:
        _d = datetime.datetime.now()
        full_timestamp = '/'.join(str(getattr(_d, i)) for i in ['month', 'day', 'year'])+' '+':'.join(str(getattr(_d, i)) for i in ['hour', 'minute', 'second'])
        if self._route is None:
            if _func.__name__ not in self._types:
                return f'{full_timestamp}  app "{self.app_name}": uknown action taken\n'
            return self._types[_func.__name__].format(full_timestamp, self.app_name)
        return f'{full_timestamp}: route "{str(self._route)}" created with action "{_func.__name__}" for app "{self.app_name}"\n'


def log(route_action=None):
    def wrapper(_f):
        def outer(*args, **kwargs):
            with open(f'{args[1]}_log.txt' if _f.__name__ == '__init__' else f'{args[0].app_name}_log.txt', 'a') as f:
                if route_action is None and _f.__name__ == 'action':
                    logger = Logging(args[1], args[0].app_name)
                    f.write(logger[_f])
                else:
                    #print(f'{args[1]}_log.txt' if _f.__name__ == '__init__' else f'{args[0].app_name}_log.txt')
                    logger = Logging(route_action, args[1] if _f.__name__ == '__init__' else args[0].app_name)
                    f.write(logger[_f])
            return _f(*args, **kwargs)
        return outer
    return wrapper

def log_error(route, app_name:str) -> None:
    _d = datetime.datetime.now()
    full_timestamp = '/'.join(str(getattr(_d, i)) for i in ['month', 'day', 'year'])+' '+':'.join(str(getattr(_d, i)) for i in ['hour', 'minute', 'second'])
    with open(f'{app_name}_log.txt', 'a') as f:
        f.write(f'{full_timestamp}: An error occured on route "{route}" in app "{app_name}"')



def log_build(f):
    def wrapper(cls):
        setattr(cls, 'file_set', True)
        return f(cls)
    return wrapper