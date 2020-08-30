from flask import render_template, jsonify, request
from app.main.models import UserDB, RoomDB, BlacklistToken, UserSchema, RoomSchema
from flask_restful import Resource, reqparse
from app.db import db
from pymongo.errors import DuplicateKeyError
from flask_jwt_extended import (create_access_token, create_refresh_token,
                                jwt_required, jwt_refresh_token_required,
                                get_jwt_identity, get_raw_jwt)

# For better serialization and stuff
user_schema = UserSchema()

PARSE_ERROR = -1
PARSE_ERROR_MSG = {'error': 'parse req err'}, 500
# TODO: Could this all be in a custom RequestParser class?
# TODO: Parsers can inherit from each other. See flask restful docs.

user_parser = reqparse.RequestParser()
user_parser.add_argument('username')


def fetch_user_args():
    try:
        return user_parser.parse_args()
    except Exception as err:
        print('USERS parse req err', err)
        return PARSE_ERROR


# TODO: Could this all be in a custom RequestParser class?
# Like argparse, but for requests to these Resources.
auth_parser = reqparse.RequestParser()
auth_parser.add_argument('username',
                         help='This field cannot be blank',
                         required=True)
auth_parser.add_argument('password',
                         help='This field cannot be blank',
                         required=True)


def fetch_auth_args():
    try:
        return auth_parser.parse_args()
    except Exception as err:
        print('AUTH parse req err', err)
        return PARSE_ERROR


room_parser = reqparse.RequestParser()
room_parser.add_argument('owner',
                         help='This field cannot be blank',
                         required=True,
                         location='args')
room_parser.add_argument('room_name', location='args')
room_parser.add_argument('stuff', location='args')


def fetch_room_args():
    url_args = None
    json_data = None
    try:
        url_args = room_parser.parse_args()
        json_data = request.get_json()
        print('fetch_room_args got', url_args, json_data)
        # room_name arg could be None or strings, that may to be be split
        # into a list
        if url_args['room_name']:
            url_args['room_name'] = url_args['room_name'].split(",")
            # Most callers don't want an array of 1 item
            if len(url_args['room_name']) == 1:
                url_args['room_name'] = url_args['room_name'][0]
    except Exception as err:
        print('ROOM parse req err', err)
        return (PARSE_ERROR, )

    return url_args, json_data


class Users(Resource):
    '''
    GET
        Read info for 1 or all Users.
    
    DELETE
        Remove 1 or all Users.
    '''
    def get(self):
        url_args = fetch_user_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        uname = url_args.get('username')
        msg = None
        # Get all users or 1 user?
        if uname:
            # Create User-DB interface, if they exist.
            u = UserDB.find_user(uname)

            # Get from DB
            if u and u.username:
                return user_schema.dump(u), 200
            else:
                msg = {'error': 'could not find ' + str(u)}, 404
        else:
            # Basically a full pull on the DB, so no interface.
            # TODO: Add projection to hide things, like password hash
            cursor = db.find_all({})
            users = []
            for doc in cursor:
                users.append(user_schema.dump(doc))
            msg = users, 200

        return msg

    def delete(self):
        url_args = fetch_user_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        uname = url_args.get('username')
        msg = None
        # Delete all users or this user?
        # TODO: Control who can delete all users.
        if uname:
            # Create User-DB interface
            u = UserDB(uname)
            if u.delete_user():
                msg = {'success': 'deleted user ' + u.username}, 200
            else:
                msg = {'error': 'failed to delete user ' + u.username}, 500
        else:
            db.drop()
            msg = {'message': 'deleted all users'}, 200

        return msg


class Room(Resource):
    '''
    All assume User exists and all actions are performed on 
    this User.

    POST
        Add 1 new room, with or without stuff.
    
    DELETE
        Remove 1, many, or all rooms.
    
    PATCH
        Update 1 room name.
    '''
    def post(self):
        '''Adding a room
        '''
        url_args, json_data = fetch_room_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        u = UserDB.find_user(url_args['owner'])
        if not u:
            return {
                'error': 'User {} doesn\'t exist'.format(url_args['owner'])
            }, 500

        msg = None
        if u.add_room(url_args['room_name'], json_data):
            msg = {'success': url_args['room_name'] + ' added!'}, 200
        else:
            msg = {"error": "failed to add room"}, 500

        return msg

    def delete(self):
        url_args, json_data = fetch_room_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        u = UserDB.find_user(url_args['owner'])
        if not u:
            return {
                'error': 'User {} doesn\'t exist'.format(url_args['owner'])
            }, 500

        msg = None
        rooms = url_args['room_name']
        if u.remove_room(rooms):
            if rooms:
                msg = {'success': 'deleted room: ' + " ".join(rooms)}, 200
            else:
                msg = {'success': 'deleted all rooms'}, 200
        else:
            msg = {'error': 'could not deletee room ' + rooms}, 500

        return msg

    def patch(self):
        # Update room name
        room_parser.add_argument('room_name_old',
                                 help='This field cannot be blank',
                                 required=True,
                                 location='args')
        room_parser.add_argument('room_name_new',
                                 help='This field cannot be blank',
                                 required=True,
                                 location='args')
        url_args, json_data = fetch_room_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        old_name = url_args['room_name_old']
        new_name = url_args['room_name_new']
        u = UserDB.find_user(url_args['owner'])
        if not u:
            return {
                'error': 'User {} doesn\'t exist'.format(url_args['owner'])
            }, 500

        room = u.get_room(old_name)
        if not room:
            return {'error': 'Room {} doesn\'t exist'.format(old_name)}, 500

        msg = None
        if room.change_name(new_name):
            msg = {
                f"success': 'Successfully change room name from {old_name} to {new_name}"
            }, 500
        else:
            msg = {'error': 'Could not change room name'}, 500


