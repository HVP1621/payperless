from PyPDF2 import PdfFileWriter, PdfFileReader
from reportlab.pdfgen import canvas
from io import BytesIO
import sys
import os
import rmv_bck

def place_sign(path,pdf_path,detail, page_no=0):


	count = 0
	f = open(os.path.normpath(pdf_path),"rb")
	pdf_op = PdfFileReader(f)
	pages = pdf_op.getNumPages()
	page = pdf_op.getPage(page_no)
	for save_path in path:
		details = detail[str(count+1)].split(' ')
		count += 1

		X, Y, height, width = float(details[1]), float(details[2]), float(details[3]), float(details[4])
		# Using ReportLab to insert image into PDF
		imgTemp = BytesIO()
		imgDoc = canvas.Canvas(imgTemp)

		# Draw image on Canvas and save PDF in buffer
		imgPath = str(save_path)
		# cords = (width, height)
		# add_alpha_channel(imgPath, imgPath, resize=True, cords=cords)

		# print(os.path.normpath(pdf_path))
		new_path = os.path.normpath(pdf_path)
		media_box = page.mediaBox
		min_pt = media_box.lowerLeft
		max_pt = media_box.upperRight

		pdf_width = float(max_pt[0] - min_pt[0])
		pdf_height = float(max_pt[1] - min_pt[1])

		# print('pdf width = ', pdf_width)
		# print('pdf height = ', pdf_height)

		X = X*(pdf_width/10)
		Y = Y*(pdf_height/10)*(59.3/65.81500244140625)
		# height *= 65.81500244140625
		height *= (pdf_height/10)*(59.3/65.81500244140625)
		#height *= 59.3
		width *= (pdf_width/10)*1.2

		# print(X, Y, height, width)


		if height < 146:
			Y = Y + (height - 134)

		if X < pdf_width/2:
			X = X - 50


		# if X + width > pdf_width:
		# 	X = pdf_width - width
		# if Y + height > pdf_height:
		# 	Y = pdf_height - height

		# if X >150:
		# 	X = X + 50
		# if Y > 200:
		# 	Y = float(pdf_height) - Y - 190
		# elif Y > 0:
		# 	Y = float(pdf_height) - Y - 190 - (120 - Y)
		# else:
		# 	Y = float(pdf_height) + Y - 50


		if pdf_width < pdf_height:
			# imgDoc.drawImage(os.path.normpath(imgPath), abs(X)+50, Y, width, height, mask=[0, 2, 0, 2, 0, 2, ])    ## at (399,760) with size 160x160
			imgDoc.drawImage(os.path.normpath(imgPath), X+50, pdf_height - Y- 182, width, height, mask=[0, 2, 0, 2, 0, 2, ])    ## at (399,760) with size 160x160

		else:
			imgDoc.drawImage(os.path.normpath(imgPath) ,pdf_height - Y- 150, X+50, width, height, mask=[0, 2, 0, 2, 0, 2, ])    ## at (399,760) with size 160x160
		imgDoc.save()
		# print("Saved")
		# Use PyPDF to merge the image-PDF into the template

		# print("Reading")
		overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
		page.mergePage(overlay)
		#Save the result
	output = PdfFileWriter()
	output.addPage(page)
	# print(new_path)#[:-4]+'_out.pdf')
	output.write(open(os.path.normpath(pdf_path[:-4]+'_'+str(page_no)+'.pdf'),"wb"))
	f.close()
	return pages
	# output.write(open(os.path.normpath(pdf_path),"wb"))

# if __name__ == '__main__':
#         place_sign('C:\Users\Bharath\Desktop\Deloitte\SignIT-v2\myflaskapp\uploads\img_7c18cb74-8e6f-4807-8bf4-d337fd75550e.png', 'C:\Users\Bharath\Desktop\Deloitte\SignIT-v2\myflaskapp\uploads\input.pdf', '347.4878234863279', '16.503417968749996', '271', '325')


# def place_sign(path,pdf_path,details):

# 	X, Y, height, width = details['X'], details['Y'], details['height'], details['width']

# 	# Using ReportLab to insert image into PDF
# 	imgTemp = BytesIO()
# 	imgDoc = canvas.Canvas(imgTemp)

# 	# Draw image on Canvas and save PDF in buffer
# 	imgPath = str(path)

# 	imgDoc.drawImage(os.path.normpath(imgPath),float(Y)*72/2.54, float(X)*72/2.54, float(height)*72/2.54, float(width)*72/2.54, mask=[0, 2, 0, 2, 0, 2, ])    ## at (399,760) with size 160x160
# 	imgDoc.save()
# 	print("Svaed")
# 	# Use PyPDF to merge the image-PDF into the template
# 	page = PdfFileReader(open(os.path.normpath(pdf_path),"rb")).getPage(0)
# 	print("Reading")
# 	overlay = PdfFileReader(BytesIO(imgTemp.getvalue())).getPage(0)
# 	page.mergePage(overlay)
# 	#Save the result
# 	output = PdfFileWriter()
# 	output.addPage(page)
# 	output.write(open(os.path.normpath(pdf_path[:-4]+'_out.pdf'),"wb"))
