from flask import Flask, render_template, request
import database_utils as db
import userfiles_utils as ufile
from passlib.hash import sha256_crypt
import uuid


app = Flask(__name__)

@app.route('/')
def serve_login_page():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
    	table_name = 'userinfo'
    	if 'nick' in request.form:
    		
    		bucket_name = str(uuid.uuid4())
    		values = {'userid': request.form['username'],
    					'passwd': request.form['password'],
    					'userdir': bucket_name}
    		# Registration
    		db.write_to_db(db.cursor, table_name, values)
    		print("Creating bucket with id {}".format(bucket_name))
    		ufile.create_bucket(bucket_name)
    		return render_template('index.html')
    	else:
    		# Login
    		email_info = {'userid': request.form['username']}
    		user_info = db.read_db(db.cursor, table_name, email_info)[0]
    		if user_info['passwd'] == request.form['password']:
    			return "Login Successful"
    		else:
    			return "Login UnSuccessful"

    	# user, pwd = request.form['username'], request.form['password']
    	# return user+' '+pwd

if __name__ == '__main__':
    app.run(debug='True')
    # pass
