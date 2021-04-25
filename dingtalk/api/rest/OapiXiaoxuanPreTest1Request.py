'''
Created by auto_sdk on 2021.04.14
'''
from dingtalk.api.base import RestApi
class OapiXiaoxuanPreTest1Request(RestApi):
	def __init__(self,url=None):
		RestApi.__init__(self,url)
		self.name = None
		self.systemData = None

	def getHttpMethod(self):
		return 'POST'

	def getapiname(self):
		return 'dingtalk.oapi.xiaoxuan.pre.test1'
