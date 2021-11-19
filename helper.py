import subprocess
import time
import math
from pymongo import MongoClient
import sys
# from flask import Flask
# import logging

uri = "mongodb+srv://shared.3zdou.mongodb.net/myFirstDatabase?authSource=%24external&authMechanism=MONGODB-X509&retryWrites=true&w=majority"
client = MongoClient(uri,
                     tls=True,
                     tlsCertificateKeyFile='X509-cert-716885866134776497-msideaudit.cer')
db = client['mside']
audit = db['audit']

# app = Flask(__name__)
# logging.basicConfig(level=logging.DEBUG)

def test():
    msgs = []
    msgs2 = ["abc"]
    out = subprocess.run(f"echo 'hey' && echo 'nowls'", shell=True, capture_output=True)
    msgs.append(get_resp(out))
    out = subprocess.run(f"echo 'hey2' && echo 'now2'", shell=True, capture_output=True)
    msgs.append(get_resp(out))
    msgs2.append(msgs)
    return msgs2

def format(s):
    # get rid of the /n and /t etc and make it display properly
    return s.decode("utf-8").replace('\n', '<br \>').replace('\t', '&nbsp;&nbsp;&nbsp;&nbsp;').strip()

def get_ex(e):
    # Insert exception into the audit database
    # Display the exception to the front end
    return "Exception: " + str(e)

def get_resp(out):
    if isinstance(out, str):
        # plain old string message
        print(out, file=sys.stdout)
        # app.logger.error(out)
        return "Log: " + out        
    elif out.returncode == 0:
        # output the stdout only as a success message
        print(format(out.stdout), file=sys.stdout)
        # app.logger.error(format(out.stdout))
        return "Success: " + format(out.stdout)
    else:
        # error occurred, e.g. cluster name conflict
        return "Error: " + format(out.stderr)

def create_cluster(clusterNm, vmType, zone, maxRPS):
    msgs = ["Creating Cluster"]
    try:
        # Check to see if the node count is too high
        maxNodes = calc_nodes(maxRPS)
        if maxNodes>10:
            raise Exception('Node count is too high. Keep it <=10 else contact eugene.kang@mongodb.com')
        if maxNodes<1:
            raise Exception('You need at least 1 node...')

        msgs.append(get_resp("Creating GKE cluster now."))
        out = subprocess.run(f"gcloud container clusters create {clusterNm} --zone {zone} --scopes \"https://www.googleapis.com/auth/cloud-platform\" --machine-type \"{vmType}\" --num-nodes \"1\" --enable-autoscaling --min-nodes \"1\" --max-nodes \"{maxNodes}\" --addons HorizontalPodAutoscaling,HttpLoadBalancing", shell=True, capture_output=True)
        msgs.append(get_resp(out))
    except Exception as e:
        msgs.append(get_ex(out)) 
    return msgs

def set_delete_cluster(clusterNm, zone, ttlSecs):
    msgs = [f"Setting cluster TTL to {ttlSecs} seconds."]
    try:
        # Run this process in the background. No output
        subprocess.Popen(f"sleep {ttlSecs} && yes | gcloud container clusters delete {clusterNm} --zone {zone}", shell=True)
    except Exception as e:
        msgs.append(get_ex(out))
    return msgs

def get_credentials(clusterNm, zone):
    msgs = ["Get GKE cluster credentials so we can call kubectl commands."]
    try:
        # Get the credentials and update kubeconfig so we can use kubectl
        out = subprocess.run(f"gcloud container clusters get-credentials {clusterNm} --zone {zone}", shell=True, capture_output=True)
        msgs.append(get_resp(out))
    except Exception as e:
        msgs.append(get_ex(out))
    return msgs

