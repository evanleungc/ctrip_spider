import requests
from lxml import etree
import PyV8
import re
from selenium import webdriver
import time
import os
import pandas as pd

JS_PATH = '/Users/apple/Documents/ctrip_spider/js/'
COOKIE_PATH = '/Users/apple/Documents/ctrip_spider/cookie/'

def usere(regex, getcontent): #regex
    pattern = re.compile(regex)
    content = re.findall(pattern, getcontent)
    return content

def modify(string):
	'''
	add escape to special signs
	'''
	string = string.replace('(', '\(')
	string = string.replace(')', '\)')
	return string

def get_city(hotel_url):
	'''
	Parameters
	----------
	hotel_url: string
		url of the hotel brand
	Return
	------
	city: list
		city id list of the hotel brand
	'''
	html = requests.get(hotel_url).content.decode('utf8')
	selector = etree.HTML(html)
	regex = '<div style="display:block;">([\s\S]*?)<div class="more_city">'
	city = usere(regex, html)[0]
	regex2 = 'hotel/(.+?)/'
	city = usere(regex2, city)
	return city

def get_max_page(city_hotel_url):
	'''
	Parameters
	----------
	city_hotel_url: string
		url of the hotel in the specific city
	Return
	------
	max_page: int
		the maximum page of the hotel in the specific city
	'''
	html = requests.get(city_hotel_url).content.decode('utf8')
	regex = 'layoutfix([\s\S]*)下一页'
	pages = usere(regex, html)[0]
	regex = 'data-value="(\d+?)"'
	pages = usere(regex, pages)
	if pages == []:
		max_page = 1
	else:
		max_page = int(pages[-1])
	return max_page

def get_hotel_info(page_url):
	'''
	Parameters
	----------
	page_url: string
		url of a single page

	Return
	------
	infodict: dict
		brief info of the hotels in that single page
	'''
	infodict = {}
	infodict.setdefault('title', [])
	infodict.setdefault('id', [])
	infodict.setdefault('score', [])
	#title: hotel name || id: hotel id(further used in detail info) || score: customers' score
	titlelist = []
	idlist = []
	scorelist = []
	html = requests.get(page_url).content.decode('utf8')
	regex = '<div class="hotel_new_list"([\s\S]*?)class="room_list2"'
	infolist = usere(regex, html)
	#regex
	titleregex = 'a title="(.*?)"'
	idregex = 'data-hotel="(.*?)"'
	scoreregex = '客户点评：(.*?)分'
	for info in infolist:
		titlelist.extend(usere(titleregex, info))
		idlist.extend(usere(idregex, info))
		scorelist.extend(usere(scoreregex, info))
	infodict.setdefault('title').extend(titlelist)
	infodict.setdefault('id').extend(idlist)
	infodict.setdefault('score').extend(scorelist)
	return infodict

