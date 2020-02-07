from flask import Flask, render_template, request, redirect, url_for, flash, Response
import database_utils as db
import userfiles_utils as ufile
from passlib.hash import sha256_crypt
from functools import wraps
from werkzeug import secure_filename
from PyPDF2 import PdfFileReader, PdfFileWriter
import uuid
import os
from datetime import datetime
import logging
import time


import rmv_bck
import sig_dark
import extract_sig
import gc
import merge_sign
import preprop
from generateURL import requestURL

app = Flask(__name__)
app.secret_key = 'super secret key'
ALLOWED_EXTENSIONS = set(['jpg'])
ALLOWED_EXTENSIONS1 = set(['pdf'])
PROJECT_HOME = os.path.dirname(os.path.realpath(__file__))
UPLOAD_FOLDER = '{}/uploads/'.format(PROJECT_HOME)			#path of the uploads
PDF_FOLDER = '{}/static/'.format(PROJECT_HOME)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER					#add key to dictionary of app.config
app.config['PDF_FOLDER'] = PDF_FOLDER


# Temporary
bucket_name = ""
username = ""


#~~~~~~~~~~~~~~~~~~~~~~~ FUNCTION: CHECK IF USER IS LOGGED IN ~~~~~~~~~~~~~~~~~~~~~~~#

def is_logged_in(f):
    @wraps(f)
    def wrap(*args,**kwargs):
          if 'logged_in' in session:
              return f(*args,**kwargs)
          else:
              flash('Unauthorized, Please login','danger')
              return redirect(url_for('login'))
    return wrap


def create_new_folder(path):
	newpath = path
	if not os.path.exists(newpath):
		os.makedirs(newpath)
		return newpath

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/')
def serve_login_page():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    global bucket_name
    global username
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
                bucket_name = user_info['userdir']
                username = user_info['userid']
                return render_template('dashboard.html')
            else:
                return "Login UnSuccessful"

    	# user, pwd = request.form['username'], request.form['password']
    	# return user+' '+pwd

@app.route('/signpdf/', methods=['GET','POST'])
# @is_logged_in
def signpdf():
    if request.method == 'POST':
        docid = request.form['docid']
        print("docid = {}".format(docid))
        docpath = db.read_db(db.cursor, 'docinfo', {'docid': docid})[0]
        docpath = docpath['docpath']
        print(docpath)
        print(docpath.split('/'))
        bucket_name, file_name = docpath.split('/')
        # file_name, file_update = get_bucket_contents(bucket_name, file_name)[0]
        # print(file_name)
        print(file_name)
        if '.pdf' in file_name[-4:]:
            print("inside if")
            cur_pdf = ufile.get_file(bucket_name, file_name)
            in_output = PdfFileWriter()
            for pages in range(cur_pdf.getNumPages()):
                cur_page = cur_pdf.getPage(pages)
                output = PdfFileWriter()
                output.addPage(cur_page)
                in_output.addPage(cur_page)
                # print(os.path.normpath(bucket_name+file_name[:-4]+'_'+str(pages)+'.pdf'))
                # output.write(open(os.path.normpath(app.config['PDF_FOLDER'] + file_name[:-4]+'_'+str(pages)+'.pdf'),"wb"))
                output.write(open(os.path.normpath(app.config['PDF_FOLDER'] + username+'_'+str(pages)+'.pdf'),"wb"))
            # in_output.write(open(os.path.normpath(app.config['PDF_FOLDER'] + file_name[:-4]+'.pdf'),"wb"))
            in_output.write(open(os.path.normpath(app.config['PDF_FOLDER'] + username+'.pdf'),"wb"))


            return redirect(url_for('retrieval', page_no=0))
        else:
        	logging.info('Wrong extension')
        	flash('PDF could not be uploaded (check if format is .pdf or not)','danger')
        	return render_template('signpdf.html')
    return "render_template('signpdf.html')"

