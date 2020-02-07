# WRAPPER FOR AUTH FUNCTIONS
import db

def get_user(user):
    cur = db.get_cursor()
    query = "SELECT * FROM USERINFO WHERE USERID = '%s'"
    res = db.exec_query(query % user, cur)
    if res is None:
        return None
    else:
        return res[0] 
    

def auth_status(user, pwd):
    cur = db.get_cursor()
    query = "SELECT PASSWD FROM USERINFO WHERE USERID = '%s'"
    res = db.exec_query(query % user, cur)
    if res is not None:
         return res[0][0] == pwd 
    else:
        return 0


