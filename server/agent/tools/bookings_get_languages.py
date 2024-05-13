import requests

url = "https://booking-com15.p.rapidapi.com/api/v1/meta/getLanguages"

headers = {
	"X-RapidAPI-Key": "acc52c4778msh49ffb4b3e136ab7p1dc71bjsna7a6c0f2d13c",
	"X-RapidAPI-Host": "booking-com15.p.rapidapi.com"
}

response = requests.get(url, headers=headers)

print(response.json())