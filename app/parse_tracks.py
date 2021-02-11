import requests
from urllib.parse import quote
import pathlib
from time import sleep
import json
import re
import os

from yamusic.parse import Download
from yamusic.get_tracks import TrackInfo


base_dir = pathlib.PosixPath(os.path.dirname(__file__)) / "Dataset"


def format_url(name, page):
	template = "https://music.yandex.ru/genre/{}/tracks/popular?page={}"
	return template.format(quote(name), str(page))


categories = [
	("рок-музыка", 20),
	("поп", 20),
	("альтернатива", 5),
	("рэп и хип-хоп", 20),
	("панк", 7),
	("эстрада", 10),
	("шансон", 10),
	("метал", 10),
	("инди", 5),
	("электроника", 10),
]

m = Download(login="jsdadfhklsad", password="jsdadfhklsad234dfDfDa$erdf")

count = 0



# for genre_name, k in categories:
# 	for number in range(k):
# 		url = format_url(genre_name, number)
# 		# print(url)
# 		data = requests.get(url).text
# 		all_tracks.append(["https://music.yandex.ru" + i for i in re.findall(r"\/album\/[0-9]+\/track\/[0-9]+", data)])

					

with open(base_dir / "tracks.txt") as log:
	data = json.loads(log.read())


for url in data:
	album, track = re.findall(r"([0-9]+)\/track\/([0-9]+)", url)[0]
	# print(track, album)
	# try:
	info = TrackInfo(album, track).get_all()
	link = m.get_music(track, album, info["author_id"])
	
	r = requests.post("http://vmi456545.contaboserver.net:5000", json={"url": link, "meta": info})

	if r.status_code == 200:
		print("[+] Success")
	else:
		raise KeyboardInterrupt

	# except KeyboardInterrupt:
	# 	raise KeyboardInterrupt
	# except:
	# 	print("[-] --Bad--")
	# count += 1