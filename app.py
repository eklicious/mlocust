import helper
import os
from flask import Flask, flash, request, redirect, render_template, url_for
from werkzeug.utils import secure_filename

# Hard code the project id and vm size
projectId = "mside-287120"
vmSize = "c2-standard-4"

UPLOAD_FOLDER = './uploads'
ALLOWED_EXTENSIONS = {'txt', 'py'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = b'_5#y2L"F4Q8z\n\xecasdf]/'
SESSION_TYPE = 'filesystem'

# Create a method to flash multiple messages
def multiflash(msgs):
    for m in msgs:
        flash(m)

def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/', methods=['GET', 'POST'])
def upload_file():
    # multiflash(helper.test())

    if request.method == 'POST':
        # The form serves 2 functions: uploading locust files or deploying gke changes

        # cluster name is absolutely req'd. Without it, we can't do anything
        clusterNm = request.form['clusterNm']

        # Fetch the other form values too just for redirect purposes
        zone = request.form['zone']
        ttl = request.form['ttl']
        maxRPS = request.form['maxRPS']
        currentRPS = request.form['currentRPS']

        if len(clusterNm.strip())<6 or clusterNm.strip().lower()=="mlocust":
            flash('Cluster name needs to be at least 6 chars and cannot be named mlocust', 'error')
            return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+ttl+"&maxRPS="+maxRPS+"&currentRPS="+currentRPS)
        else:
            flash(f"Cluster name set to {clusterNm}")

        # If we are cleaning up, do it now and don't proceed
        if "cleanup" in request.form:
            multiflash(helper.cleanup(clusterNm, zone))
            return redirect("/")

        # check if the post request has the file part
        # Skip the check for now
        # if 'file' in request.files:
        file = request.files['file']

        # If the user does not select a file, the browser submits an
        # empty file without a filename.
        if file.filename == '':
            flash('Configuring GKE Cluster')

            # Check all parameters are set and valid
            flash(f"Zone set to {zone}")

            # must be numeric and >=60 and <=7200
            try:
                ttl = int(ttl)
            except Exception as e:
                flash('TTL must be an integer', 'error')
                return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))
            if ttl<60 or ttl>7200:
                flash('TTL must be >=60s and <=7200s', 'error')
                return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))

            # Check max RPS numeric and >0 and <=39k (39 worker replicas)
            try:
                maxRPS = int(maxRPS)
            except Exception as e:
                flash('Max Requests/Sec must be an integer', 'error')
                return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))
            if maxRPS<1:
                flash('Max Requests/Sec must be >0 and <=39000 (due to hard-coded limit of 39 worker replicas. Contact eugene.kang@mongodb.com if you need to go beyond this)', 'error')
                return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))

            # Check current RPS numeric and >0 and <=maxRPS
            try:
                currentRPS = int(currentRPS)
            except Exception as e:
                flash('Current Requests/Sec must be an integer', 'error')
                return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))
            if currentRPS<1 or currentRPS>maxRPS:
                flash('Current Requests/Sec must be >0 and <=max requests/sec', 'error')
                return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))

            # If we made it this far, it's time to deploy!
            multiflash(helper.deploy(projectId, clusterNm, vmSize, zone, maxRPS, currentRPS, ttl))
            return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))

        else:
            flash('Handling file upload only at the moment')
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)

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
                    flash('locustfile.py uploaded successfully. Did you remember to upload your requirements.txt too if you made any modifications?')
                    file.save(os.path.join(dir, "locustfile.py"))
                else:
                    flash('requirements.txt uploaded successfully. Did you remember to upload your locust file?')
                    file.save(os.path.join(dir, "requirements.txt"))
            else:
                flash('File type not allowed. Only .py and .txt permitted.', 'error')

            return redirect("/?clusterNm="+clusterNm+"&zone="+zone+"&ttl="+str(ttl)+"&maxRPS="+str(maxRPS)+"&currentRPS="+str(currentRPS))


    return render_template('index.html')    
