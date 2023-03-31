from httplib2 import Http
from datetime import datetime
from googleapiclient import discovery
from apiclient.discovery import build
from oauth2client import file, client, tools
from google.auth.transport.requests import Request
import urllib.request, os, json, requests, filedate

def doAuth():
    # Authentication
    SCOPES = 'https://www.googleapis.com/auth/photoslibrary.readonly'
    store = file.Storage('credentials/credentials.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials/client_secret.json', SCOPES)
        creds = tools.run_flow(flow, store)
    return discovery.build('photoslibrary', 'v1', http=creds.authorize(Http()), static_discovery=False)
    
def getAlbum(service):
    # Albums
    hasNextPageToken = False
    nextPageToken = ""
    albums = {}
    results = service.albums().list(pageSize=50).execute()
    counter = 0;
    if 'nextPageToken' in results:
        hasNextPageToken = True
        nextPageToken = results['nextPageToken']
        for album in results['albums']:
            albums[counter] = {'id': album['id'], 'title': album['title']}
            print(counter, ' - ', album['title'])
            counter +=1

    album_id = input("Enter album index: ")
    albumId = albums[int(album_id)]['id']
    albumTitle = albums[int(album_id)]['title']
    
    return {'id': albumId, 'title': albumTitle}

def loadAlbumIndex(service, albumId):
    # Get files in chosen album
    hasNextPageToken = True
    nextPageToken = ""
    finalData = {}

    while hasNextPageToken:
        body = {
            "albumId": albumId,
            "pageSize": 100,
            "pageToken" : nextPageToken
            }
        results = service.mediaItems().search(body=body).execute()

        for key in results['mediaItems']:
            url = key['baseUrl'] + "=d"
            if key['mimeType'] == 'video/mp4':
                url = key['baseUrl']+ "=dv"
            finalData[key['id']] = {'filename': key['filename'], 
                                    'url': url, 
                                    'date': key['mediaMetadata']['creationTime']}

        # Write to index file
        sorted_dict = dict(sorted(finalData.items(), key=lambda x: datetime.fromisoformat(x[1]['date'].removesuffix('Z')).timestamp()))

        json.dump(sorted_dict, open("index.json",'w'))

        if 'nextPageToken' in results.keys():
            nextPageToken = results['nextPageToken']
        else:
            hasNextPageToken = False
    
service = doAuth()

isIndex = os.path.exists('index.json')
download_continue = 'n'
if isIndex:
    download_continue = input("There is an incomplete download. Would you like to continue? (y/n) ") or 'y'
        
if download_continue == 'n':
    album = getAlbum(service)
    json.dump(album, open("album.json",'w'))

    print("Fetching album index for album: ", album['title'])
    loadAlbumIndex(service, album['id'])
else:
    with open('album.json') as f:
        data = f.read()
    album = json.loads(data)
    print("Continue downloading the album: ", album['title'])

# Open index file and get the files        
with open('index.json') as f:
    data = f.read() 
# Reconstructing the data from the index file as a dictionary
js = json.loads(data)

# Check if the destination folder is there or make it
destination_folder = './downloads/' + album['title'] + '/'
isExist = os.path.exists(destination_folder)
if not isExist:
    os.makedirs(destination_folder)

# Iterate, check and fetch files
for item in js:
    print("Checking: ", js[item]['filename'])
    # Also check if existing file is the same size - could be an interrupted download.
    url = js[item]['url']
    file_name = js[item]['filename']
    full_file_destination = os.path.join(destination_folder, file_name)
    if os.path.isfile(full_file_destination) == False:
        print("Downloading: ", js[item]['filename'])
        response = requests.get(url)
        with open(full_file_destination, 'wb') as f:
            f.write(response.content)
            f.close()
        a_file = filedate.File(full_file_destination)
        a_file.set(created = js[item]['date'], modified = js[item]['date'], accessed = js[item]['date'])
    else:
        try:
            rfile = urllib.request.urlopen(url)
        except:
            print ('Probably a HTTPError because the link tokens are too old or the program was interrupted.')
            exit()
        meta = rfile.info()
        rfile_size = meta['Content-Length']
        lfile_stats = os.stat(full_file_destination)
        lfile_size = lfile_stats.st_size
        if(int(rfile_size) != int(lfile_size)):
            print("Re-downloading: ", js[item]['filename'], ' R:', rfile_size, ' L:', lfile_size)
            response = requests.get(url)
            with open(full_file_destination, 'wb') as f:
                f.write(response.content)
                f.close()
            a_file = filedate.File(full_file_destination)
            a_file.set(created = js[item]['date'], modified = js[item]['date'], accessed = js[item]['date'])

# Get rid of the index and album files
# os.popen('cp index.json ' + destination_folder + 'index.json') 
os.remove('index.json')
os.remove('album.json')