import telemonius, jinja2, jnet_utilities

with telemonius.Controller('apps') as app:
    @app.action('/')
    def display_apps():
        return telemonius.TelemoniusEnv(open('jnet_static_folder/full_app_listing.html').read())

    @app.action('/create-app')
    def create_app():
        return telemonius.TelemoniusEnv(open('jnet_static_folder/create_app_options.html').read())

    @app.action('/create-app/<fromtype>')
    def display_creation_form(fromtype):
        return telemonius.TelemoniusEnv(jinja2.Template(open('jnet_static_folder/create_app_form.html').read()).render(apptype=fromtype))

    @app.action('/create-app/<fromtype>/submit')
    def get_creation_form_vals(fromtype):
        #print([app[i] for i in ['name', 'description', 'host']])
        _valid = not jnet_utilities.app_exists(app['name'])
        if _valid:
            jnet_utilities.create_app(app['name'], app['description'], app['host'])
        return telemonius.TelemoniusJasonify(success=_valid)