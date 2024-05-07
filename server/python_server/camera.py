import requests

def download_jpg(url, file_path):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        # Check if the request was successful (status code 200)
        if response.status_code == 200:
            # Open the file in binary write mode and write the content of the response
            with open(file_path, 'wb') as f:
                f.write(response.content)
            print("Download successful")
        else:
            print("Failed to download:", response.status_code)
    except Exception as e:
        print("An error occurred:", e)