@app.route('/retrieval/<page_no>')
# @is_logged_in
def retrieval(page_no=0):
	# print(page_no)
    page_no = int(page_no)
    # global file_names
    # global file_update
    # bucket_name = session["bucket_name"]
    # bucket_name = 'a1edf455-273f-48a6-a2c5-0b056a042e5d'
    print(bucket_name)
    file_name = username + '.pdf'
    file_names = []

    # try:
    #     file_names = session['file_names']
    #     file_update = session['file_update']

    #     logging.info('Using cached data to show')
    #     print('Using OLD DATA')
    # except:
    #     # client.connect()
    #     logging.info('client connected to database')

    #     file_names, file_update = get_bucket_contents(bucket_name)
    #     session['file_names'] = file_names
    #     session['file_update'] = file_update
    #     logging.info('bucket contents retrieved')
        # client.disconnect()


    # pdf_path = os.path.join(app.config['PDF_FOLDER'] , session['username'] + ".pdf")
    # pdf_path = os.path.join(app.config['PDF_FOLDER'] , file_name)
    pdf_file = '/static/'+ file_name[:-4]+'_'+str(page_no)+'.pdf'
    file_names, file_update = ufile.get_bucket_contents(bucket_name)
    # pdf_file = '/static/'+ os.path.normpath(file_name[:-4]+'_'+str(page_no)+'.pdf')
    # if os.path.isfile(os.path.normpath(pdf_path[:-4]+'temp.pdf')):
    	# pdf_path = os.path.normpath(pdf_path[:-4]+'temp.pdf')
    # 	save_path = pdf_path
    # 	pdf.save(save_path)
    # 	cur_pdf = PdfFileReader(open(os.path.normpath(save_path),"rb"))
    # 	for pages in range(cur_pdf.getNumPages()):
    # 		cur_page = cur_pdf.getPage(pages)
    # 		output = PdfFileWriter()
    # 		output.addPage(cur_page)
    # 		output.write(open(os.path.normpath(save_path[:-8]+'_'+str(pages)+'.pdf'),"wb"))
    #     	# print(new_path)#[:-4]+'_out.pdf')
            

    # 	pdf_file = '/static/'+ pdf_path.split('/')[-1][:-8]+'_'+str(page_no)+'.pdf'
    # else:
    # pdf.save(save_path)

    	# os.remove(os.path.normpath(pdf_path[:-8]+'.pdf'))
    	# os.rename(os.path.normpath(pdf_path), os.path.normpath(pdf_path[:-8]+'.pdf'))

    # try:
    print('Inside try MOFO')
    # pdf_file = '/static/'+ pdf_path.split('/')[-1][:-4]+'_'+str(page_no)+'.pdf'
    # pdf_file = '/static/' + session['username'] + '_' + str(page_no) + '.pdf'
    # except Exception as e:
    #     print(e)
    #     print('Inside exception')
    # output = PdfFileWriter()
    # with open(os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'.pdf'),"rb") as f:
    # 	page = PdfFileReader(f).getPage(0)
    # 	output.addPage(page)

    # 	output.write(open(os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'temp.pdf'),"wb"))
    # # del output
    # # print(pdf_file)
    signatures=[]
    for file_name in file_names:
        if ".jpg" in file_name or ".png" in file_name :
            signatures.append({'image': requestURL(bucket_name, file_name),
                                'title': file_name})
    

    # os.remove(os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'.pdf'))
    # os.rename(os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'temp.pdf'), os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'.pdf'))
    #     # pdf_file = requestURL(bucket_name, '1.pdf')
    #     # pdf_file = os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'.pdf')
    
    # pdf_file = os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'.pdf')
    
    print(pdf_file)
    # pdf_file = pdf_path[:-4]+'_'+str(page_no)+'.pdf'
    

    res = {}
    res['pdf'] = pdf_file
    res['signatures'] = signatures
    res['page_no'] = page_no 
    print(res)   

    """Need to display stuff from the Bucket"""
    result=len(signatures)
    if result > 0 :
        return render_template('retrieval.html', res=res)
        #return render_template('dashboard.html',signatures=signatures)
    else:
        msg = "No Signature Found"
        logging.debug('Signature mot Found in Bucket')
        return render_template('dashboard.html',msg=msg)

