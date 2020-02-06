import psycopg2
import psycopg2.extras

# DATABASE_URL = "postgres://qgnvbmsplbvqce:8cb4b33626fed4f446c45ad0956379133e6c946f70643b2a866b867a3969d94f@ec2-184-72-236-3.compute-1.amazonaws.com:5432/dbd7uveailk0vg"
DATABASE_URL = "postgres://postgres@localhost/plo"
plo = psycopg2.connect(DATABASE_URL, sslmode='require')
cursor = plo.cursor(cursor_factory=psycopg2.extras.DictCursor)

def get_columns_db(cursor, table_name, connection=plo):
    # cursor = connection.cursor()
    try:
        cursor.execute("SELECT * FROM {} LIMIT 0".format(table_name))
        # cursor.execute("""select *
        #        from information_schema.columns
        #        where table_schema NOT IN ('information_schema', 'pg_catalog')
        #        order by table_schema, table_name""")
        # column_names = []
        # data_types = []
        # for row in cursor:
        # 	if row['table_name'] == table_name.lower():
        # 		column_names.append(row['column_name'])
        # 		data_types.append(row['data_type'])

        # return column_names, data_types
        colnames = [desc[0] for desc in cursor.description]
        return colnames
    except psycopg2.errors.UndefinedTable as e:
        print(e)
        return []
    except psycopg2.errors.InFailedSqlTransaction as e:
        print(e)
        return []
    except psycopg2.InterfaceError as e:
        print(e)
        return []


def write_to_db(cursor, table_name, values, connection=plo):
    while True:
        columns = list(values.keys())
        column_names = ""
        number_of_values = ""
        for column in columns:
            column_names += column + ", "
            if isinstance(values[column], str):
            	number_of_values += "'" + str(values[column]) + "', "
            elif isinstance(values[column], int):
            	number_of_values += str(values[column]) + ", "
        if len(column_names) >= 2:
            column_names = column_names[:-2]
        if len(number_of_values) >= 2:
            number_of_values = number_of_values[:-2]
        # number_of_values = ("{},"*len(columns))[:-1]
        print(columns)

        query = """INSERT INTO {}({}) VALUES({})""".format(table_name, column_names, number_of_values)
        # query = """INSERT INTO docstatus(docid, owner, userlist, activeuser, wfid) VALUES(15, 'sAhaan', '{"sAP", "sHarsh", "sBharath"}', 'sHarsh', 1)"""
        print(query)
        try:
            cursor.execute(query)
            print("what")
            connection.commit()
            print("da")
            return True
        except psycopg2.errors.InFailedSqlTransaction as e:
            return False
        except psycopg2.errors.UniqueViolation as e:
            return False
        except psycopg2.errors.InterfaceError as e:
            time.sleep(1)

def read_db(cursor, table_name, column_names:dict=None, connection=plo):
        
    try:  
        #Reading the Employee data 
        # cursor = connection.cursor()
        search_str = "*"
        if column_names is not None:
            search_str = ""
            for column_name in column_names:
                search_str += column_name + "=" + "'" + column_names[column_name] + "', "
            if len(search_str) >= 2:
                search_str = search_str[:-2]
            cursor.execute("SELECT * from {} WHERE {}".format(table_name, search_str))  
        else:
        	cursor.execute("SELECT * from {}".format(table_name))

      
        #fetching the rows from the cursor object  
        result = cursor.fetchall() 

        columns = get_columns_db(cursor, table_name)
        list_dict_result = []
        for row in result:
            dict_result = {}
            for column_no in range(len(row)):
                dict_result[columns[column_no]] = row[column_no]
            list_dict_result.append(dict_result)
        return list_dict_result 
    except Exception as e: 
        print(e) 
        connection.rollback()  
    return []


# @app.route('/signpdf/', methods=['GET','POST'])
# @is_logged_in
# def signpdf():
#     if request.method == 'POST' and request.files['pdf']:

#         pdf=request.files['pdf']
#         # logging.info('PDF Form POSTed')

#         pdf_name=secure_filename(pdf.filename)
#         if '.pdf' in pdf_name[-4:]:
#         #create_new_folder(app.config['UPLOAD_FOLDER'])
#             save_path = os.path.join(app.config['PDF_FOLDER'] , session['username'] + ".pdf")
#             pdf.save(save_path)
#             with open(os.path.normpath(save_path),"rb") as f:
# 	            cur_pdf = PdfFileReader(f)
	            
# 	            for pages in range(cur_pdf.getNumPages()):
# 	                cur_page = cur_pdf.getPage(pages)
# 	                output = PdfFileWriter()
# 	                output.addPage(cur_page)
# 	            # print(new_path)#[:-4]+'_out.pdf')
# 	                output.write(open(os.path.normpath(save_path[:-4]+'_'+str(pages)+'.pdf'),"wb"))
	            
#             out_path = save_path.replace('.pdf', '_signed.pdf')
#             bucket_name = session['bucket_name']
#             del pdf
#             try:
#                 print("uploading..")
#                 # upload2bucket(Filename=save_path, Bucket=bucket_name, Key='1.pdf')
#                 print("uploaded..")
#                 # try:
#                     # if len(session['file_names'] )
#                 session['file_names'].append('1.pdf')
#                 session['file_update'].append(datetime.today().strftime('%Y-%m-%d %H:%M:%S'))
#                 print("updated session")
#                 # except:
#                 logging.info('PDF uploaded to bucket as 1.pdf')
#                 flash('PDF ADDED','success')
#                 return redirect(url_for('retrieval', page_no=0))

#             except Exception as e:
#                 logging.warning('1.pdf not uploaded')
#                 # return make_response(e)
#                 return render_template('signpdf.html')
#         else:
#             logging.info('Wrong extension')
#             flash('PDF could not be uploaded (check if format is .pdf or not)','danger')
#             return render_template('signpdf.html')
#     return render_template('signpdf.html')



if __name__ == '__main__':
	# print(get_columns_db(cursor, "DocInfo"))
	# write_to_db(cursor, "DocStatus", {'docid': 5, 'owner': 'Ahaan', 'userlist': '{"AP", "Harsh"}', 'activeuser': 'AP', 'wfid': 2})
	# print(read_db(cursor, "userinfo"))
	email_info = {'userid': 'bharathvarma21041999@gmail.com'}
	user_info = read_db(cursor, 'userinfo', email_info)[0]
	print(user_info)

