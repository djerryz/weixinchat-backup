import os, json
from datetime import timedelta
from flask import Flask, session, Response, jsonify, request, redirect, render_template, send_from_directory

def read_data(datafile):
	with open(datafile,"rb") as f:
		_ = f.read()
	return json.loads(_)


app = Flask(__name__, static_url_path='', static_folder="./wechat-backup/static/")


@app.after_request
def handle_after_request(response):
    """
    设置CORS源
    :param response: 
    :return: 
    """
    if "Origin" in request.headers:
        response.headers["Access-Control-Allow-Origin"] = request.headers["Origin"]
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,PUT,HEAD,OPTIONS,DELETE,PATCH"
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type,x-requested-with"
    return response


# Serve React App - UI
@app.route("/")
def statics():
    return send_from_directory(app.static_folder, "index.html")

# Server Media
@app.route("/media/<path:filename>")
def medias(filename):
    print(filename)
    return send_from_directory("./tmp/", filename)
@app.route("/wx/media/<path:filename>")
def medias2(filename):
    print(filename)
    return send_from_directory("./tmp/", filename)

# 获取聊天列表
@app.route('/api/chat/list', methods=['GET'])
def chatlist():
    pageIndex = request.args.get('pageIndex')
    pageSize = request.args.get('pageSize')
    name = request.args.get('name')

    total = 0
    rows = []

    this_chat = medb["chatdb"]
    for onechat in this_chat:
        total += 1
        onerow = {
            "talker": onechat,
            "alias": "",
            "msgCount": this_chat[onechat]["allchatnum"],
            "createTime": "",
            "chatType": "",
            "userType": ""
        }
        _ = getuserinfo(onechat, "")
        onerow = {**onerow , **_}
        # 由于wechat UI取值是小写的"nickname"，这儿我们需要转换一下，否则前端不正确
        onerow["nickname"] = onerow["nickName"]
        rows.append(onerow)
    response = app.response_class(
        response=json.dumps({"total": total, "rows": rows}),
        mimetype='application/json'
    )
    return response


def getuserinfo(wxid, chatroomid): # 第二个参数仅当查询一个用户在群聊里面的备注昵称才需要传参
    base = {
        "userName": "",
        "alias":"",
        "conRemark": "",
        "nickName": "",
        "reserved1": "",
        "reserved2": "",
        "localAvatar": ""
    }
    if wxid == "unknow":
        return base
    if wxid[-9:] == "@chatroom":
        # 聊天室
        this_u = medb["chatdb"][wxid]
        nick = this_u["name"]
        con = this_u["conRemark"]
        base["userName"] = wxid
        base["conRemark"] = this_u["conRemark"]
        base["nickName"] = this_u["name"]
        base["reserved1"] = this_u["reserved1"]
        base["reserved2"] = this_u["reserved2"]
        base["localAvatar"] = "media/" + this_u["avatar"]
    else:
        this_u = medb["talkerdb"][wxid]
        con = this_u["conname"]
        if chatroomid == "":
            nick = this_u["realname"]
        else:
            try:
                nick = this_u["nicknameinroom"][chatroomid]
            except:
                nick = "" # 不一定由昵称
    
    base["userName"] = wxid
    base["conRemark"] = con
    base["nickName"] = nick
    base["reserved1"] = this_u["reserved1"]
    base["reserved2"] = this_u["reserved2"]
    base["localAvatar"] = "media/" + this_u["avatar"]
    return base

def getcontentbytype(content,type_):
    # ["image", "voice", "video", "file", "emoji", "special", "text"]
    # type_需要修正和wechat对齐，否则前端不显示
    base = {
        "imgPath": "",
        "mediaPath": "",
        "mediaBCKPath":"",
        "mediaSourcePath":"",
        "fileInfo":{
            "fileName":"",
            "fileSize":"",
            "filePath":"",
            "fileExt":""
        },
        "emojiInfo":{
            "md5":"",
            "cdnUrl":"",
            "w":0,
            "h":0
        }
    }
    raw_type = 0
    raw_content = ""
    if type_ == "image" or type_ == "voice" or type_ == "video":
        for onepath in content:
            if content[onepath] == "":
                continue
            content[onepath] = "media/" +  content[onepath]
        base = {**base, **content}
        if type_ == "image":
            raw_type = 3
        if type_ == "voice":
            raw_type = 34
        if type_ == "video":
            raw_type = 43
    elif type_ == "file":
        content["filePath"] = "media/" +  content["filePath"]
        base["fileInfo"] = content
        raw_type = 1090519089
    elif type_ == "emoji":
        base["emojiInfo"] = content
        raw_type = 47
    elif type_ == "special":
        raw_content = content
        raw_type = 268445456
    elif type_ == "text":
        raw_content = content.split(":\n",1)[-1]
        raw_type = 1
    return base,raw_content,raw_type

# 获取聊天详情
@app.route('/api/chat/detail', methods=['GET'])
def chatdetail():
    pageIndex = request.args.get('pageIndex')
    pageSize = request.args.get('pageSize')
    talker = request.args.get('talker')
    
    total = 0
    rows = []

    this_chatdetail = medb["chatdb"][talker]["chatdetail"]
    for index_ in this_chatdetail:
        total += 1
        this_content = this_chatdetail[index_]

        this_who = this_content["who"]
        if this_who == "":
            print(this_content)
        u_info = getuserinfo(this_who, talker)
        f_info,rawcontent,raw_type = getcontentbytype(this_content["say"]["detail"] , this_content["say"]["type"])
        issend = 0
        if this_who == mywxid:
            issend = 1
        onerow = {
            "msgId": index_,
            "msgSvrId": "",
            "type": raw_type, #this_content["say"]["type"],
            "isSend": issend,
            "createTime": this_content["time"],
            "talker": this_content["who"],
            "content": rawcontent,
            "isChatRoom":"",
            "userInfo": u_info,

        }
        onerow = {**onerow,**f_info}
        rows.append(onerow)

    response = app.response_class(
        response=json.dumps({"total": total, "rows": rows}),
        mimetype='application/json'
    )
    return response

# 查询用户信息
@app.route('/api/user/info', methods=['GET'])
def userinfo():
    username = request.args.get('username')
    u_info = getuserinfo(username, "")
    response = app.response_class(
        response=json.dumps(u_info),
        mimetype='application/json'
    )
    return response

medb = ""
mywxid = ""
def main():
    global medb,mywxid
    weixindb = read_data("weixin_decrypt.db")
    _ = list(weixindb.keys())
    for index,oneid in enumerate(_):
        print(index,oneid)
    me_ = int(input("which is you (number):\n"))
    mywxid = _[me_]
    medb = weixindb[mywxid]
    
    app.config['JSON_AS_ASCII'] = False
    app.run(host="0.0.0.0", port=8888)
 