def deploy(projectId, clusterNm, vmSize, zone, maxRPS, currentRPS, ttlSecs):
    msgs = ["Deploying codes and/or clusters"]
    try:
        # Create a subdirectory for the cluster name. Each cluster gets its own build
        # Based on the locustfile.py and requirements.txt that the user uploads, we need to replace the files in the clone dir above
        msgs.append(get_resp("Fetch latest container codes and update it with user's own locust and requirements file if the file exists."))
        out = subprocess.run(f"if [ -f 'uploads/{clusterNm}/locustfile.py' ]; then rm -rf {clusterNm} && mkdir {clusterNm} && cd {clusterNm} && git clone https://github.com/eklicious/mlocust-app && mv ../uploads/{clusterNm}/locustfile.py mlocust-app/docker-image/locust-tasks/locustfile.py && mv ../uploads/{clusterNm}/requirements.txt mlocust-app/docker-image/locust-tasks/requirements.txt && cd mlocust-app && gcloud builds submit --tag gcr.io/{projectId}/{clusterNm}:latest docker-image/.; fi", shell=True, capture_output=True)

        # This will be the entry point. Whether a cluster is up and running or not. Check for it.
        msgs.append(get_resp("Checking if the cluster already exists or not."))
        out = subprocess.run(f"gcloud container clusters describe {clusterNm} --zone {zone}", shell=True, capture_output=True)
        if out.returncode == 0:
            # Audit any executions
            audit.insert_one({"type":"mLocust", "action":"redeploy", "userId":"Add this later with auth", "msg":{"clusterNm":clusterNm, "vmSize":vmSize, "zone":zone, "maxRPS":maxRPS, "currentRPS":currentRPS, "ttlSecs":ttlSecs}})

            # cluster already exists. Scale to 0 then to workers
            msgs.append(get_resp(f"Cluster already exists. Just scale nodes down and rescale back up."))
            scale_master(clusterNm, zone, 0)
            scale_workers(clusterNm, zone, 0)
            scale_master(clusterNm, zone, 1)
            scale_workers(clusterNm, zone, currentRPS)
        else:
            # Audit any executions
            audit.insert_one({"type":"mLocust", "action":"deploy", "userId":"Add this later with auth", "msg":{"clusterNm":clusterNm, "vmSize":vmSize, "zone":zone, "maxRPS":maxRPS, "currentRPS":currentRPS, "ttlSecs":ttlSecs}})

            # build cluster out from scratch
            msgs.append(create_cluster(clusterNm, vmSize, zone, maxRPS))

            # Now configure and deploy the master and worker nodes
            msgs.append(deploy_nodes(projectId, clusterNm, zone))

            # Present the External IP so we can access the locust portal
            msgs.append(get_ip(clusterNm, zone))

            # Scale the workers if the RPS target is higher than 1000
            if currentRPS>1000:
                msgs.append(scale_workers(clusterNm, zone, currentRPS))

            # Set ttl for the cluster
            msgs.append(set_delete_cluster(clusterNm, zone, ttlSecs))

    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def deploy_nodes(projectId, clusterNm, zone):
    msgs = ["Configure the master and worker nodes"]
    try:
        # TODO probably best to inline all these commands so we get a single output and not 10
        # First update the k8s yml files to include references to the projectId
        msgs.append(get_resp("Update the K8s yaml files with the appropriate GCR url pointing to the latest cluster container build."))
        out = subprocess.run(f"sed -i -e \"s/\\[TARGET_HOST\\]/not_used/g\" {clusterNm}/mlocust-app/kubernetes-config/locust-master-controller.yaml", shell=True, capture_output=True)
        out = subprocess.run(f"sed -i -e \"s/\\[TARGET_HOST\\]/not_used/g\" {clusterNm}/mlocust-app/kubernetes-config/locust-worker-controller.yaml", shell=True, capture_output=True)
        out = subprocess.run(f"sed -i -e \"s/\\[PROJECT_ID\\]/{projectId}/g\" {clusterNm}/mlocust-app/kubernetes-config/locust-master-controller.yaml", shell=True, capture_output=True)
        out = subprocess.run(f"sed -i -e \"s/\\[PROJECT_ID\\]/{projectId}/g\" {clusterNm}/mlocust-app/kubernetes-config/locust-worker-controller.yaml", shell=True, capture_output=True)
        out = subprocess.run(f"sed -i -e \"s/\\[CLUSTER_NM\\]/{clusterNm}/g\" {clusterNm}/mlocust-app/kubernetes-config/locust-master-controller.yaml", shell=True, capture_output=True)
        out = subprocess.run(f"sed -i -e \"s/\\[CLUSTER_NM\\]/{clusterNm}/g\" {clusterNm}/mlocust-app/kubernetes-config/locust-worker-controller.yaml", shell=True, capture_output=True)

        # Remember we always have to set kubeconfig in case if there's some concurrency issue
        msgs.append(get_credentials(clusterNm, zone))

        # Now apply the yaml files
        msgs.append(get_resp("Apply the yaml files now to the master/workers"))
        out = subprocess.run(f"kubectl apply -f {clusterNm}/mlocust-app/kubernetes-config/locust-master-controller.yaml", shell=True, capture_output=True)
        msgs.append(get_resp(out))
        out = subprocess.run(f"kubectl apply -f {clusterNm}/mlocust-app/kubernetes-config/locust-master-service.yaml", shell=True, capture_output=True)
        msgs.append(get_resp(out))
        out = subprocess.run(f"kubectl apply -f {clusterNm}/mlocust-app/kubernetes-config/locust-worker-controller.yaml", shell=True, capture_output=True)
        msgs.append(get_resp(out))

    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def get_ip(clusterNm, zone):
    msgs = ["Getting external IP"]
    try:
        # Remember we always have to set kubeconfig in case if there's some concurrency issue
        msgs.append(get_credentials(clusterNm, zone))

        # Need to get keep trying till we get an actual external IP
        while True:
            # Not using the python formatted string notation because of the print $NF
            out = subprocess.run("echo \"http://`kubectl get svc locust-master -o yaml | grep ip | awk -F\":\" '{print $NF}' | awk '{$1=$1};1'`:8089\"", shell=True, capture_output=True)
            if out.stdout.decode("utf-8").strip() == "http://:8089":
                msgs.append(get_resp('IP missing. Trying again after 15s.'))
                time.sleep(15)
            else:
                msgs.append(get_resp(out))
                break
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def scale_master(clusterNm, zone, replicas):
    msgs = [f"Scaling the master to {replicas} replicas"]
    try:
        # We can only have 0 or 1 replicas for master
        if replicas>1:
            raise Exception('You cannot have more than 1 master.')
        if replicas<0:
            raise Exception('You cannot have negative masters.')

        # Remember we always have to set kubeconfig in case if there's some concurrency issue
        msgs.append(get_credentials(clusterNm, zone))

        out = subprocess.run(f"kubectl scale deployment/locust-master --replicas={replicas}", shell=True, capture_output=True)
        msgs.append(get_resp(out))
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def scale_workers(clusterNm, zone, currentRPS):
    # We can only have 0 to 39 replicas for workers because we are limiting it to 10 nodes per gke cluster of 4 cpu's each
    # convert rps into workers
    replicas = calc_workers(currentRPS)
    msgs = [f"Scaling the workers to {replicas} replicas"]
    try:
        if replicas>39:
            raise Exception('You cannot have more than 39 workers due to GKE node limitation. Contact eugene.kang@mongodb.com if you need more.')
        if replicas<0:
            raise Exception('You cannot have negative workers.')

        # Remember we always have to set kubeconfig in case if there's some concurrency issue
        msgs.append(get_credentials(clusterNm, zone))

        out = subprocess.run(f"kubectl scale deployment/locust-worker --replicas={replicas}", shell=True, capture_output=True)
        msgs.append(get_resp(out))
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def get_pods(clusterNm, zone):
    msgs = ["Getting pods details"]
    try:
        # Remember we always have to set kubeconfig in case if there's some concurrency issue
        msgs.append(get_credentials(clusterNm, zone))

        out = subprocess.run("kubectl get pods -o wide", shell=True, capture_output=True)
        msgs.append(get_resp(out))
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def cleanup(clusterNm, zone):
    msgs = ["Cleaning up"]
    try:
        # Delete the cluster
        msgs.append(get_resp("Deleting cluster..."))
        out = subprocess.run(f"yes | gcloud container clusters delete {clusterNm} --zone {zone}", shell=True, capture_output=True)
        msgs.append(get_resp(out))

        # Clean up local files
        msgs.append(get_resp("Removing local files"))
        out = subprocess.run(f"rm -rf {clusterNm}", shell=True, capture_output=True)
        out = subprocess.run(f"rm -rf uploads/{clusterNm}", shell=True, capture_output=True)

        # TODO need to clean up the gcr containers
        msgs.append("TODO: Need to clean up the gcr containers eventually")
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def calc_nodes(maxRPS):
    msgs = [f"Calculating nodes from the expected max RPS of {maxRPS}"]
    try:
        # From the max rps expected, calculate the total nodes needed for the cluster
        # We add 1 to the workers to account for the master
        nodes = math.ceil((math.ceil(maxRPS / 1000) + 1)/4)
        msgs.append(get_resp(f"Calculated Nodes: {nodes}"))
        return nodes
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