#~~~~~~~~~~~~~~~~~~~~~~~ ROUTE: merger * route to merge the sign with the pdf *  ~~~~~~~~~~~~~~~~~~~~~~~#

@app.route('/merger', methods=['GET', 'POST'])
# @is_logged_in
def merger():
    details= request.form
    save_path = []
    # bucket_name = 'a1edf455-273f-48a6-a2c5-0b056a042e5d'
    # pdf_path = os.path.join(app.config['PDF_FOLDER'] , session['username'] + ".pdf")
    pdf_path = os.path.join(app.config['PDF_FOLDER'] , username + ".pdf")
    if 'Next' in request.form or 'Previous' in request.form:
        print('IN next')
        print(request.form['Page_Num'])
        for i in range(5):
            print('amn')
            print(details[str(i+1)])
            print('son')
            if details[str(i+1)] != '':
                save_path.append(os.path.join(app.config['PDF_FOLDER'] , details[str(i+1)].split(' ')[0]))
                print('saving path')
                # cos_client.download_file(session['bucket_name'], details[str(i+1)].split(' ')[0], save_path[-1])
                ufile.cos_client.download_file(bucket_name, details[str(i+1)].split(' ')[0], save_path[-1])
                print('downloading image')

                print('sign merged')
                logging.info('Downloaded Dropped Signature from Bucket')
            else:
                print('break if')
                break

        num_pages = merge_sign.place_sign(save_path,pdf_path, details, int(request.form['Page_Num']))
        for path in save_path:
            os.remove(path)
        output = PdfFileWriter()
        filenames = [os.path.normpath(pdf_path[:-4]+'_'+str(i)+'.pdf') for i in range(num_pages)]
        filedata = {filename: open(filename, 'rb') for filename in filenames}
        for more_pages in range(num_pages):
            # f[more_pages] = open(os.path.normpath(pdf_path[:-4]+'_'+str(more_pages)+'.pdf'),"rb")
            page = PdfFileReader(filedata[os.path.normpath(pdf_path[:-4]+'_'+str(more_pages)+'.pdf')]).getPage(0)
            print('added pages')
            output.addPage(page)
        with open(os.path.normpath(pdf_path[:-4]+'.pdf'),"wb") as f:
            output.write(f)
        for file in filedata.values():
            file.close()
        
        print('OH MY GOD WHAT THOU IS HAPPENING')
        if 'Next' in request.form:
            if int(request.form['Page_Num'])+1 <= num_pages-1:
                return redirect(url_for('retrieval', page_no=str(int(request.form['Page_Num'])+1)))
            else:
                flash('Reached the last Page', 'danger')
                return redirect(url_for('retrieval', page_no=str(num_pages-1)))
        elif 'Previous' in request.form:
            if int(request.form['Page_Num'])-1 >= 0:
                return redirect(url_for('retrieval', page_no=str(int(request.form['Page_Num'])-1)))
            else:
                flash('Reached the first Page','danger')
                return redirect(url_for('retrieval', page_no=str(0)))


    if 'Submit' in request.form:
        print('IN submit')
        print(request.form['Page_Num'])
        for i in range(5):
            print('amn')
            print(details[str(i+1)])
            print('son')
            if details[str(i+1)] != '':
                save_path.append(os.path.join(app.config['PDF_FOLDER'] , details[str(i+1)].split(' ')[0]))
                print('saving path')
                ufile.cos_client.download_file(bucket_name, details[str(i+1)].split(' ')[0], save_path[-1])
                print('downloading image')

                print('sign merged')
                logging.info('Downloaded Dropped Signature from Bucket')
            else:
                print('break if')
                break

        num_pages = merge_sign.place_sign(save_path,pdf_path, details, int(request.form['Page_Num']))
        for path in save_path:
            os.remove(path)
        output = PdfFileWriter()
        filenames = [os.path.normpath(pdf_path[:-4]+'_'+str(i)+'.pdf') for i in range(num_pages)]
        filedata = {filename: open(filename, 'rb') for filename in filenames}
        for more_pages in range(num_pages):
            page = PdfFileReader(filedata[os.path.normpath(pdf_path[:-4]+'_'+str(more_pages)+'.pdf')]).getPage(0)
            print('added pages')
            output.addPage(page)
        with open(os.path.normpath(pdf_path[:-4]+'_signed.pdf'),"wb") as f:
            output.write(f)
        for file in filedata.values():
            file.close()
        # del output



        print(request.form)
        key_pdf = 'PDF_'+str(uuid.uuid4())+'.pdf'
        # ufile.upload2bucket(Filename=os.path.normpath(pdf_path[:-4]+'_out.pdf'), Bucket=session['bucket_name'], Key=key_pdf)
        # ufile.upload2bucket(Filename=os.path.normpath(pdf_path[:-4]+'_out.pdf'), Bucket=bucket_name, Key=key_pdf)

        # os.remove(os.path.normpath(pdf_path[:-4]+'_out.pdf'))
        # os.remove(os.path.normpath(pdf_path[:-4]+'.pdf'))
        for pages in range(num_pages):
            os.remove(os.path.normpath(pdf_path[:-4]+'_'+str(pages)+'.pdf'))
        # upload2bucket(Filename=os.path.normpath(pdf_path[:-4]+"_out.pdf"), Bucket=session['bucket_name'], Key=key_pdf)
        # session['file_names'].append(key_pdf)
        # session['file_update'].append(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        # logging.info('Merged PDF uploaded to Bucket')
        # session['pdf_signed'] = key_pdf
        try:
            pdf_name = '1.pdf'
            if pdf_name in session['file_names']:
                index = session['file_names'].index(pdf_name)
                session['file_names'].remove(pdf_name)
                del session['file_update'][index]
                print("FIles deleted fro merger")
            else:
                print('Id not found')
        except Exception as e:
            print(e)
        # delete_item(session['bucket_name'], '1.pdf')
        logging.info('Deleting 1.pdf from Bucket')

        ############################# DELETING THE LOCAL FILE SAVED IN /uploads #############################
        logging.info('Removing all local files')
        # os.remove(pdf_path)
        # os.remove(save_path)
        # os.remove(pdf_path[:-4]+'_out.pdf')
        logging.info('All local files Removed')
        ############################# files will not get deleted if error in between -- maunally clean uploads folder  #############################
        flash('PDF SIGNED','success')
        return redirect(url_for('showpdf'))

