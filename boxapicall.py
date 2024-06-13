import argparse
import webbrowser
from boxsdk import OAuth2, Client
from boxsdk.network.default_network import DefaultNetwork
from http.server import HTTPServer, BaseHTTPRequestHandler
import threading
import os

# Configuration
CLIENT_ID = 'ynzl6597waymjajmrqegkqekjcmog7t4'
CLIENT_SECRET = 'xsOjCsLMJkflD2AbQeJkPhAKdu64M42z'
REDIRECT_URI = 'http://localhost:8080'

# Global variable to store the auth code
auth_code = None

# Class to handle the OAuth 2.0 redirect
class OAuthHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        global auth_code
        try:
            auth_code = self.path.split('code=')[1]
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b'You can close this window now.')
        except Exception as e:
            self.send_response(400)
            self.end_headers()
            self.wfile.write(b'Authorization failed. Please check your redirect URI.')

# Function to authenticate using OAuth 2.0
def authenticate_oauth2():
    global auth_code
    oauth2 = OAuth2(
        client_id=CLIENT_ID,
        client_secret=CLIENT_SECRET,
    )

    auth_url, csrf_token = oauth2.get_authorization_url(REDIRECT_URI)
    webbrowser.open(auth_url)

    # Start a local server to handle the OAuth 2.0 redirect
    httpd = HTTPServer(('localhost', 8080), OAuthHandler)
    httpd_thread = threading.Thread(target=httpd.handle_request)
    httpd_thread.start()
    httpd_thread.join()

    if auth_code:
        # Fetch the access token using the auth code
        access_token, refresh_token = oauth2.authenticate(auth_code)
        return oauth2
    else:
        print("Failed to retrieve authorization code.")
        return None

# Function to upload a file
def upload_file(client, folder_id, file_path):
    try:
        folder = client.folder(folder_id).get()
        new_file = folder.upload(file_path)
        print(f'File "{new_file.name}" uploaded to Box with file ID {new_file.id}')
        return "SUCCESS"
    except Exception as e:
        print(f"Failed to upload file: {e}")
        return "FAILURE"

# Function to list files in a folder
def list_files(client, folder_id):
    try:
        folder = client.folder(folder_id).get()
        items = folder.get_items()
        for item in items:
            if item.type == 'file':
                print(f'File: {item.name}, ID: {item.id}')
        return "SUCCESS"
    except Exception as e:
        print(f"Failed to list files: {e}")
        return "FAILURE"

# Function to list directories in a folder
def list_directories(client, folder_id):
    try:
        folder = client.folder(folder_id).get()
        items = folder.get_items()
        directories = [item for item in items if item.type == 'folder']
        for directory in directories:
            print(f'Directory: {directory.name}, ID: {directory.id}')
        return "SUCCESS"
    except Exception as e:
        print(f"Failed to list directories: {e}")
        return "FAILURE"

# Recursive function to list all directories in Box
def list_all_directories(client, folder_id='0'):
    try:
        folder = client.folder(folder_id).get()
        items = folder.get_items()
        directories = [item for item in items if item.type == 'folder']
        for directory in directories:
            print(f'Directory: {directory.name}, ID: {directory.id}')
            list_all_directories(client, directory.id)
        return "SUCCESS"
    except Exception as e:
        print(f"Failed to list all directories: {e}")
        return "FAILURE"

# Function to download a file
def download_file(client, file_id, download_path):
    try:
        box_file = client.file(file_id).get()
        # Ensure the download path includes the filename if it's a directory
        if os.path.isdir(download_path):
            download_path = os.path.join(download_path, box_file.name)
        with open(download_path, 'wb') as file:
            box_file.download_to(file)
        print(f'File "{box_file.name}" downloaded from Box to "{download_path}"')
        return "SUCCESS"
    except Exception as e:
        print(f"Failed to download file: {e}")
        return "FAILURE"

# Main function to handle CLI arguments
def main():
    parser = argparse.ArgumentParser(description="Interact with Box API")
    
    # Define the subcommands
    subparsers = parser.add_subparsers(dest='command', help='Sub-command help')
    
    # Subcommand for uploading a file
    upload_parser = subparsers.add_parser('upload', help='Upload a file to Box')
    upload_parser.add_argument('folder_id', type=str, help='ID of the folder to upload the file to')
    upload_parser.add_argument('file_path', type=str, help='Path of the file to upload')
    
    # Subcommand for listing files in a folder
    list_parser = subparsers.add_parser('list', help='List files in a Box folder')
    list_parser.add_argument('folder_id', type=str, help='ID of the folder to list files from')

    # Subcommand for listing directories in a folder
    list_dirs_parser = subparsers.add_parser('list_dirs', help='List directories in a Box folder')
    list_dirs_parser.add_argument('folder_id', type=str, help='ID of the folder to list directories from')

    # Subcommand for listing all directories in Box recursively
    list_all_dirs_parser = subparsers.add_parser('list_all_dirs', help='List all directories in Box recursively')

    # Subcommand for downloading a file
    download_parser = subparsers.add_parser('download', help='Download a file from Box')
    download_parser.add_argument('file_id', type=str, help='ID of the file to download')
    download_parser.add_argument('download_path', type=str, help='Path where the file should be downloaded')

    # Parse the arguments
    args = parser.parse_args()

    # Authenticate using OAuth 2.0
    oauth2 = authenticate_oauth2()
    if oauth2:
        client = Client(oauth2)

        # Execute the appropriate function based on the command
        if args.command == 'upload':
            result = upload_file(client, args.folder_id, args.file_path)
            print(result)
        elif args.command == 'list':
            result = list_files(client, args.folder_id)
            print(result)
        elif args.command == 'list_dirs':
            result = list_directories(client, args.folder_id)
            print(result)
        elif args.command == 'list_all_dirs':
            result = list_all_directories(client)
            print(result)
        elif args.command == 'download':
            result = download_file(client, args.file_id, args.download_path)
            print(result)

if __name__ == '__main__':
    main()