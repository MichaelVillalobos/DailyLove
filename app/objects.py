from datetime import datetime

from flask import g, jsonify
from redis import StrictRedis

from .exceptions import HTTPError


class Notes(object):

    def __init__(self):
        # initialize redis here
        redis_args = {
            'host': 'pub-redis-14032.us-east-1-1.1.ec2.garantiadata.com',
            'password': '#P5958401',
            'port': 14032
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
            user_id=g.user_id, date=datetime.today().strftime('%y%m%d'))

        self.previous_notes_key = '{user_id}:notes:*'.format(
            user_id=g.user_id)

    def get_color(self, type):
        if type in self.keys:
            notes = self.redis.smembers(self.keys[type])
            return notes
        else:
            return []

    def add_note(self, type, note):
        if type in self.keys:
            if not self.redis.sismember(self.check_keys[type], note.lower()):
                self.redis.sadd(self.keys[type], note)
                self.redis.sadd(self.check_keys[type], note.lower())
                return {'result': 'success'}
            else:
                return {'result': 'error', 'err': 'message already in key'}
        else:
            raise HTTPError(403, 'invalid note type')

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
                self.redis.set(self.todays_note_key, jsonify(note_value))
                self.redis.delete_note(note)
                return note
            else:
                return None
        else:
            return self.redis.get(self.todays_note_key)

    def get_previous_notes(self):
        previous_keys = self.redis.keys(self.previous_notes_key)
        previous_notes = self.redis.mget(previous_keys)
        return previous_notes
