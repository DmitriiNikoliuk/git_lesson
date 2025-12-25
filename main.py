from bs4 import BeautifulSoup

with open("test.html", encoding="utf-8") as file:
    html = file.read()
    soup = BeautifulSoup(html, "lxml")
    
products = soup.find_all("div", class_ = "product")
# print(products)
for product in products:
    name = product.find("h2", class_ = "name").text
    price = product.find("p", class_ = "price").text 
    link = product.find("a", class_ = "details").get("href")
    image = product.find("img", class_ = "product-image").get("src") 
    print(name, price, link, image)
