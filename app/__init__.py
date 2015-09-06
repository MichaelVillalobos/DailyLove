from flask import Flask, g, render_template

from app.api.notes import NotesView
from .objects import Notes


def create_app(config=None):
    app = Flask(
        __name__,
        template_folder='client/templates',
        static_folder='client/static')

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
        note = Notes()
        todays_note = note.get_todays_note()
        if not todays_note:
            return render_template('index.html')
        else:
            return render_template(
                'selected.html',
                color=note.type,
                message=note.note
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
            message=message
        )

    return app

app = create_app()