class Stuff(Resource):
    '''
    All assume Room exists and all actions are performed on 
    this Room.

    POST
        Add/update items.

        This endpoint handles:
            Add: 1 or many items
            Update: 1 or more names, 1 or more values, and
                    1 or more name/value pairs.    
    DELETE
        Remove 1, many, or all items.
    '''
    def post(self):
        url_args, json_data = fetch_room_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        print('Stuff POST', url_args, json_data)
        u = UserDB.find_user(url_args['owner'])

        if not u:
            return {
                'error': 'User {} doesn\'t exist'.format(url_args['owner'])
            }, 500

        msg = None
        # Get the user's room we are modifying
        # This only runs if the user already owns the room.
        room = u.get_room(url_args['room_name'])
        if room and room.update_stuff(json_data):
            msg = {'success': 'Stuff added!'}, 200
        else:
            msg = {"error": "failed to add stuff"}, 500
        return msg

    def delete(self):
        url_args, json_data = fetch_room_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        u = UserDB.find_user(url_args['owner'])
        if not u:
            return {
                'error': 'User {} doesn\'t exist'.format(url_args['owner'])
            }, 500

        msg = None
        # This only runs if the user already owns the room.
        room = u.get_room(url_args['room_name'])
        if room and room.remove_stuff(json_data):
            msg = {'success': 'Stuff delete!'}, 200
        else:
            # return error
            msg = {'error': 'Failed to remove {}'.format(json_data)}, 500
        return msg


'''
*********************************************
AUTH HANDLERS

Uses JWT. Should switch to cookies eventually to support anon Users
and other juicy features.

Flask-jwt-extended defaults these error codes. There are 
decorators available to override this behavior.

    401: token expired
*********************************************
'''


# TODO: Could these be combined?
# POST: Register/Login based on URL arg
# DELETE: Logout, token based on args.
class Register(Resource):
    def post(self):
        url_args = fetch_auth_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        uname = url_args['username']
        msg = None
        # First, does the requested user account exist?
        u = UserDB.find_user(uname)
        if u:
            msg = {'error': 'Username already exists'}, 500
        else:
            # Replace the empty var with a new User
            u = UserDB(uname)
            u.password = (url_args['password'])
            db.create(user_schema.dump(u))
            # JWT stuff
            access_token = create_access_token(identity=uname)
            refresh_token = create_refresh_token(identity=uname)
            msg = {
                'success': uname + ' added!',
                'access_token': access_token,
                'refresh_token': refresh_token
            }, 200
        return msg


class Login(Resource):
    def post(self):
        url_args = fetch_auth_args()
        if url_args == PARSE_ERROR:
            return PARSE_ERROR_MSG

        uname = url_args['username']
        u = UserDB.find_user(uname)
        msg = None
        if not u:
            msg = {'error': 'User {} doesn\'t exist'.format(uname)}
        # same password?
        # print('****', user_schema.load(db_user))
        if u.check_password(url_args['password']):
            access_token = create_access_token(identity=uname)
            refresh_token = create_refresh_token(identity=uname)
            msg = {
                'success': 'Login successful',
                'access_token': access_token,
                'refresh_token': refresh_token
            }
        else:
            msg = {"error": "Login unsuccessful"}
        return msg


class LogoutAccess(Resource):
    @jwt_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            blacklisted_token = BlacklistToken(jti)
            blacklisted_token.add()

            return {'message': 'Access token has been revoked'}, 200
        except:
            return {
                'message': 'Something went wrong with access token on logout'
            }, 500


class LogoutRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        jti = get_raw_jwt()['jti']
        try:
            blacklisted_token = BlacklistToken(jti)
            blacklisted_token.add()
            return {'message': 'Refresh token has been revoked'}, 200
        except:
            return {
                'message': 'Something went wrong with refresh token on logout'
            }, 500


class TokenRefresh(Resource):
    @jwt_refresh_token_required
    def post(self):
        current_user = get_jwt_identity()
        access_token = create_access_token(identity=current_user)
        return {'access_token': access_token}


class TestResource(Resource):
    @jwt_required
    def get(self):
        return {'answer': 42}
