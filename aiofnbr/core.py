import aiohttp
import asyncio
from . import constants, utils


# requests
class APIRequest():
	"""Parent class of all API Requests"""
	def __init__(self,key,endpoint,arguments={}):
		self.key = key
		self.endpoint = endpoint
		self.arguments = arguments
	@asyncio.coroutine
	def url(self):
		args = yield from self.parseArguments()
		url = constants.BASEURL + self.endpoint + args
		return url
	@asyncio.coroutine
	def parseArguments(self):
		args = ""
		for a in self.arguments:
			args += uriencode(a) + "=" + uriencode(self.arguments[a]) + "&"
		if len(args) > 0:
			args = "?" + args
		return args
	@asyncio.coroutine
	def send(self):
		headers = {'x-api-key':self.key}
		session = aiohttp.ClientSession(headers=headers)
		url = yield from self.url()
		response = yield from session.get(url)
		json = yield from response.json()
		yield from session.close()
		self.response = APIResponse(response,json)
		return self.response



class Shop(APIRequest):
	""""Shop API Request"""
	def __init__(self,key):
		super().__init__(key,"/v2/shop/br/combined",{})


# responses
class APIResponse():
	"""API Response (formated requests.response)"""
	def __init__(self,response,json):
		self.headers = response.headers
		self.json = json
		try:
			self.status = self.json['status']
		except KeyError:
			self.status = response.status
		if self.status != 200:
			self.type = constants.ERROR_TYPE
			try:
				self.error = self.json['error']
			except KeyError:
				self.error = response.reason
		elif 'data' in self.json:
			if type(self.json['data']) is dict:
				self.type = constants.SHOP_TYPE
				self.data = ShopResponse(self.json)
			else:
				self.type = constants.NONE_TYPE
		else:
			self.type = constants.NONE_TYPE

class ShopResponse():
	def __init__(self,json={}):
		self.featured = []
		if json['data']['featured']:
			for i in range(0,len(json['data']['featured']['entries'])):
				self.featured.append(Item(json['data']['featured']['entries'][i]))
		self.daily = []
		if json['data']['daily']:
			for i in range(0,len(json['data']['daily']['entries'])):
				self.daily.append(Item(json['data']['daily']['entries'][i]))
		self.date = json.get('data',None).get('date',None)



class Item():
	"""A fortnite shop item"""
	def __init__(self,json={}):
		items = json.get('items', None)[0]
		if items != None:
			isBundle = json.get('bundle', None)
			self.id = items.get('id',None)
			if isBundle != None:
				self.name = isBundle.get('name',None)
			else:
				self.name = items.get('name',None)
			rarity_ = items.get('rarity',None)
			if rarity_!= None:
				self.rarity = rarity_.get('value',None)
			self.type = items.get('type',None)
			self.occurrences= items.get('shopHistory',None)
			images = items.get('images',None)

			if images != None:
				self.icon = images.get('icon',None)
				self.smallicon = images.get('smallIcon',None)
				if isBundle != None:
					self.featured = isBundle.get('image',None)
				else:
					self.featured = images.get('featured',None)
			self.price = json.get('finalPrice',None)
		
		

