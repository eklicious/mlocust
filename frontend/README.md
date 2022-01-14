To deploy changes to the front-end in REALM - here are the steps I recommend.

1. Delete ALL of the files in the 'hosting' directory & Press 'Save & Deploy'
2. cd into the 'mlocust-web' directory, and run 'rm -rf ./build' && then run 'npm run build'
3. In the REALM UI, press 'upload files' - and upload the files. Please note you will have to manually re-create the folder structure.
(folder structure = static/js, static/css, static/media, ./)
4. After everything has been uploaded, press 'SAVE & DEPLOY'
