DESCRIPTION:
This is the front-end Python Flask application that handles the re/deployment of the Locust app to a GKE cluster.

PREREQUISITES:
Before you get started, you need to set up Google so you can run the api calls: https://cloud.google.com/docs/authentication/getting-started.
You will most likely have to enable the nlp api when you execute the script. It basically gives you a URL to go to.

LOCAL DEVELOPMENT:
You'll need to install cli's and tools by following the steps inside of run.sh excluding the last step that tries to run flask. You only need to set up the venv and pip install once if nothings changed with the requirements file.

python3 -m venv mlocust-env 
source mlocust-env/bin/activate
python -m pip install -r requirements.txt
flask run
deactivate

PRE-DEPLOYMENT:
Note that there's an issue where I can't get a POST response for an initial deployment because I think it takes too long and Flask is timing out or something.
docker build -t mlocust .
dockerun -p 5000:5000 mlocust

DEPLOYMENT:
gcloud builds submit --tag gcr.io/mside-287120/mlocust
Go to https://console.cloud.google.com/run and create a new service
	Select the mlocust container image
	Pick a low c02 region :)
	min/max instances: 1/1
	Advanced Settings:
		Container port: 5000
		Capacity > Memory: 1 GiB
		Request timeout: 500 secs
	Authentication: Allow unauthenticated invocations
	Find the run.app url and launch. It'll be port 80 by default.

OUTSTANDING STUFF:
1. Add Google SSO auth via Realm to the python app
	Figure out how to make cluster names unique so folks don't conflict, e.g. prefix cluster names with the authenticated users email
	Update MDB auditing to include email for userId field after Google auth done
2. Consolidate the upload locust/reqts file into a multi-upload so we don't have to do it twice.
3. When the user executes anything, put up a modal hour glass till the operation completes.
4. Update the other mlocust sample app project to add a really good pyfaker example to the locustfile.py
5. Do we bother removing all the private key files from the container, e.g. Docker secrets (https://medium.com/trabe/use-your-local-ssh-keys-inside-a-docker-container-ea1d117515dc) or https://stackoverflow.com/questions/18136389/using-ssh-keys-inside-docker-container
6. Migrate off of my personal account: 
	Figure out which project / service account / orgs / etc. to use, e.g. noc account
	Generate a service account private key file
	The service account needs all api's enabled which is a 1 time thing.
7. Ability to deploy the k8s clusters in other clouds. This is harder because we'd have to maintain separate scripts specific to each cloud.
8. Add the ability to pull existing templates, e.g. {author:, desc:, body:}, from our db that people can select to dynamically create a pyfaker locust file to load specific types of data, e.g. pharma.
9. How to scale this so new SAs and Mgrs are aware of this tool? Add to global trello boards?
