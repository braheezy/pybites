from flask import Flask, g, current_app, json
from marshmallow import Schema, fields, post_load, validate, EXCLUDE
from app.db import db
from werkzeug.security import generate_password_hash, check_password_hash


class UserDB(object):
    '''User represents the document in the DB and provides access
    to CRUDing all fields.
    '''
    def __init__(self, username, password=None, rooms=[]):
        self.username = username
        self._password = password
        self.rooms = rooms

        # We set owner here because we didn't want to store owner
        # field in DB, as it's redundant with username field and we
        # don't plan on supporting acting on roooms if user isn't the
        # username.
        for room in self.rooms:
            room.owner = username
        print("User done __init__", self.rooms, type(self.rooms))

        self.room_schema = RoomSchema()

    def delete_user(self):
        '''Delete self from DB.
        '''
        return db.delete({"username": self.username}) == 1

    @property
    def password(self):
        return self._password

    @password.setter
    def password(self, new_password):
        '''Set/Update password in DB.
        Use set_password() below to initial create the password
        '''
        self._password = generate_password_hash(new_password)

    # rooms are a list of app-specific objects, so we use don't user properties
    # TODO: Yet?
    def get_room(self, name):
        '''Using a generator plus next to avoid creating the intermediate list
        and avoid the ugly "[0]" call. 

        We supply a default of None if the room is not found.
        '''
        return next((r for r in self.rooms if r.name == name), None)

    def add_room(self, name, stuff):
        ''' A wrapper for RoomDB's constructor
        @param name: str
        @param stuff: dict
        '''
        room = None
        print("add room stuff", stuff)
        stuff = dict() if stuff is None else stuff
        room = RoomDB(name, self.username, stuff)

        print(room)

        # Dump rooms for db to handle
        room = self.room_schema.dump(room)
        print('room added, adding to db', room)
        return db.update({'username': self.username},
                         {"$push": {
                             "rooms": room
                         }})

    def remove_room(self, room=None):
        '''Delete room(s) from DB.

        @param room: name(s) of room to delete
        '''
        res = None
        if room is None:
            # Delete all rooms
            res = db.update({"username": self.username},
                            {"$set": {
                                "rooms": []
                            }})
        else:
            # Because of $pull, all rooms with this name will be deleted.
            # Client should take care of enforcing unique names.
            room = room if isinstance(room, list) else [room]
            print("remove these rooms", room)
            res = db.update({"username": self.username},
                            {"$pull": {
                                "rooms": {
                                    "name": {
                                        "$in": room
                                    }
                                }
                            }})

        return res

    @classmethod
    def find_user(cls, username):
        usr = db.find({'username': username})
        print('usr found:', usr)
        if usr:
            return UserSchema().load(usr)
        return None

    def check_password(self, password):
        # print('checking {} to {} or {}'.format(
        #     self.password, password, generate_password_hash(password)))
        return check_password_hash(self._password, password)

    def __repr__(self):
        return f'<UserDB {self.username}>'


class RoomDB(object):
    '''A RoomDB provides deeper DB access to CRUD rooms directly 
    '''
    def __init__(self, name, owner=None, stuff=dict()):
        # stuff: A dict of items: {item: price}
        # owner: not used in DB
        self.name = name
        self.stuff = stuff
        self.room_schema = RoomSchema()

        # Not stored in DB because it's redundant right now.
        self.owner = owner

    def change_name(self, new_name):
        '''Update room name in DB.

        Does not preserve item placement in DB's room array.
        '''
        # TODO: Do this in one DB operation?
        # Mongo does not support $rename on embedded doc in array.
        # Instead, $pull the old room and $push the new one
        db.update({"username": self.owner},
                  {"$pull": {
                      "rooms": {
                          "name": self.name
                      }
                  }})

        self.name = new_name
        db.update({'username': self.owner},
                  {"$push": {
                      "rooms": RoomSchema().dump(self)
                  }})

    def update_stuff(self, changes):
        '''Add/Update stuff for this room in DB.
        @param changes: dict mapping old items to new.

        {
            "item": {
                "name": "item_name",
                "value": "item_value"
            },
        }
        name or value may not null, indicating no update
        '''
        selector = {"username": self.owner, "rooms.name": self.name}

        # Build cmd based on requested changes
        set_cmd = {"$set": dict()}
        unset_cmd = {"$unset": dict()}
        arr_filter = [{"element.name": self.name}]
        print("current stuff: ", self.stuff)

        for key, change in changes.items():
            # print(f"key: {key}, change: {change}")
            # otherwise, a new item
            if change.get("name") and change.get("value"):
                # Set, or possibly replace, item.
                if key in self.stuff.keys():
                    # Remove current item
                    unset_cmd["$unset"]["rooms.$[element]" + ".stuff." +
                                        key] = ""

                set_cmd["$set"]["rooms.$[element]" + ".stuff." +
                                change["name"]] = change["value"]
            elif change.get("name"):
                # Update item name.
                set_cmd["$set"]["rooms.$[element]" + ".stuff." +
                                change["name"]] = self.stuff[key]
                unset_cmd["$unset"]["rooms.$[element]" + ".stuff." + key] = ""
            elif change.get("value"):
                # Update item value.
                set_cmd["$set"]["rooms.$[element]" + ".stuff." +
                                key] = change["value"]

        print("unset_cmd", unset_cmd)
        print("set_cmd", set_cmd)
        print("selector", selector)

        if len(unset_cmd["$unset"]) > 0:
            db.update(selector, unset_cmd, array_filters=arr_filter)
        return db.update(selector, set_cmd, array_filters=arr_filter)

    def remove_stuff(self, items=None):
        '''Remove items from stuff in this room in DB.

        @param items: List of names to delete
                      None: Delete all stuff
        '''
        if items:
            # Array of item(s) to delete
            update_cmd = {"$unset": dict()}
            for item in items:
                update_cmd["$unset"]["rooms.$[element].stuff." + item] = ""
            print("del stuff update cmd", update_cmd)
            return db.update({"username": self.owner},
                             update_cmd,
                             array_filters=[{
                                 "element.name": self.name
                             }])
        else:
            # Delete all stuff
            return db.update({"username": self.owner},
                             {"$set": {
                                 "rooms.$[element].stuff": {}
                             }},
                             array_filters=[{
                                 "element.name": self.name
                             }])

    def __repr__(self):
        return f'<RoomDB {self.name} has {len(self.stuff)} stuff.>'


class RoomSchema(Schema):
    name = fields.Str()
    stuff = fields.Dict(keys=fields.Str(),
                        values=fields.Str(),
                        allow_none=True)

    @post_load
    def make_room(self, data, **kwargs):
        print('loading room into Class', data, kwargs)
        return RoomDB(**data)


class UserSchema(Schema):
    username = fields.Str(required=True)
    password = fields.Str()
    rooms = fields.List(fields.Nested(RoomSchema), allow_none=True)

    @post_load
    def make_user(self, data, **kwargs):
        print('loading user into Class', data, kwargs)
        return UserDB(**data)

    class Meta:
        unknown = EXCLUDE


# Framework and internet recommended way of handling blacklisted
# tokens, those that should no longer be given access.
class BlacklistToken(object):
    def __init__(self, jti):
        self.jti = jti

    def add(self):
        db.create({'jti': self.jti}, 'jwt_tokens')

    @classmethod
    def is_jti_blacklisted(cls, jti):
        res = db.find({'jti': jti}, 'jwt_tokens')
        return bool(res)