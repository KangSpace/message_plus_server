'''
Created by auto_sdk on 2020.09.18
'''
from dingtalk.api.base import RestApi
class OapiProcessinstanceExecuteV2Request(RestApi):
	def __init__(self,url=None):
		RestApi.__init__(self,url)
		self.request = None

	def getHttpMethod(self):
		return 'POST'

	def getapiname(self):
		return 'dingtalk.oapi.process.instance.execute'
