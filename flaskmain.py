from flask import Flask
from flask import request
import os
from flask import Flask, request, redirect, url_for
from werkzeug.utils import secure_filename
from flask import send_from_directory
from flask.ext.httpauth import HTTPBasicAuth
from flask import make_response
from flask import Flask, jsonify
import uuid
from flask.ext.mail import Mail, Message
import ConfigParser
import numpy as np
import dicom


auth = HTTPBasicAuth()


def entropy(signal):
	'''
	function returns entropy of a 1-D numpy array
	'''
	sigsize = signal.size
	symset = list(set(signal))
	propb = [np.size(signal[signal == i]) / (1.0 * sigsize) for i in symset]
	entro = np.sum([p * np.log2(1.0 / p) for p in propb])
	return entro


def entro_filt(imagedata, N=5):
	S = imagedata.shape
	entro_filt = np.array(imagedata)
	for io in range(S[0]):
		for j in range(S[1]):
			Lx = np.max([0, j - N])
			Ux = np.min([S[1], j + N])
			Ly = np.max([0, io - N])
			Uy = np.min([S[0], io + N])
			region = imagedata[Ly:Uy, Lx:Ux].flatten()
			entro_filt[io, j] = entropy(region)
	return entro_filt


@auth.get_password
# def get_password(username):
# 	if username == str(config.get('UserInfo','USER')):
# 		return str(config.get('UserInfo','PASS'))
# 	return None
def get_password(username):
	if username == os.environ['APP_USER']:
		return os.environ['APP_PASS']
	return None


@auth.error_handler
def unauthorized():
	return make_response(jsonify({'error': 'Unauthorized access'}), 401)
app = Flask(__name__)

app.config.update(dict(
	DEBUG=True,
	# EMAIL SETTINGS
	MAIL_SERVER='localhost', # smtp.gmail.com
	MAIL_PORT=25,
	MAIL_USE_TLS=False,
	MAIL_USE_SSL=False
	# MAIL_USE_SSL=True,
	# MAIL_USERNAME=os.environ['MAIL_USERNAME'],
	# MAIL_PASSWORD=os.environ['MAIL_PASSWORD']
))
mail = Mail(app)
UPLOAD_FOLDER = os.environ['OPENSHIFT_DATA_DIR']
ALLOWED_EXTENSIONS = set(['dcm'])
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['PROPAGATE_EXCEPTIONS'] = True


@app.route("/")
def hello():
	return 'MIAcloud --->>>>> curl -u user:pass -i -X POST -F "file=@/IM-0001-0054.dcm" http://miacloud-panagiotis.rhcloud.com/upload?email=a@a.ed'


def allowed_file(filename):
	return '.' in filename and \
		filename.rsplit('.', 1)[1] in ALLOWED_EXTENSIONS


@app.route('/upload', methods=['GET', 'POST'])
@auth.login_required
def upload_file():
	if request.method == 'POST':
		file = request.files['file']
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			filename2 = str(uuid.uuid4()) + '.' + filename.rsplit('.', 1)[1]
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename2))
			dicomfile = dicom.read_file(
				os.path.join(app.config['UPLOAD_FOLDER'], filename2))
			temp = dicomfile.pixel_array
			dicomfile.pixel_array = entro_filt(temp, 5)
			dicomfile.save_as(
				os.path.join(app.config['UPLOAD_FOLDER'], filename2))
			getfileurl='http://'+str(os.environ.get('OPENSHIFT_APP_DNS'))+'/uploads/'+str(filename2)
		if 'email' in request.args:
			email = request.args['email']
			message = Message(
				subject='Thanks for trusting our service!', sender=os.environ['MAIL_USERNAME'], html="""<html><body><h1>Good News!!!</h1>
				<p>If you didn't already download the results, you can visit 
				<a href="http://{}/uploads/{}">your private link</a>. You'll be able to
				download the file up to five times, at which point the link will
				expire.""".format(os.environ['MAIL_PASSWORD'], filename2), recipients=[email])
			with mail.connect() as conn:
				conn.send(message)
			return redirect(url_for('uploaded_file',filename=getfileurl))
	return '''
	<!doctype html>
	<title>Upload new File</title>
	<h1>Upload new File</h1>
	<form action="" method=post enctype=multipart/form-data>
	  <p><input type=file name=file>
		 <input type=submit value=Upload>
	</form>
	'''


@app.route('/uploads/<filename>')
@auth.login_required
def uploaded_file(filename):
	if request.method == 'GET':
		return send_from_directory(app.config['UPLOAD_FOLDER'],
								   filename)

if __name__ == "__main__":
	app.run()
