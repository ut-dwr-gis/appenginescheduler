# App Engine Scheduler

This app engine application is designed to retrieve data from an oracle database on a schedule and pipeline the data to big query. Due to long running queries (over an hour) cloud function and cloud run could not be used. When using a backend app engine instance scripts may run for up to 24 hours. These queries each take between 1 and 4 hours. This script is kept cost effective by having the scheduled scripts straddle the free-tier reset time of midnight. Short running queries are stacked, one particularly long running query starts on Saturday and runs through into Sunday. All scripts start after close of business Friday and complete before open of business Monday. 

For you to run this script you will need to create an "env.py" script in the root folder (same as main.py). This script will contain your oracle (or other) connection file in the following format:

```
import oracledb
conn = oracledb.connect(
            user='username in quotes',
            password='password in quotes',
            host='hostname can be the webaddress or ip address of the service (in quotes)',
            port=1521,
            service_name='servicename in quotes'
      )

```

To redeploy in the biobase-dev GCP project:
Open computer terminal/PowerShell.  

```
# Make sure gcloud CLI is installed on your system.
gcloud version

# If CLI is not installed run:
(New-Object Net.WebClient).DownloadFile("https://dl.google.com/dl/cloudsdk/channels/rapid/", "$env:Temp\GoogleCloudSDKInstaller.exe")
& $env:Temp\GoogleCloudSDKInstaller.exe
```
For first-time setup you may need to navigate to the Registry Editor on your machine and find:
HKEY_LOCAL_MACHINE->SOFTWARE->Microsoft->PowerShell->1->ShellIds->Microsoft_PowerShell
Add an item by right clicking and selecting 
New->String Value 
Name it "ExecutionPolicy" then Double click the new item and add value = "RemoteSigned".

Additional setup steps:
```
gcloud init #sign in, set project, set region
gcloud auth application-default login
```

Finally, clone this repo in a local directory with the custom modified env.py file, then deploy in PowerShell. 
```
cd C:\Users\exampleName\Documents\bioticsscheduler
git clone https://github.com/ut-dwr-gis/appenginescheduler.git
cd .\appenginescheduler\ #Confirm correct files are listed
git pull
gcloud app deploy ./app.yaml #Configure app and deployment
gcloud app deploy ./cron.yaml #Need this after app.yaml deployment to update cron jobs
```

