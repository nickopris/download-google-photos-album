### Download Images from Google Photos using Python



## Used Libraries and Tools

* Python: 
    * Http
    * googleapiclient
    * apiclient
    * oauth2client
    * google.auth

## Start the project
 - Create a virtual environment `python3 -m venv venv`, activate it `source venv/bin/activate` and install requirements `pip install -r requirements.txt`
 
## Get Google credentials
    - Enable Google API
    - Enable Google Photos API Service
    - Go to the Google API Console https://console.cloud.google.com/.
    - From the menu bar, select a project or create a new project.
    - To open the Google API Library, from the Navigation menu, select APIs & Services > Library.
    - Search for "Google Photos Library API". Select the correct result and click "enable". If its already enabled, click "manage"
    - Afterwards it will forward you to the "Photos API/Service details" page (https://console.cloud.google.com/apis/credentials)
    - Configure "OAuth consent screen" (Source)
    - Go back to the Photos API Service details page and click on "OAuth consent screen" on the left side (below "Credentials")
    - Add a Test user: Use the email of the account you want to use for testing the API call
    - Create API/OAuth credentials
    - On the left side of the Google Photos API Service page, click Credentials
    - Click on "Create Credentials" and create a OAuth client ID
    - As application type I am choosing "Desktop app" and give your client you want to use to call the API a name
    - Download the JSON file to the created credentials, rename it to "client_secret.json" and save it in the folder "credentials"


## License
[MIT](https://choosealicense.com/licenses/mit/)