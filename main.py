from app import check_price
import time

def check_for_price_change():
    check_price()
    time.sleep(20)
    

while True:
    check_for_price_change()    

