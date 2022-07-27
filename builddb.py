import sqlite3
import os
import hashlib
import json


def md5_(content):
	m = hashlib.md5()
	if type(content) == str:
		content = content.encode()
	m.update(content)
	return m.hexdigest()

''' DATA MODEL
{
	"self_wxid_inreal":{
		"name":"",
		"talkerdb":{
			"wxid_inrel": { # wxid
				"conname": "XXX", # 备注名
				"realname": "XXX", # 微信原始名
				"avatar": "xxxx", # 头像地址
				"reserved1":"", # 头像的网络地址
            	"reserved2":"",
				"nicknameinroom": { # 在聊天室显示的名称
					"chatroom_inreal": "" 
				}
			}
		},
		"chatdb": {
			"chatroom_inreal":{ # chootroomid / wxid
				"name": "", # 群名 / 用户名
				"conRemark": "", # 备注名
				"owner": "", #群主 / 无
				"notice": "", # 群通知 / 无
				"allchatnum": 1, # 聊天个数
				"avatar": "", # 群聊头像
				"reserved1":"", # 头像的网络地址
            	"reserved2":"",
				"chatdetail": {
					"1":{
						"who": "wxid_inrel", 
						"say": {
							"type":"", # image, file, voice, video, emoji, special, text
							"detail": "" # 聊天内容
						},
						"time": "" # 创建时间
					}
				}
			}
		}
	}
}
'''

dbcursor = ""

def main():
	global dbcursor
	dbname = "./tmp/EnMicroMsg_plain.db"
	dbhandler = sqlite3.connect(dbname)
	dbhandler.row_factory = sqlite3.Row
	dbcursor = dbhandler.cursor()
	datafile = "weixin_decrypt.db"

	# 0. 加载历史数据
	weixindb  = {}
	try:
		weixindb = read_data(datafile)
	except:
		pass

	_ = builddb(weixindb)
	# 1. 构建号主信息
	_.getmyselfinfo()

    # 2. 构建chatroom信息
	_.getchatroominfo()

	# 3. 构建聊天数据
	_.getmessage()

	# 4. 保存数据到json
	write_data(_.getdata(), datafile)

def write_data(jsondata, datafile):
	with open(datafile,"w") as f:
		f.write(json.dumps(jsondata, indent=4, ensure_ascii=False)) # , sort_keys=True ,避免报错TypeError: '<' not supported between instances of 'int' and 'str'，取消排序
    

def read_data(datafile):
	with open(datafile,"rb") as f:
		_ = f.read()
	return json.loads(_)

def getnamebyid(id): # 投入
	query_ = "select conRemark, nickname from rcontact where username='{}'".format(id)
	dbcursor.execute(query_)
	rows2 = dbcursor.fetchall()
	return [rows2[0]['conRemark'], rows2[0]['nickname']]

def getavatar(id):
	md5id = md5_(id)
	return "avatar/{}/{}/user_{}.png".format(md5id[0:2], md5id[2:4], md5id)

def getavatar_net(id):
	query_ = "select reserved1, reserved2 from img_flag where username='{}'".format(id)
	dbcursor.execute(query_)
	rows2 = dbcursor.fetchall()
	if len(rows2) == 0:
		return ["",""]
	return [rows2[0]['reserved1'], rows2[0]['reserved2']]

def getemoinfo(path):
	query_ = "select cdnUrl from EmojiInfo where md5='{}'".format(path)
	dbcursor.execute(query_)
	rows2 = dbcursor.fetchall()
	_ = {
		"md5":"",
		"cdnUrl":rows2[0]['cdnUrl'],
		"w":0,
		"h":0
    }
	return _

def getfilepath(content):
	try:
		filename = content.split("<title>")[1].split("</title>")[0]
		filelen = content.split("<totallen>")[1].split("</totallen>")[0]
		_ = {
			"fileName":filename,
			"fileSize":filelen,
			"filePath":"Download/{}".format(filename),
			"fileExt":""
		}
	except:
		print(content)
		exit()
	return _

def getvoiceinfo(path):
	md5path = md5_(path)
	_ = {
		"mediaPath": "voice2/{}/{}/msg_{}.mp3".format(md5path[0:2], md5path[2:4], path)
	}
	return _