@app.route('/showpdf')
# @is_logged_in
def showpdf():
    # bucket_name = session["bucket_name"]
    # bucket_name = 'a1edf455-273f-48a6-a2c5-0b056a042e5d'
    # pdf_file = requestURL(bucket_name, 'PDF_8120d2d6-93b8-4dc5-a973-3ad8a3472aa7.pdf')
    # pdf_file = '/static/' + session['username'] + '_out.pdf'
    pdf_file = '/static/' + username + '_signed.pdf'


    """Need to display stuff from the Bucket"""
    return render_template('showpdf.html', pdf_file=pdf_file)

@app.route('/mysignatures')
# @is_logged_in
def mysignatures():
    #get the signatures for the sessions username

    # bucket_name = session["bucket_name"]
    # bucket_name = 'a1edf455-273f-48a6-a2c5-0b056a042e5d'
    logging.info('client connected to database')

    file_names, file_update = ufile.get_bucket_contents(bucket_name)
    # file_names, file_update = get_bucket_contents(bucket_name, 'img_1')

    # session['file_names'] = file_names
    # session['file_update'] = file_update
    logging.info('bucket contents retrieved')
    # client.disconnect()

    signatures=[]
    count = 0
    for file_name in file_names:
        if ".jpg" in file_name or ".png" in file_name:

            signatures.append({'image': requestURL(bucket_name, file_name),
                                'id': file_name, 'title': count+1,
                                'timestamp': str(file_update[file_names.index(file_name)]).split('.')[0]})
            count+=1
        logging.debug(file_name)
        # print( requestURL(bucket_name, file_name))
    # print(session['file_names'])
    """Need to display stuff from the Bucket"""
    if count > 0 :
        return render_template('mysignatures.html',signatures=signatures)

    else:
        msg = "No Signature Found"
        logging.warning('No Signature found')
        return render_template('mysignatures.html',msg=msg)

    return render_template('mysignatures.html')

