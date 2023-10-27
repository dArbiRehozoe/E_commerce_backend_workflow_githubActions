import requests
import os
TAG_TO_REPLACE = os.environ.get("TAG_TO_REPLACE","0.2")
DOCKERHUB_USERNAME = os.environ.get("DOCKERHUB_USERNAME")
DOCKERHUB_REPO = os.environ.get("DOCKERHUB_REPO","testpush")
DOCKERHUB_TOKEN = os.environ.get("DOCKERHUB_TOKEN")
DOCKERHUB_PASSWORD = os.environ.get("DOCKERHUB_PASSWORD")




# Obtenez l'ID de l'image existante avec le tag à remplacer
url = f"https://hub.docker.com/v2/repositories/{DOCKERHUB_USERNAME}/{DOCKERHUB_REPO}/tags/{TAG_TO_REPLACE}/"
headers = {
    "Authorization": f"Bearer {DOCKERHUB_TOKEN}"
}
response = requests.get(url, headers=headers)

urllogin = f"https://hub.docker.com/v2/users/login/"
data = {
    "username":DOCKERHUB_USERNAME,
    "password":DOCKERHUB_PASSWORD
    }
responselogin = requests.post(urllogin, data=data)
print(responselogin)

if response.status_code == 200:
    image_id = response.json()["id"]
    print(f"ID de l'image Docker existante avec le tag '{TAG_TO_REPLACE}': {image_id}")

    # Supprimez le tag existant
    url = f"https://hub.docker.com/v2/repositories/{DOCKERHUB_USERNAME}/{DOCKERHUB_REPO}/tags/{TAG_TO_REPLACE}/"
    response = requests.delete(url, headers={
        "Content-Type":"application/json",
        "Authorization": f"JWT {responselogin.json()['token']}"
    })

    if response.status_code == 204:
        print(f"Tag '{TAG_TO_REPLACE}' supprimé avec succès.")
else:
    print(f"Erreur lors de la récupération de l'ID de l'image: {response.status_code}")
