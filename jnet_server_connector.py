import os, re, typing
import json, jnet_utilities, pickle

def matching_app(_folder:str, _name:str, live=True) -> bool:
    with open(f'apps/{_folder}/app_config.json') as f:
        data = json.load(f)
    
    return re.sub('^app_', '', _folder) == _name and (True if not live else data['live'])

def request_0(_payload:dict) -> typing.Dict[str, bool]:
    '''checks if resource contains app'''
    return {'request-type':0, 'contains_app':any(matching_app(i, _payload['app']) for i in os.listdir('apps') if re.findall('^app_', i))}


@jnet_utilities.log_view
def request_1(_payload:dict) -> dict:
    import apps
    _app_inst = getattr(apps, f'app_{_payload["app"]}').app_routes.app
    _framework_results = _app_inst.build(_payload['path'], _sessions = _payload['session'], **_payload['forms'])
    return {'session':_app_inst.sessions.session, 'response-type':[1, 2][_framework_results == 'env'], 'payload':_framework_results._jsonified_results if _framework_results == 'json' else {i:getattr(_framework_results, i) for i in ['html', 'css', 'js']}}