def get_detail_info(hotel_id, city, start_date, dep_date):
	'''
	Get detail price / full-or-not / etc. info of the hotel
	Parameters
	----------
	hotel_id: string
		id of the hotel
	city: string
		id of the city
	start_date: string
		date of living
	dep_date: string
		date of departure

	Return
	------
	detail_info: dict
		detail info of each hotel
	'''
	detail_info = {}
	eleven = get_eleven()
	#use 'eleven' as key to get detail info of each hotel
	info_url = "http://hotels.ctrip.com/Domestic/tool/AjaxHote1RoomListForDetai1.aspx"
	querystring = {"psid":"","MasterHotelID":"%s"%hotel_id,"hotel":"%s"%hotel_id,"EDM":"F","roomId":"",
	"IncludeRoom":"","city":"%s"%city,"showspothotel":"T","supplier":"","IsDecoupleSpotHotelAndGroup":"F",
	"contrast":"0","brand":"0","startDate":"%s"%start_date,"depDate":"%s"%dep_date,"IsFlash":"F","RequestTravelMoney":"F",
	"hsids":"","IsJustConfirm":"","contyped":"0","priceInfo":"-1","equip":"","filter":"","productcode":"","couponList":"",
	"abForHuaZhu":"","defaultLoad":"T","TmFromList":"F","RoomGuestCount":"1,1,0",
	"eleven":"%s"%eleven}
	payload = '''psid=&MasterHotelID=%s&hotel=%s&EDM=F&roomId=&IncludeRoom=&city=%s
	&showspothotel=T&supplier=&IsDecoupleSpotHotelAndGroup=F&contrast=0&brand=110&startDate=%s
	&depDate=%s&IsFlash=F&RequestTravelMoney=F&hsids=&IsJustConfirm=&contyped=0&priceInfo=-1
	&equip=&filter=&productcode=&couponList=&abForHuaZhu=&defaultLoad=T&TmFromList=F
	&RoomGuestCount=1,1,0&eleven=%s'''%(hotel_id, hotel_id, city, start_date, dep_date, eleven)
	headers = {
	    'content-type': "multipart/form-data; boundary=----WebKitFormBoundary7MA4YWxkTrZu0gW",
	    'Accept': "*/*",
	    'Accept-Encoding': "gzip, deflate",
	    'Accept-Language': "zh-CN,zh;q=0.9,en;q=0.8",
	    'Cache-Control': "no-cache",
	    'Connection': "keep-alive",
	    'Content-Type': "application/x-www-form-urlencoded; charset=utf-8",
	    'Host': "hotels.ctrip.com",
	    'If-Modified-Since': "Thu, 01 Jan 1970 00:00:00 GMT",
	    'Referer': "http://hotels.ctrip.com/hotel/%s.html?isFull=F"%hotel_id,
	    'User-Agent': "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36",
	    'Postman-Token': "3aa8586c-caee-45a7-8cfd-5d2cbee1df43"
	    }
	html = requests.request("GET", info_url, data=payload, headers=headers, params=querystring).content.decode('utf8')
	roomregex = 'onNameNewClick\(this\)\\\\\">\\\\u000a([\s\S]*?)\\\\u000a'
	roomlist_raw = usere(roomregex, html)
	for i in roomlist_raw[0:2]:
		replaceregex = 'onNameNewClick\(this\)\\\\\">\\\\u000a%s'%modify(i)
		replacestr = usere(replaceregex, html)[0]
		html = html.replace(replacestr, '', 1)
	roomlist_raw = roomlist_raw[2:] #exclude recommendations
	roomlist = list(map(lambda x : x.strip(' '), roomlist_raw))
	roomlist_raw = list(map(lambda x : modify(x), roomlist_raw))
	splitlist = roomlist_raw[1:]
	splitlist.append('}')
	splitlist = [[i, j] for i, j in zip(roomlist_raw, splitlist)]
	for idx, split in enumerate(splitlist):
		sub_detail_info = {}
		splitregex = 'onNameNewClick\(this\)\\\\\">\\\\u000a%s([\s\S]*?)onNameNewClick\(this\)\\\\\">\\\\u000a%s'%(split[0], split[1])
		if idx == len(splitlist) - 1:
			splitregex = 'onNameNewClick\(this\)\\\\\">\\\\u000a%s([\s\S]*)%s'%(split[0], split[1])
		temp_html = usere(splitregex, html)[0]
		priceregex = 'base_price[\s\S]*?(\d+?)<'
		temp_price = usere(priceregex, temp_html)
		sub_detail_info.setdefault('price', []).extend(temp_price)
		detail_info.setdefault(roomlist[idx], []).extend(temp_price)
		satisfyregex = '预订满意度[\s\S]*?([\d+%].*?)<'
		temp_satisfy = usere(satisfyregex, temp_html)
		sub_detail_info.setdefault('satisfy', []).extend(temp_satisfy)
		roomidregex = '"roomid\\\\\":\\\\\"(\d+?)\\\\\"'
		temp_roomid = usere(roomidregex, temp_html)
		fullregex = 'data-isMember([\s\S]*?)预订'
		temp_fullhtml = usere(fullregex, temp_html)
		temp_full_left = []
		for full in temp_fullhtml:
			hrefregex = "InputNewOrder.aspx\?(.*?)\\\'  onclick"
			full_domain = 'http://hotels.ctrip.com/DomesticBook/InputNewOrder.aspx?'
			full_href = full_domain + usere(hrefregex, full)[0]
			left = get_room_left(full_href)
			temp_full_left.append(left)
		sub_detail_info.setdefault('room_left', []).extend(temp_full_left)
		detail_info[roomlist[idx]] = sub_detail_info
		replaceregex = 'onNameNewClick\(this\)\\\\\">\\\\u000a%s'%split[0]
		replacestr = usere(replaceregex, html)[0]
		html = html.replace(replacestr, '', 1)
	return detail_info

