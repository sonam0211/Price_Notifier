from flask import Flask,render_template,request 
import urllib.request
from bs4 import BeautifulSoup

url = "http://www.jabong.com/w-Off-White-Printed-Rayon-Kurta-300069811.html?pos=2&cid=XW574WA44AWIINDFAS"

response = urllib.request.urlopen(url)
html = response.read()
soup = BeautifulSoup(html,'html.parser')
price = soup.find('span',{'class':'actual-price'}).text

print(price)