def calc_workers(currentRPS):
    msgs = [f"Calculating workers from the current RPS of {currentRPS}"]
    try:
        # From the current rps expected, calculate the total workers needed for the cluster
        workers = math.ceil(currentRPS / 1000)
        msgs.append(get_resp(f"Calculated Workers: {workers}"))
        return workers
    except Exception as e:
        msgs.append(get_ex(e))
    return msgs

projectId = "mside-287120"
clusterNm = "abc123"
vmSize = "c2-standard-4"
zone = "us-east4-a"
ttlSecs = 10
maxRPS = 1
currentRPS = 1

#print('Creating Cluster')
#create_cluster(clusterNm, vmSize, zone, maxRPS)

# There is going to be a concurrency issue because if 2 people are working against this same code they will start overwriting each others kubeconfig
# We will need to run this prior to every kubectl command unfortunately and serialize the calls if possible
#print('Setting kubeconfig with cluster credentials')
#get_credentials(clusterNm, zone)

# Now grab sample codes per cluster
# We could potentially have one control plane instance launch 2+ clusters 
#print('Cloning base code for build')
#deploy(projectId, clusterNm, vmSize, zone, maxRPS, currentRPS, ttlSecs)

# Now configure and deploy the master and worker nodes
#print('Configure the master and worker nodes')
#deploy_nodes(projectId, clusterNm, zone)

# Present the External IP so we can access the locust portal
#print('Get External IP')
#get_ip(clusterNm, zone)

#print('Deleting Cluster after TTL (secs)')
#set_delete_cluster(clusterNm, zone, ttlSecs)

# Test scaling
#scale_workers(clusterNm, zone, 2)
#get_pods(clusterNm, zone)

# Test cleanup
#cleanup(clusterNm, zone)
#calc_nodes(34567)

print('done')
