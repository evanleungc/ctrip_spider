import os
os.chdir('/Users/apple/Documents/ctrip_spider')
import ctrip_funcs as cf

BRAND_ID = 'h110' #如家id--'h110'

#1. get citylist
hotel_url = 'http://hotels.ctrip.com/brand/%s'%BRAND_ID
citylist = cf.get_city(hotel_url)

#2. get hotel_page_url
page_urllist = []
city = citylist[0] #Test on one city only
city_hotel_url = 'http://hotels.ctrip.com/hotel/%s/%s'%(city, BRAND_ID)
max_page = cf.get_max_page(city_hotel_url) #get total pages in a specific city
for page in range(1, max_page + 1):
	temp_url = city_hotel_url + 'p' + str(page)
	page_urllist.append(temp_url)

#3. get hotel info
hotel_info = {}
for page_url in page_urllist[0:2]:
	page_info = cf.get_hotel_info(page_url)
	hotel_info.setdefault('title', []).extend(page_info['title'])
	hotel_info.setdefault('id', []).extend(page_info['id'])
	hotel_info.setdefault('score', []).extend(page_info['score'])

#4. get detail info
hotel_id = hotel_info['id'][0] #Test on one hotel
city = citylist[0]
start_date = '2018-05-23'
dep_date = '2018-05-24'
detailinfo = cf.get_detail_info(hotel_id, city, start_date, dep_date)
