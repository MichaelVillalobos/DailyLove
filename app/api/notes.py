from flask import jsonify, request
from flask.ext.classy import FlaskView, route

from app.exceptions import HTTPError
from app.objects import Notes


class NotesView(FlaskView):

    @route('/<type>')
    def get_color(self, type):
        return jsonify(Notes().get_color(type))

    def post(self):
        json = request.get_json(silent=True)
        if not json:
            raise HTTPError(400, 'Invalid request type')

        response = Notes().add_note(**json)
        return jsonify(response)

    def put(self):
        json = request.get_json(silent=True)
        if not json:
            raise HTTPError(400, 'Invalid Request Type')

        response = Notes().modify_note(**json)
        return jsonify(response)

    def delete(self):
        json = request.get_json(silent=True)
        if not json:
            raise HTTPError(400, 'Invalid Request Type')

        response = Notes().delete_note(**json)
        return jsonify(response)

    @route('/today/<type>')
    def pop_todays_note(self, type):
        response = Notes().get_todays_note(type)
        return jsonify(response)

    @route('/today')
    def retrieve_todays_note(self):
        response = Notes().get_todays_note()
        return jsonify(response)

    @route('/previous')
    def retrieve_previous_notes(self):
        response = Notes().get_previous_notes()
        return jsonify(response)
