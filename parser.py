import request
from bs4 import BeautifulSoup

url = "https://habr.com/ru/articles/"

response = requests.get(url)

soup = BeautifulSoup(response.text, "html.parser")

titles = soup.select("a.tm-title__link")
for i, title in enumerate(titles, 1):
    print(f"{i}. {title.text} ({title['href']})")