#~~~~~~~~~~~~~~~~~~~~~~~ GLOBAL CONSTANTS ~~~~~~~~~~~~~~~~~~~~~~~#

save_path=0
out_path=0
# bucket_name=0
img_name=0
flag=0

gen_file_name = None
gen_file_update = None

#~~~~~~~~~~~~~~~~~~~~~~~ GENERATOR FOR EXTRACTING SIGNATURE AND UPLOADING IT TO BUCKET ~~~~~~~~~~~~~~~~~~~~~~~#
# @is_logged_in
def generator():
    global save_path
    global out_path
    global bucket_name
    global gen_file_name
    global gen_file_update
    global img_name
    yield "data:" + str(10) + "\n\n"
    #preprop.preprocess(save_path, save_path)
    #yield "data:" + str(30) + "\n\n"
    extract_sig.process_image(save_path, out_path)
    logging.info('Image Processed by extract_sig.py')
    yield "data:" + str(50) + "\n\n"
    rmv_bck.add_alpha_channel(out_path,out_path)
    logging.info('Alpha channel removed by rmv_back.py')
    yield "data:" + str(60) + "\n\n"
    sig_dark.darken(out_path, out_path)
    logging.info('Darkening Image by sig_dark.py')
    yield "data:" + str(70) + "\n\n"
    gc.collect()
    Key = "img_"+str(uuid.uuid4())+".png"
    ufile.upload2bucket(Filename=out_path, Bucket=bucket_name, Key=Key)
    print(gen_file_name)
    gen_file_name = Key
    gen_file_update = datetime.today().strftime('%Y-%m-%d %H:%M:%S')

    logging.info('Extracted Image Uploaded to Bucket')
    yield "data:" + str(90) + "\n\n"
    os.remove(out_path)
    logging.info('Final Image Removed from local storage')
    yield "data:" + str(100) + "\n\n"

    flash('SIGNATURE ADDED','success')

#~~~~~~~~~~~~~~~~~~~~~~~ GENERATOR WHEN POST METHOD IS NOT USED i.e WHEN ERROR FILE IS UPLOADED OR FOR FIRST VISIT  ~~~~~~~~~~~~~~~~~~~~~~~#

def err_generator():
    logging.info('Err_generator called')
    yield "data:" + str(0) + "\n\n"


#~~~~~~~~~~~~~~~~~~~~~~~ ROUTE: add_signature *add signature page* ~~~~~~~~~~~~~~~~~~~~~~~#


@app.route('/add_signature/', methods=['GET','POST'])
# @is_logged_in
def add_signature():
    global save_path
    global out_path
    global bucket_name
    global img_name
    if request.method == 'POST' and request.files['image']:
        global flag
        flag=1
        img=request.files['image']
        logging.info('Signature Form POSTed and Image Received by CloudFoundry Server')

        if allowed_file(img.filename):
            logging.info('Allowed File ===> YES')
            img_name=secure_filename(img.filename)
            create_new_folder(app.config['UPLOAD_FOLDER'])
            save_path = os.path.join(app.config['UPLOAD_FOLDER'] , img_name)
            img.save(save_path)
            out_path = save_path.replace('.jpg', '_sig_detected.png')
            # bucket_name = session['bucket_name']
            # bucket_name = 'a1edf455-273f-48a6-a2c5-0b056a042e5d'
            del img
            logging.info('Global Vars Set, Redirecting to dashboard')
            logging.debug('Expecting Generator')
            print("rendenring dashboard")
            print("####################")
            print("Printing Requests : ", request)
            print("####################")
            return render_template('mysignatures.html')

        else:
           msg=("IMAGE INVALID - CHECK FORMAT (.JPG)","Danger")
           logging.warning('Invalid Input')
           flag=0
           return render_template('add_signature.html',msg=msg)

    logging.info('Rendering add_signature.html')
    return render_template('add_signature.html')


