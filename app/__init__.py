from flask import Flask, g, jsonify, render_template

from yamlsettings import YamlSettings

from app.api.notes import NotesView
from app.exceptions import HTTPError
from app.models.notes import Notes


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder='../client/templates',
        static_folder='../client/static')

    app.config.update(
        YamlSettings(
            'app/configs.yml',
            'app/configs.yml',
            default_section='Config'
        ).get_settings())

    @app.before_request
    def before_request():
        g.user_id = 0
#    @app.route('/power')
#    def power():
#        return render_template(
#            'power.html',
#            power_types=POWER_TYPES,
#            power_values=POWER_VALUES)

    NotesView.register(app, route_base='/api/notes')

    @app.route('/')
    def index():
        print 'index'
        note = Notes()
        todays_note = note.get_todays_note()
        if not todays_note:
            return render_template('index.html')
        else:
            return render_template(
                'selected.html',
                color=todays_note.type,
                message=todays_note.note
            )

    @app.route('/selected/<type>')
    def selected(type):
        note = Notes()
        todays_note = note.get_todays_note(type)
        colors = {
            'red': '#FF6666',
            'green': '#559955',
            'blue': '0000FF'
        }
        if todays_note:
            message = todays_note.note
        else:
            message = 'Sorry no note for this color today :('
        return render_template(
            'selected.html',
            color=colors[type],
            message=message,
            has_message=todays_note is not None
        )

    @app.errorhandler(HTTPError)
    def http_error(e):
        error_body = {
            'error': e.message,
        }

        return jsonify(error_body), e.status_code

    return app

app = create_app()
