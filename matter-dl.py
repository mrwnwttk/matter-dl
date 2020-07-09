import os
import sys
import json
import requests

def create_folder_from_key(key):
	folder_name = get_album_name_from_key(key)
	if not os.path.isdir(folder_name):
		os.mkdir(folder_name)
	return folder_name

def get_album_name_from_key(key):
	j = json.loads((requests.get(f"https://api.matter.online/api/preview/albums/{key}")).text)
	return j['data']['attributes']['title']

def download_track(key):
	j = json.loads((requests.get(f"https://api.matter.online/api/preview/tracks/{key}")).text)

	url = ""
	filename = ""

	for x in j['included']:
		if not 'login' in x['attributes'].keys():
			if not 'title' in x['attributes'].keys():
				if 'audio' in x['attributes']['mime_type']:
					print(x['attributes']['file_uri'])
					print(x['attributes']['metadata']['original_name'])
					url = x['attributes']['file_uri']
					filename = x['attributes']['metadata']['original_name']
					break

	r = requests.get(url)
	with open(filename, "wb") as f:
		f.write(r.content)

def download_playlist(key):
	f = create_folder_from_key(key)
	os.chdir(f)	

	r = requests.get("https://api.matter.online/api/preview/albums/{}".format(key))
	j = json.loads(r.text)
	tracks = []
	for x in j['included']:
		if x['type'] == 'tracks':
			tracks.append(x['id'])

	for key in tracks:
		download_track(key)

def get_keys_from_album(url):
	key = url.split('/')[4]
	r = requests.get("https://api.matter.online/api/preview/albums/{}".format(key))
	j = json.loads(r.text)
	tracks = []
	for x in j['included']:
		if x['type'] == 'tracks':
			tracks.append(x['id'])
	return tracks

if __name__ == '__main__':
	url = sys.argv[1]
	key = url.split('/')[4]

	if '/tracks/' in url:
		download_track(key)
	elif '/albums/' in url:
		download_playlist(key)