def get_room_left(url):
	'''
	How many rooms are available to be booked in the current situation
	Parameters
	----------
	url: string
		booking url of each room type

	Returns
	-------
	left: int
		number of rooms available to be booked in the current situation
		special case '-1': more than 5 rooms are available
					 '0': no rooms can be booked
	'''
	ticketdf = pd.read_csv(COOKIE_PATH + 'ticket.csv')
	ticket = ticketdf['ticket'].values[0]
	headers = {
	    'Cookie': 'ticket_ctrip=' + ticket}
	html = requests.get(url, headers=headers).content.decode('gbk', errors = 'ignore')
	if '预订信息' not in html:
		raise UserWarning('Invalid Ticket or All Rooms Full')
	if '不可预订' in html:
		left = 0
	else:
		leftregex = '仅剩(\d+?)间' 
		left = usere(leftregex, html)
		if left == []:
			left = -1
		else:
			left = int(left[0])
	return left

def gen_ctrip_ticket(update_freq):
	'''
	Use selenium to generate ticket cookie. The ticket will be saved in COOKIE_PATH
	Parameters
	---------- 
	update_freq: int
		frequency of updating ticket (in seconds)
	'''
	while 1:
		try:
			if not os.path.exists(COOKIE_PATH + 'ticket.csv'): #If not exist, make file
				ticketdf = pd.DataFrame({'ticket': ['Null']})
				ticketdf.to_csv(COOKIE_PATH + 'ticket.csv', index = False)
			driver = webdriver.Chrome()
			driver.set_page_load_timeout(10)
			button = '//*[@id="J_RoomListTbl"]/tbody/tr[3]/td[9]/div/a/div[1]'
			url1 = 'http://hotels.ctrip.com/Domestic/ShowHotelInformation.aspx?hotel=433176'
			driver.get(url1)
			driver.find_element_by_xpath(button).click()
			time.sleep(5)
			ticket = driver.get_cookie('ticket_ctrip')['value']
			if ticket != None:
				ticketdf = pd.DataFrame({'ticket': [ticket]})
				ticketdf.to_csv(COOKIE_PATH + 'ticket.csv', index = False)
				time.sleep(update_freq) #update cookie after update_freq time
			driver.close()
		except:
			driver.close()
			ticketdf = pd.DataFrame({'ticket': ['Null']})
			ticketdf.to_csv(COOKIE_PATH + 'ticket.csv', index = False)

def get_oceanball():
	'''
	Get random oceanball javascript
	Return
	------
	oceanball: random url of oceanball js
	cas: random function of generation of eleven
	'''
	oceanball = 'http://hotels.ctrip.com/domestic/cas/oceanball?callback=%s&_=%s'
	f = open(JS_PATH + 'get_callback.js')
	callback_js = f.read()
	with PyV8.JSContext() as ctxt:
		ctxt.eval('var callback = %s'%callback_js)
		ctxt.eval('cas = callback(15)')
		ctxt.eval('var current_time = (new Date).getTime()')
		vars = ctxt.locals
		cas = vars.cas
		current_time = vars.current_time
	oceanball = oceanball%(cas, int(current_time))
	return (oceanball, cas)

def get_eleven():
	'''
	Get "eleven" from oceanball
	Return
	------
	eleven: string
		parameter to get detail info
	'''
	oceanball, cas = get_oceanball()
	ocean = requests.get(oceanball).content.decode('utf8')
	ocean = ocean.replace('eval','JSON.stringify')  
	ctxt = PyV8.JSContext()           
	ctxt.__enter__()
	ocean = ctxt.eval(ocean)
	ocean = eval(ocean)
	ocean = ocean.replace(cas, 'eleven=' + cas)
	ctxt = PyV8.JSContext()           
	with PyV8.JSContext() as ctxt:
		ctxt.eval('var hotel_id = "433176"; var site = {}; site.getUserAgent = function(){}; var Image = function(){}; var window = {}; window.document = {body:{innerHTML:"1"}, documentElement:{attributes:{webdriver:"1"}}, createElement:function(x){return {innerHTML:"1"}}}; var document = window.document;window.navigator = {"appCodeName":"Mozilla", "appName":"Netscape", "language":"zh-CN", "platform":"Win"}; window.navigator.userAgent = site.getUserAgent(); var navigator = window.navigator; window.location = {}; window.location.href = "http://hotels.ctrip.com/hotel/"+hotel_id+".html"; var location = window.location;')
		# ctxt.eval('var div = {innerHTML:"1"};')
		ctxt.eval('var navigator = {userAgent:{indexOf: function(x){return "1"}}, geolocation:"1"}')
		ctxt.eval('var %s = function(x){return x()}'%cas)
		ctxt.eval(ocean)
		vars = ctxt.locals
		eleven = vars.eleven
	return eleven




