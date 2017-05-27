from model import Users
from flask import Flask, render_template, request
from peewee import create_model_tables
from bs4 import BeautifulSoup as bs
import yagmail
import requests
from selenium import webdriver


app = Flask(__name__)
yag = yagmail.SMTP("your_email_id", "password")


def setup_db():
    create_model_tables([Users], fail_silently=True)

setup_db()


def jabong_find_price(url):
    # response = urllib.request.urlopen(url)
    r = requests.get(url)
    html = r.content
    soup = bs(html, 'html.parser')
    price = soup.find('span', {'class': 'actual-price'}).text
    product_brand = soup.find('span', {'class': 'brand'}).text
    product_title = soup.find('span', {'class': 'product-title'}).text
    product_info = {}
    product_info['price'] = price
    product_info['product_brand'] = product_brand
    product_info['product_title'] = product_title
    return product_info


def amazon_find_price(url):
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/54.0.2840.71 Safari/537.36'}
    r = requests.get(url, headers=headers)
    html = r.content
    soup = bs(html, 'html.parser')
    price = soup.find('span', {'class': 'a-size-medium a-color-price'}).text
    product_title = soup.find('span', {'id': 'productTitle'}).text
    price = price.strip()
    price = price.replace(',','')
    product_title = product_title.strip()
    product_info = {}
    product_info['price'] = price
    product_info['product_title'] = product_title
    return product_info 


def flipkart_find_price(url):
    driver = webdriver.Chrome()
    driver.get(url)
    markup = driver.page_source
    soup = bs(markup,"html.parser")
    price = soup.find('div', {'class': '_1vC4OE _37U4_g'}).text
    price = price[1:]
    price = price.replace(',','')
    product_title = soup.find('h1', {'class': '_3eAQiD'}).text
    product_info = {}
    product_info['price'] = price
    product_info['product_title'] = product_title
    driver.quit()
    return product_info


def myntra_find_price(url):
    driver = webdriver.Chrome()
    driver.get(url)
    markup = driver.page_source
    soup = bs(markup, "html.parser")
    product_title = soup.find('h1', {'class': 'pdp-title'}).text
    price = soup.find('strong', {'class': 'pdp-price'}).text
    price = price.strip('Rs.')
    price = price.strip()
    product_info = {}
    product_info['price'] = price
    product_info['product_title'] = product_title
    driver.quit()
    return product_info


def send_mail(email, content):
    yag.send(email, "subject", content)


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/result', methods=['GET', 'POST'])
def result():
    if request.method == 'POST':
        if 'jabong' in request.form['url']:
            dict_price = jabong_find_price(request.form['url'])
            price = dict_price['price']
            
        elif 'amazon' in request.form['url']:
            dict_price = amazon_find_price(request.form['url'])
            price = dict_price['price']
        elif 'flipkart' in request.form['url']:
            dict_price = flipkart_find_price(request.form['url'])
            price = dict_price['price']

        elif 'myntra' in request.form['url']:
            dict_price = myntra_find_price(request.form['url'])
            price = dict_price['price']
        else:
            return render_template('not_found.html')

        url = request.form['url']
        email = request.form['mail']
        user = Users(email=email, price=price, url=url)
        user.save()
        return render_template('message.html')


def check_price():
    user_infos = Users.select().where(Users.mail_send == False)
    for user in user_infos:
        # new_price = find_price(user.url)
        if 'amazon' in user.url:
            a = amazon_find_price(user.url)
        elif 'jabong' in user.url:
            a = jabong_find_price(user.url)
        elif 'myntra' in user.url:
            a = myntra_find_price(user.url)
        else:
            a = flipkart_find_price(user.url)
        new_price = a['price']
        if float(new_price) < float(user.price):
            print("price down")
            content = "<h3>Hey price of your item {} is change from {} to {} click on {} and go shopping</h3>".format(a['product_title'], user.price, new_price, user.url)
            send_mail(user.email, content)
            query = Users.update(mail_send=True).where(Users.id == user.id)
            query.execute()

if __name__ == '__main__':
    app.run(debug=True)
