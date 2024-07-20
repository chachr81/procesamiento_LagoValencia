import json
import requests
import datetime

def send_request(url, data, api_key=None):
    headers = {'Content-Type': 'application/json'}
    if api_key:
        headers['X-Auth-Token'] = api_key
    response = requests.post(url, json=data, headers=headers)
    response_data = response.json()
    if response.status_code != 200 or 'errorCode' in response_data:
        print("Error:", response_data.get('errorCode'), response_data.get('errorMessage'))
        return None
    return response_data['data']

def download_file(url, path):
    response = requests.get(url, stream=True)
    filename = response.headers.get('content-disposition').split('filename=')[1].strip('"')
    full_path = f"{path}/{filename}"
    with open(full_path, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)
    print(f"Downloaded {filename} to {path}")

if __name__ == '__main__':
    service_url = "https://m2m.cr.usgs.gov/api/api/json/stable/"
    download_path = "C:\\Workspace\\LagoValencia\\raster\\"  # Adjust your download path accordingly

    # Insert your Earth Explorer credentials here
    username = 'chachr'
    password = 'Matrix00'

    # Login
    login_payload = {'username': username, 'password': password}
    api_key = send_request(service_url + "login", login_payload)
    if not api_key:
        print("Failed to login")
        exit()

    # Define search criteria
    dataset_name = "LANDSAT_8_C1"
    path_row_filter = {
        'filterType': 'and', 
        'childFilters': [
            {'filterType': 'value', 'fieldId': 20530, 'value': '004'},  # WRS Path
            {'filterType': 'value', 'fieldId': 20531, 'value': '053'}   # WRS Row
        ]
    }
    date_filter = {
        'start': '2020-01-01',
        'end': '2020-12-31'
    }

    # Search for scenes
    search_payload = {
        'datasetName': dataset_name,
        'spatialFilter': path_row_filter,
        'temporalFilter': date_filter
    }
    scenes = send_request(service_url + "scene-search", search_payload, api_key)
    if scenes and scenes['recordsReturned'] > 0:
        print(f"Found {scenes['recordsReturned']} scenes")
        # Example: download first scene
        scene_id = scenes['results'][0]['entityId']
        download_url = service_url + f"download/{scene_id}"
        download_file(download_url, download_path)
    else:
        print("No scenes found")

    # Logout
    send_request(service_url + "logout", {}, api_key)
    print("Logged out successfully")
