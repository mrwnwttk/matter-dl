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

def get_user_id_from_handle(handle):
	if '@' in handle:
		handle = handle[1:]

	r = requests.get(f'https://api.matter.online/api/preview/users/@{handle}')
	j = json.loads(r.text)
	return j['data']['id'] 

def download_track(key):
	j = json.loads((requests.get(f"https://api.matter.online/api/preview/tracks/{key}")).text)

	url = ""
	filename = ""

	for x in j['included']:
		if not 'login' in x['attributes'].keys():
			if not 'title' in x['attributes'].keys():
				if 'audio' in x['attributes']['mime_type']:
					url = x['attributes']['file_uri']
					filename = x['attributes']['metadata']['original_name']
					break

	if filename != j['data']['attributes']['title']:
		fn = j['data']['attributes']['title']+ "." + filename.split('.')[-1]
		filename = fn

	print(filename)

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

def get_tracks_from_user(user_id):
	page_nr = 1
	return get_tracks_from_user_rec(user_id, 1)


def get_tracks_from_user_rec(user_id, page_nr):
	r = requests.get(f'https://api.matter.online/api/preview/users/{user_id}/tracks?sort=created_at&dir=desc&limit=50&page={page_nr}')
	j = json.loads(r.text)
	track_ids = []

	for x in j['data']:
		if x['type'] == "tracks":
			track_ids.append(x['id'])
	if j['meta']['has_next_page'] == True:
		print("Has another page!")
		return get_tracks_from_user_rec(user_id, page_nr + 1)  + track_ids
	else:
		return track_ids


def download_user(key):
	if not os.path.isdir(key[1:]):
		os.mkdir(key[1:])
	os.chdir(key[1:])

	user_id = get_user_id_from_handle(key)
	tracks = get_tracks_from_user(user_id)

	print(f"Total number of tracks: {tracks}")

	for t in tracks:
		download_track(t)




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
	key = url.split('/')[-1]

	if '/tracks/' in url:
		download_track(key)
	elif '/albums/' in url:
		download_playlist(key)
	elif '@' in url:
		download_user(key)
