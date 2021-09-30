# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup as bs

trans_table = str.maketrans({'₽': ' '})

HEADERS = {'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1 Safari/605.1.15'}
async def get_html(url):

    if 're-store' in url:
        req = requests.get(url, headers=HEADERS)
        print(req)
        return await re_store(req.text)
    if 'technopark' in url:
        req = requests.get(url, headers=HEADERS)
        print(req)
        return await techopark(req.text)

    else:
        return False


async def techopark(html):
    soup = bs(html, 'lxml')
    product_price = ' '.join(soup.find('span', class_='price product-page-card__price').text.translate(trans_table).split())
    product_name = ' '.join(soup.find('h1').text.split())
    print(product_name, product_price)
    info = {
        'product_name': product_name,
        'product_price': product_price
    }
    return info
#
#
# async def e_catalog(html):
#     soup = bs(html, 'lxml')
#     product_price = soup.find('div', class_='desc-big-price ib').find('span', {'itemprop':'lowPrice'}).text
#     product_name = soup.find('h1').text
#     print(product_price)
#     print(product_name)
#     info = {
#         'product_name':product_name,
#         'product_price':product_price
#     }
#     return info

async def re_store(html):
    soup = bs(html, 'lxml')
    product_name = ' '.join(soup.find('h1').text.split())
    try:
        product_price = ' '.join(soup.find('span', class_='product__price').text.translate(trans_table).split())
    except:
        product_price = ' '.join(soup.find('span', class_='product__info-price').text.translate(trans_table).split())

    finally:
        pass
    print(product_price)
    print(product_name)
    info = {
        'product_name': product_name,
        'product_price': product_price
    }
    return info


