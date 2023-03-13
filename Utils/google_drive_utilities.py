import io
import os
from googleapiclient import discovery
from httplib2 import Http
from oauth2client import file, client, tools
from googleapiclient.discovery import build
from tabulate import tabulate
from googleapiclient.errors import HttpError
from googleapiclient.http import MediaIoBaseDownload


"""
This file contains useful functions that can be used to interact with your google drive data using the Google Drive API (v3). 
NOTE: We assume that you have followed all necessary steps to set up your oauth2 Client using the Google Developer Console.
Follow instructions described here to do so: https://developers.google.com/drive/api/quickstart/python
Additional Help: https://hansheng0512.medium.com/download-folders-and-files-using-google-drive-api-and-python-1ad086e769b
"""

def confirm_connection_and_obtain_token(path_to_creds_json):
  """
  Confirms connection to a Google Drive account and obtains an access token for it.

  Args:
      path_to_creds_json (str): The file path to the credentials JSON file for the Google Drive oauth Client.

  Returns:
      credentials needed for future interactions with the Google Drive API.
  """
  # Create an object to store attributes
  obj = lambda: None
  # Define the attributes for authorization
  lmao = {"auth_host_name":'localhost', 'noauth_local_webserver':'store_true', 'auth_host_port':[8080, 8090], 'logging_level':'ERROR'}
  # Set the attributes for the object
  for k, v in lmao.items():
      setattr(obj, k, v)

  # Set the authorization scope
  SCOPES = 'https://www.googleapis.com/auth/drive.readonly'
  # Create a storage object for storing the access token
  store = file.Storage('token.json')
  # Get the access token
  creds = store.get()
  # If the access token is invalid or does not exist
  if not creds or creds.invalid:
      # Create a flow object from the client secrets file and the authorization scope
      flow = client.flow_from_clientsecrets(path_to_creds_json, SCOPES)
      # Run the flow to obtain the access token and store it in the storage object
      creds = tools.run_flow(flow, store, obj)
  
  # You should now have a token.json file.
  return creds

  
def search_file(name, creds):
  """
  This function allows you to search for a file within your Google Drive, directly using its name. In case there are duplicate file names,
  the function will return the file which is the largest in size.

  Args:
    name (str): The file name you want to search for.
    creds (google.oauth2.credentials.Credentials): The Google Drive API credentials to use.
  """
    
  try:
      # Build the Drive API client with the given credentials
      service = build('drive', 'v3', credentials=creds)

      # Initialize an empty list to hold the matching files
      files = []
      # Initialize the page token to None
      page_token = None

      # Loop until all pages of search results have been processed
      while True:
          # Make the API request to search for files with the given name
          response = service.files().list(q="name = '" + name + "'",
                                          spaces='drive',
                                          fields='nextPageToken, '
                                                 'files(id, name, size)',
                                          pageToken=page_token).execute()

          # Print out the name and ID of each file found
          for file in response.get('files', []):
              print(F'Found file: {file.get("name")}, {file.get("id")}')

          # Add the files found in this page to the files list
          files.extend(response.get('files', []))

          # Get the page token for the next page of search results, if any
          page_token = response.get('nextPageToken', None)
          if page_token is None:
              # Break out of the loop if there are no more pages
              break

  except HttpError as error:
      # If there's an error with the API request, print the error and set files to None
      print(F'An error occurred: {error}')
      files = None

  # If multiple files were found with the same name, return the one with the largest size
  max_item = max(files, key=lambda x: int(x['size']))
  return [max_item]


def download_file(file_id, file_name, destination_folder_path, creds):
  """
  Downloads a file from Google Drive with the given file ID and saves it to the specified destination folder path with the given file name.

  Args:
    file_id (str): The ID of the file to download.
    file_name (str): The name of the file to save.
    destination_folder_path (str): The path of the folder where the file should be saved.
    creds: Google Drive API credentials.

  Returns:
    None
  """
  # Check if the file already exists in the destination folder
  if os.path.exists(destination_folder_path + file_name):
      print(file_name, "already exists; skipping the download")
      return

  try:
      # Create a Google Drive API client service
      service = build('drive', 'v3', credentials=creds)

      # Create a media request for the file with the given ID
      request = service.files().get_media(fileId=file_id)

      # Create a BytesIO object to hold the downloaded file data
      file = io.BytesIO()

      # Create a downloader instance that will write the downloaded data to the BytesIO object
      downloader = MediaIoBaseDownload(file, request)

      done = False
      print("Downloading:", file_id, "name:", file_name)

      # Download the file in chunks until the download is complete
      while done is False:
          status, done = downloader.next_chunk()
          print(F'Download {int(status.progress() * 100)}.')

      # Write the downloaded content to a file in the destination folder
      with open(destination_folder_path + file_name, 'wb') as f:
          f.write(file.getvalue())

  except HttpError as error:
      print(F'An error occurred: {error}')
      file = None

  print("Done downloading!", file_name)
