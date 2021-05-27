from pydrive.drive import GoogleDrive
from pydrive.auth import GoogleAuth

import os
import dotenv


# Backs up all of the images (memes) to google drive once a day

# Initialize and load the memes and credentials environment variables
dotenv.load_dotenv()
MEMES_PATH = os.getenv('MEMES_FOLDER')
CREDENTIALS = os.getenv('CREDENTIALS')

# Create a new authentication system and attempt to load credentials from file
AUTH = GoogleAuth()
AUTH.LoadCredentialsFile(CREDENTIALS)

# If the credentials failed to load from file authenticate with teh web server
if AUTH.credentials is None:
    AUTH.LocalWebserverAuth()

# If the token was just expired then refresh it and continue
elif AUTH.access_token_expired:
    AUTH.Refresh()

# Otherwise just authorize like normal
else:
    AUTH.Authorize()

# Then be sure to save these new credentials for next time and create new drive instance
AUTH.SaveCredentialsFile(CREDENTIALS)
DRIVE = GoogleDrive(AUTH)

# Get the root folder of the database backup that we need to parent new folders to
DATABASE_ROOT = DRIVE.ListFile({'q': "title = 'Bruh Bot Database' and trashed = false"}).GetList()[0]

# Iterate over everyone's meme folder to get to their memes
for directory in os.listdir(MEMES_PATH):

    # Query google drive and check to make sure the file is not already present
    duplication = DRIVE.ListFile({'q': f"title = '{directory}' and trashed = false"}).GetList()

    # If the query was empty then we have a new user and need to create a new directory for them in Google Drive
    if not duplication:
        folder = DRIVE.CreateFile({
            'title': directory,
            'parents': [{'id': DATABASE_ROOT['id']}],
            'mimeType': 'application/vnd.google-apps.folder'
        })
        folder.Upload()

    # Otherwise we need to just grab the pre-existing folder
    else:
        folder = duplication[0]

    # Now we need to iterate over everyone's memes and upload them into their person's folder
    for file in os.listdir(os.path.join(MEMES_PATH, directory)):
        
        # Query the Google Drive folder and assume this file is unique
        file_duplication = DRIVE.ListFile({'q': f"title = '{file}' and trashed = false"}).GetList()
        unique_file = True

        # Then iterate over every parent of every matching file to make sure this file is unique
        for duplicate_file in file_duplication:
            for parent in duplicate_file['parents']:
                if parent['id'] == folder['id']:
                    unique_file = False

        # If the query was empty then we know that the file needs to uploaded into their parent folder
        if unique_file:
            upload = DRIVE.CreateFile({'title': file, 'parents': [{'id': folder['id']}]})
            upload.SetContentFile(os.path.join(MEMES_PATH, directory, file))
            upload.Upload()