def getimageinfo(imgPath, issend, mywxid, talker, msgsrvid):
	src_path = ""
	th_path = imgPath.split("://")[1]
	th_path = "image2/{}/{}/{}".format(th_path[3:5],th_path[5:7],th_path)

	if issend == 0:
		# 接受
		a = talker
		b = mywxid
	else:
		a = mywxid
		b = talker

	bck_path = "{}_{}_{}_backup".format(a,b,msgsrvid)

	_ = {
		"mediaPath": th_path,
        "mediaBCKPath":bck_path,
        "mediaSourcePath":src_path,
	}
	return _

class builddb:
	def __init__(self, weixindb):
		self.already_checktalker = []
		self.weixindb = weixindb

	def getdata(self):
		return self.weixindb

	def getmyselfinfo(self):
		query_ = "select value from userinfo WHERE id = 2"
		dbcursor.execute(query_)
		rows = dbcursor.fetchall()
		mywxid = rows[0]["value"]
		myname = getnamebyid(mywxid)[1]
		if mywxid not in self.weixindb:
			self.weixindb[mywxid] = {}
			self.weixindb[mywxid]["talkerdb"] = {}
			self.weixindb[mywxid]["chatdb"] = {}
		self.weixindb[mywxid]["name"] = myname
		self.mywxid = mywxid
		self.chatdb = self.weixindb[mywxid]["chatdb"]
		self.talkerdb = self.weixindb[mywxid]["talkerdb"]


	def getchatroominfo(self):
		query_ = "select chatroomname,memberlist,displayname,chatroomnotice,roomowner from chatroom"
		dbcursor.execute(query_)
		rows = dbcursor.fetchall()
		for onerow in rows:
			chatroomname = onerow['chatroomname']
			memberlist = onerow['memberlist']
			displayname = onerow['displayname']
			memberlist = memberlist.split(";")
			displayname = displayname.split("、")
			print(len(displayname))
			print(len(memberlist))
			for index,newxid in enumerate(memberlist):
				if newxid not in self.already_checktalker:
					if newxid not in self.talkerdb :
						self.talkerdb[newxid] = {}
						self.talkerdb[newxid]["nicknameinroom"] = {}
					_ = getnamebyid(newxid)
					self.talkerdb[newxid]["realname"]  = _[1]
					self.talkerdb[newxid]["avatar"] = getavatar(newxid)
					_a_n = getavatar_net(newxid)
					self.talkerdb[newxid]["reserved1"] = _a_n[0]
					self.talkerdb[newxid]["reserved2"] = _a_n[1]

					self.talkerdb[newxid]["conname"]  = _[0]
					self.already_checktalker.append(newxid)
				self.talkerdb[newxid]["nicknameinroom"][chatroomname] = displayname[index]
				
			if chatroomname not in self.chatdb:
				self.chatdb[chatroomname] = {}
				self.chatdb[chatroomname]["chatdetail"] = {}
				self.chatdb[chatroomname]["allchatnum"] = 0
			_roomname = getnamebyid(chatroomname)
			self.chatdb[chatroomname]["conRemark"] = _roomname[0]
			self.chatdb[chatroomname]["name"] = _roomname[1]
			self.chatdb[chatroomname]["owner"] = onerow['roomowner']
			self.chatdb[chatroomname]["notice"] = onerow['chatroomnotice']
			self.chatdb[chatroomname]["avatar"] = getavatar(chatroomname)
			_a_n = getavatar_net(newxid)
			self.chatdb[chatroomname]["reserved1"] = _a_n[0]
			self.chatdb[chatroomname]["reserved2"] = _a_n[1]
				

	def getmessage(self):
		query_ = "select msgSvrId,issend,type,createTime,talker,content,imgPath,isSend from message order by createTIme desc"
		dbcursor.execute(query_)
		rows = dbcursor.fetchall()

		
		for onemessage in rows:
			talker = onemessage['talker']
			content = onemessage['content']
			imgPath = onemessage['imgPath']
			issend = onemessage['isSend']
			msgsrvid = onemessage['msgSvrId']
			isSend = onemessage['isSend']
			type_ = str(onemessage['type'])
			current_allow_types = ["image", "voice", "video", "file", "emoji", "special", "text"]
			special_feature = ["<title><![CDATA[安全登录提醒]]></title>","<title>当前版本不支持展示该内容，请升级至最新版本。</title>",'<msg><appmsg appid=\"\" sdkver=\"0\"><title>']
			this_type_ = ""
			this_detail_ = ""
			this_who_ = ""
			is_specail = 0

			if talker not in self.chatdb:
				self.chatdb[talker] = {}
				self.chatdb[talker]["chatdetail"] = {}
				self.chatdb[talker]["allchatnum"] = 0

			this_chatdb = self.chatdb[talker]
			
			if talker[-9:] != "@chatroom":
				# 若非聊天室
				if talker not in self.already_checktalker:
					# 补充talker相关数据
					if talker not in self.talkerdb :
						self.talkerdb[talker] = {}
						self.talkerdb[talker]["nicknameinroom"] = {}
					_ = getnamebyid(talker)
					self.talkerdb[talker]["realname"]  = _[1]
					self.talkerdb[talker]["avatar"] = getavatar(talker)
					_a_n = getavatar_net(talker)
					self.talkerdb[talker]["reserved1"] = _a_n[0]
					self.talkerdb[talker]["reserved2"] = _a_n[1]
					
					self.talkerdb[talker]["conname"]  = _[0]
					self.already_checktalker.append(talker)
				else:
					pass

				# 处理发送者
				if isSend == 1: # 本人发送
					this_who_ = self.mywxid
				else:
					this_who_ = talker

				
			else:
				# 若是聊天室
				if isSend == 1:
					this_who_ = self.mywxid
				else:
					try:
						if ":" not in content: # 拍一拍，撤回的特殊形态
							is_specail = 2
						else:
							this_who_ = content.split(":",1)[0]
							if this_who_ == "":
								this_who_ = "unknow"
					except:
						this_who_ = "unknow"
				# pass 已处理

			# 处理聊天内容
			_roomname = getnamebyid(talker)
			this_chatdb["conRemark"] = _roomname[0]
			this_chatdb["name"] = _roomname[1]
			this_chatdb["owner"] = ""
			this_chatdb["notice"] = ""
			this_chatdb["avatar"] = getavatar(talker)
			_a_n = getavatar_net(talker)
			this_chatdb["reserved1"] = _a_n[0]
			this_chatdb["reserved2"] = _a_n[1]
			
			# 开始处理具体聊天内容 -- 由于时间排序不用担心乱序的问题
			if type_ == "3":
				# 1. 图片
				this_type_ = current_allow_types[0]
				this_detail_ = getimageinfo(imgPath, issend, self.mywxid, talker, msgsrvid)
			elif type_ == "34":
				# 2. 语音
				this_type_ = current_allow_types[1]
				this_detail_ = getvoiceinfo(imgPath)
			elif type_ == "43":
				# 3. 视频
				this_type_ = current_allow_types[2]
				this_detail_ = {
					"mediaPath": "video/{}.mp4".format(imgPath)
				}
			elif type_ == "1090519089":
				# 4. 文件
				this_type_ = current_allow_types[3]
				this_detail_ = getfilepath(content)
			elif type_ == "47":
				# 5. 表情
				this_type_ = current_allow_types[4]
				this_detail_ = getemoinfo(imgPath)
			else:
				if content == None:
					# 非正常数据，直接pass
					continue
				
				for onefeature in special_feature:
					if onefeature in content:
						is_specail = 1
						break

				if is_specail == 2:
					this_who_ = "unknow" # 强制设置为unknow
					this_type_ = current_allow_types[5]
					this_detail_ = content
				elif is_specail == 1:
					# 特殊内容 -- 拍一拍，撤回，通知等
					this_who_ = "unknow" # 强制设置为unknow
					text = ""
					this_type_ = current_allow_types[5]
					if "<name><![CDATA[" in content:
						try:
							text += content.split("<name><![CDATA[")[-1].split("]]></name>")[0]
						except:
							pass
					if "<digest><![CDATA[" in content:
						try:
							text += content.split("<digest><![CDATA[")[-1].split("]]></digest>")[0]
						except:
							pass
					if "<template><![CDATA[" in content:
						try:
							text += content.split("<template><![CDATA[")[-1].split("]]></template>")[0] # 多个取最后
						except:
							pass
					this_detail_ = text
				else:
					# 普通聊天内容
					if "\n<msg><emoji fromusername" in content:
						# 处理表情
						this_type_ = current_allow_types[4]
						this_detail_ = content.replace(" ","").split('cdnurl="')[1].split('"',1)[0] # "cdnurl = "
					else:
						this_type_ = current_allow_types[6]
						this_detail_ = content
				
				
			this_chatdb["chatdetail"][this_chatdb["allchatnum"]] = {
				"who": this_who_, 
				"say": {
					"type": this_type_,
					"detail": this_detail_
				},
				"time": onemessage['createTime']
			}
			
			this_chatdb["allchatnum"] += 1