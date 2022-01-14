import helper
import os
from flask import Flask, flash, request, redirect, session, render_template, url_for
from flask_cors import CORS
from werkzeug.utils import secure_filename
import json
import subprocess
import sys

# Hard code the project id and vm size
projectId = "oblivion02"
vmSize = "c2-standard-4"

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'py'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xecasdf]/'
SESSION_TYPE = 'filesystem'
CORS(app, resources={r"/*": {"origins": "*"}})

# Create a method to flash multiple messages
def multiflash(msgs):
    session['flash'] = msgs


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/flash', methods=['GET'])
def flashy():
    return json.dumps(session['flash'])


@app.route('/rm_cluster', methods=['GET'])
def test_delete():
    # This will be the entry point. Whether a cluster is up and running or not. Check for it.
    msgs = []
    cluster_name = request.args.get('cluster')
    zone = request.args.get('zone')
    multiflash(helper.cleanup(cluster_name, zone))
    return "OK"



@app.route('/', methods=['POST'])
def upload_file():
    if request.method == 'POST':
        # The form serves 2 functions: uploading locust files or deploying gke changes
        # cluster name is absolutely req'd. Without it, we can't do anything
        clusterNm = ""
        # Fetch the other form values too just for redirect purposes
        zone = ""
        ttl = 0
        maxRPS = 0
        currentRPS = 0
        isFORM = False
        username = ""
        post_data = request.form
        if post_data:
            isFORM = True
        if post_data['clusterNm']:
            clusterNm = post_data['clusterNm']
        if post_data['zone']:
            zone = post_data['zone']
        if post_data['ttl']:
            ttl = post_data['ttl']
        if post_data['maxRPS']:
            maxRPS = post_data['maxRPS']
        if post_data['currentRPS']:
            currentRPS = post_data['currentRPS']
        if post_data['username']:
            username = post_data['username']

        if len(clusterNm.strip())<6 or clusterNm.strip().lower()=="mlocust":
            session['flash'] = 'Cluster name needs to be at least 6 chars and cannot be named mlocust', 'error'
            return json.dumps({"error":"true","topic":"clusterNm","msg":session['flash']})


        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if isFORM:
            # Check all parameters are set and valid
            # must be numeric and >=60 and <=7200
            try:
                ttl = int(ttl)
            except Exception as e:
                return json.dumps({"ttl_error":"true","topic":"ttl","msg":ttl})
            if ttl<60 or ttl>7200:
                return json.dumps({"ttl_error":"true","topic":"ttl","msg":ttl})

            # Check max RPS numeric and >0 and <=39k (39 worker replicas)
            try:
                maxRPS = int(maxRPS)
            except Exception as e:
                return json.dumps({"rps_error":"true","topic":"maxRPS","msg":maxRPS})
            if maxRPS<1:
                return json.dumps({"rps_error":"true","topic":"maxRPS","msg":maxRPS})

            # Check current RPS numeric and >0 and <=maxRPS
            try:
                currentRPS = int(currentRPS)
            except Exception as e:
                return json.dumps({"error":"true","topic":"currentRPS","msg":currentRPS})
            if currentRPS<1 or currentRPS>maxRPS:
                return json.dumps({"error":"true","topic":"currentRPS","msg":currentRPS})




            fileA = request.files['fileA']
            fileB = request.files['fileB']
            if fileA.filename == '':
                return json.dumps({"file_a_error":session['flash']})
            if fileB.filename == '':
                return json.dumps({"file_b_error":session['flash']})

            if fileA and allowed_file(fileA.filename):
                filename = secure_filename(fileA.filename)

                # Check if the upload dir exists or not
                dir = app.config['UPLOAD_FOLDER']+"/"+clusterNm
                if not os.path.exists(dir):
                    try:
                        os.makedirs(dir)
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                # rename the file to locustfile.py in case they named it something else
                if filename.endswith(".py"):
                    session['flash'] = 'locustfile.py uploaded successfully. Did you remember to upload your requirements.txt too if you made any modifications?'
                    fileA.save(os.path.join(dir, "locustfile.py"))

            if fileB and allowed_file(fileB.filename):
                filename = secure_filename(fileB.filename)

                # Check if the upload dir exists or not
                dir = app.config['UPLOAD_FOLDER']+"/"+clusterNm
                if not os.path.exists(dir):
                    try:
                        os.makedirs(dir)
                    except OSError as exc: # Guard against race condition
                        if exc.errno != errno.EEXIST:
                            raise

                # rename the file to locustfile.py in case they named it something else
                if filename.endswith(".txt"):
                    session['flash'] = 'requirements.txt uploaded successfully. Did you remember to upload your locust file?'
                    fileB.save(os.path.join(dir, "requirements.txt"))

            # do we have everything?
            requirementsTxtPath = app.config['UPLOAD_FOLDER']+"/"+clusterNm+"/requirements.txt"
            locustFilePath = app.config['UPLOAD_FOLDER']+"/"+clusterNm+"/locustfile.py"

            if not os.path.exists(requirementsTxtPath):
                return json.dumps({"requirementsTxtPathErr":"true","msg":requirementsTxtPath})
            if not os.path.exists(locustFilePath):
                return json.dumps({"locustFilePathErr":"true","msg":locustFilePath})

            # If we made it this far, it's time to deploy!
            deployOutput = helper.deploy(username,projectId, clusterNm, vmSize, zone, maxRPS, currentRPS, ttl)
            return json.dumps({"success":"true","deploy":deployOutput,"cluster_name":clusterNm,"zone":zone,"public_ip":helper.get_ip(clusterNm,zone)})