#~~~~~~~~~~~~~~~~~~~~~~~ ROUTE: progress * route when submit button is pressed on add_signature.html * ~~~~~~~~~~~~~~~~~~~~~~~#


@app.route('/progress')
def bar():
    logging.info('Route accessed ==> progress')
    global flag
    if flag==1:
        logging.debug('global Flag SET')
        logging.info("CALLING LEGIT_GENERATOR")
        return Response(generator(), mimetype= 'text/event-stream')
    else:
        logging.debug('global Flag UNSET')
        logging.info("CALLING ERROR GENERATOR" + str(flag))
        return Response(err_generator(), mimetype= 'text/event-stream')


#~~~~~~~~~~~~~~~~~~~~~~~ ROUTE: delete_signature * route for deleting signtures from the bucket * ~~~~~~~~~~~~~~~~~~~~~~~#

@app.route('/delete_signature/<string:id>',methods=['POST'])
# @is_logged_in
def delete_signature(id):
    try:
        if id in session['file_names']:
            index = session['file_names'].index(id)
            session['file_names'].remove(id)
            del session['file_update'][index]
            print("FIles deleted")
        else:
            print('Id not found')
    except Exception as e:
        print(e)
    # bucket_name = session['bucket_name']
    # bucket_name = 'a1edf455-273f-48a6-a2c5-0b056a042e5d'
    ufile.delete_item(bucket_name, id)
    logging.info('Signature Deleted from Bucket')
    flash('Signature deleted','success')
    return redirect(url_for('mysignatures'))





if __name__ == '__main__':
    app.run(debug='True')
    # pass


        # pdf=request.files['pdf']
        # logging.info('PDF Form POSTed')

        # pdf_name=secure_filename(pdf.filename)
        # if '.pdf' in pdf_name[-4:]:
        # #create_new_folder(app.config['UPLOAD_FOLDER'])
        #     save_path = os.path.join(app.config['PDF_FOLDER'] , session['username'] + ".pdf")
        #     pdf.save(save_path)
        #     with open(os.path.normpath(save_path),"rb") as f:
	       #      cur_pdf = PdfFileReader(f)
	            
	       #      for pages in range(cur_pdf.getNumPages()):
	       #          cur_page = cur_pdf.getPage(pages)
	       #          output = PdfFileWriter()
	       #          output.addPage(cur_page)
	       #      # print(new_path)#[:-4]+'_out.pdf')
	       #          output.write(open(os.path.normpath(save_path[:-4]+'_'+str(pages)+'.pdf'),"wb"))
	            
        #     out_path = save_path.replace('.pdf', '_signed.pdf')
        #     bucket_name = session['bucket_name']
        #     del pdf
        #     try:
        #         print("uploading..")
        #         upload2bucket(Filename=save_path, Bucket=bucket_name, Key='1.pdf')
        #         print("uploaded..")
        #         # try:
        #             # if len(session['file_names'] )
        #         session['file_names'].append('1.pdf')
        #         session['file_update'].append(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
        #         print("updated session")
        #         # except:
        #         logging.info('PDF uploaded to bucket as 1.pdf')
        #         flash('PDF ADDED','success')
        #         return redirect(url_for('retrieval', page_no=0))

        #     except Exception as e:
        #         logging.warning('1.pdf not uploaded')
        #         # return make_response(e)
        #         return render_template('signpdf.html')
