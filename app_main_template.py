import os
import sys

file_dir = os.path.dirname(__file__)
sys.path.append(file_dir)


import telemonius
with telemonius.Controller("{}") as app:
    @app.action('/')
    def home_route():
        return telemonius.TelemoniusEnv(telemonius.Controller.render_page('home.html'))