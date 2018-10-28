import telemonius, jnet_utilities


with telemonius.Controller('history') as app:
    @app.action('/')
    def home_history():
        return telemonius.TelemoniusEnv(jnet_utilities.jNetHistory.render_history())