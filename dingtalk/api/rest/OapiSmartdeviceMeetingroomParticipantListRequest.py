'''
Created by auto_sdk on 2021.04.07
'''
from dingtalk.api.base import RestApi
class OapiSmartdeviceMeetingroomParticipantListRequest(RestApi):
	def __init__(self,url=None):
		RestApi.__init__(self,url)
		self.bookid = None
		self.cursor = None
		self.size = None

	def getHttpMethod(self):
		return 'POST'

	def getapiname(self):
		return 'dingtalk.oapi.smartdevice.meetingroom.participant.list'
