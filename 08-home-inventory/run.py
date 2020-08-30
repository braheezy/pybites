from app import create_app
from app.db import db
from app.main.models import UserDB, RoomDB

app = create_app()
'''
'flask shell' can be used to launch a shell with the application
already imported, avoiding tedious retyping of 'import app'
when using the interpreter.
This decorator registers this function. When 'flask shell' is
run, it invokes this function and essentially imports
these items for use.
'''


@app.shell_context_processor
def make_shell_context():
    return {'db': db, 'UserDB': UserDB, 'RoomDB': RoomDB}
