from flask_login import UserMixin
from auth import auth_status, get_user

class User(UserMixin):
    def __init__(self, identifier):
        self._isauthenticated = False
        self._id, self._pwd, self._userdir = get_user(identifier)

    def is_authenticated(self):
        return self._isauthenticated

    def get_id(self):
        return self._id
    
    def authenticate(self, pwd):
        self._isauthenticated = pwd == self._pwd
        return self._isauthenticated


