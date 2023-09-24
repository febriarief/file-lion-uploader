import argparse, json, os, re, requests
from tqdm import tqdm

API_KEY = "YOUR_API_KEY"

def download_video(url, filename="video.mp4", save_dir="./"):
    response = requests.get(url, stream=True)    
    save_path = os.path.join(save_dir, filename)
    total_size = int(response.headers.get('content-length', 0))

    with open(save_path, 'wb') as file, tqdm(
        desc=f"Downloading {filename}",
        total=total_size,
        unit='B',
        unit_scale=True,
        unit_divisor=1024,
        ascii=True,
    ) as bar:
        for data in response.iter_content(chunk_size=1024):
            file.write(data)
            bar.update(len(data))
    
    return save_path

def get_upload_url(api_url):
    response = requests.get(api_url)
    data = response.json()
    if data.get('result'):
        return data['result']
    else:
        print("Failed to get upload URL from the server.")
        return None

def upload_file(upload_url, file_path):
    files = {'file': open(file_path, 'rb')}
    payload = {'key': API_KEY, 'fld_id': 9601}

    response = requests.post(upload_url, files=files, data=payload)
    os.remove(file_path)

    return response.json()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Download and upload a video.")
    parser.add_argument("--url", required=True, help="URL of the video to download")
    parser.add_argument("--filename", required=True, help="Filename of video")
    args = parser.parse_args()

    video_url = args.url
    filename = args.filename
    
    print("Step 1: Downloading video...")
    path = download_video(video_url, filename)

    api_url = "https://api.filelions.com/api/upload/server?key={}".format(API_KEY)
    print("\nStep 2: Getting upload URL from the server...")
    upload_url = get_upload_url(api_url)
    
    if upload_url:
        print("\nStep 3: Uploading video...")
        response = upload_file(upload_url, path)
        print("\nUpload response:")
        print(response)
    else:
        print("Upload process aborted due to missing upload URL.")
