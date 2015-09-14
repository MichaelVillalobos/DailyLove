import json
import pytz
from datetime import datetime, time

from flask import g
from flask import current_app
from redis import StrictRedis

from app.exceptions import HTTPError


class Notes(object):

    def __init__(self):
        # initialize redis here
        redis_args = {
            'host': current_app.config['redis']['host'],
            'password': current_app.config['redis']['password'],
            'port': current_app.config['redis']['port']
        }
        self.redis = StrictRedis(**redis_args)

        self.keys = {
            'red': 'red:{user_id}'.format(user_id=g.user_id),
            'blue': 'blue:{user_id}'.format(user_id=g.user_id),
            'green': 'green:{user_id}'.format(user_id=g.user_id)
        }
        self.check_keys = {
            'red': 'red:{user_id}:lcase'.format(user_id=g.user_id),
            'blue': 'blue:{user_id}:lcase'.format(user_id=g.user_id),
            'green': 'green:{user_id}:lcase'.format(user_id=g.user_id)
        }

        self.todays_note_key = '{user_id}:notes:{date}'.format(
            user_id=g.user_id, date=datetime.combine(
                datetime.now(pytz.timezone('US/Pacific')).date(), time())
            .strftime('%y%m%d'))

        self.previous_notes_key = '{user_id}:notes:*'.format(
            user_id=g.user_id)

    def get_notes_count(self):
        with self.redis.pipeline() as pipe:
            pipe.scard(self.keys['red'])
            pipe.scard(self.keys['blue'])
            pipe.scard(self.keys['green'])
            results = pipe.execute()
        return {'red': results[0], 'blue': results[1], 'green': results[2]}

    def get_color(self, type):
        if type in self.keys:
            notes = self.redis.smembers(self.keys[type])
            return notes
        else:
            return []

    def add_notes(self, notes):
        with self.redis.pipeline() as pipe:
            for type, note_list in notes.iteritems():
                for note in note_list:
                    pipe.sadd(self.keys[type], note)
                    pipe.sadd(self.check_keys[type], note.lower())
            pipe.execute()

    def validate_notes(self, notes):
        checked_notes = []
        with self.redis.pipeline() as pipe:
            for type, note_list in notes.iteritems():
                for note in note_list:
                    if type in self.keys:
                        checked_notes.append(note)
                        pipe.sismember(self.check_keys[type], note.lower())
                    else:
                        raise HTTPError(403, 'invalid note type')
            results = pipe.execute()
        err_notes = []
        for i, result in enumerate(results):
            if result == 1:
                err_notes.append(checked_notes[i])
        if err_notes:
            err_message = "Some notes already exist."
            raise HTTPError(403, {'message': err_message, 'notes': err_notes})

    def modify_note(self, type, old_note, new_note):
        if type in self.keys:
            if not self.redis.sismember(self.keys[type], new_note):
                self.delete_note(type, old_note)
                self.add_note(type, new_note)
            else:
                return {'result': 'error', 'err': 'message already in key'}
        else:
            raise HTTPError(403, 'invalid note type')

    def delete_note(self, type, note):
        if type in self.keys:
            self.redis.srem(self.keys[type], note)
            self.redis.srem(self.check_keys[type], note.lower())
            return {'result': 'success'}
        else:
            raise HTTPError(403, 'invalid note type')

    def get_todays_note(self, type=None):
        if not self.redis.exists(self.todays_note_key):
            if not type:
                return None
            note = self.redis.spop(self.keys[type])
            if note:
                note_value = {
                    'note': note,
                    'type': type
                }
                self.redis.set(self.todays_note_key, json.dumps(note_value))
                self.delete_note(type, note)
                return Note(**note_value)
            else:
                return None
        else:
            note = self.redis.get(self.todays_note_key)
            return Note(**json.loads(note))

    def get_previous_notes(self):
        previous_keys = self.redis.keys(self.previous_notes_key)
        previous_notes = self.redis.mget(previous_keys)
        return previous_notes


class Note(object):
    def __init__(self, note, type):
        self.note = note
        self.type = type
