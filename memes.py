import requests
import json
import config
import psycopg2 as cop

con = cop.connect(host="localhost", database="sa_images", user="postgres", password="postgres")

print("DB connected!")
cur = con.cursor()

def meme_db(thread):
    request = thread.split()[0]
    db.get_img(str(request[1:]))
    cur.execute("SELECT url FROM {0} ORDER BY RANDOM() LIMIT 1".format(thread))
    img = cur.fetchone()

    return img[0]

def cat_pic(x):
    if x == "neb":
        cat_search = f"https://api.thecatapi.com/v1/images/search?breed_ids=nebe&api_key={config.cat_auth}"
        cat = json.loads(requests.get(cat_search).text)[0]["url"]
    elif x == "catgif":
        cat_search = f"https://api.thecatapi.com/v1/images/search?mime_types=gif&api_key={config.cat_auth}"
        cat = json.loads(requests.get(cat_search).text)[0]["url"]
    elif x == "cat":
        cat_search = f"https://api.thecatapi.com/v1/images/search?&api_key={config.cat_auth}"
        cat = json.loads(requests.get(cat_search).text)[0]["url"]
    elif x == "catfact":
        cat_fact = json.loads(requests.get('https://meowfacts.herokuapp.com').text)["data"]
        cat = ((str(cat_fact)).strip("'[]'"))

    return cat

def dog_pic():
    dog_search = f"https://api.thedogapi.com/v1/images/search?api_key={config.dog_auth}"
    dog_pic = json.loads(requests.get(dog_search).text)[0]["url"]

    return dog_pic

def waffle_pic():
    waffles = 'https://randomwaffle.gbs.fm/'
    image = BeautifulSoup(requests.get(waffles).content, 'html.parser').find('img').attrs['src']

    return (waffles+image)