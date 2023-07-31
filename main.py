import fade, random, requests, uuid, json, threading, time
from datetime import datetime
from flask import Flask, render_template, jsonify, request
from bs4 import BeautifulSoup as htmlparser
from typing import Literal, Optional
import discord
from discord.ext import commands
from discord.utils import MISSING
import requests

print(fade.water(f"""
    __                                
   / /_  __  ___  ______  ____ ___  __
  / __ \/ / / / |/_/ __ \/ __ `/ / / /
 / /_/ / /_/ />  </ /_/ / /_/ / /_/ /  ~ a hevnd project ~
/_.___/\__,_/_/|_/ .___/\__,_/\__, /  
                /_/          /____/   
"""))

app = Flask(__name__, template_folder='./templates/', static_folder='./static/')
PROXY = "put your proxy here"

def create_gamepass(price):
    cook = json.load(open("./buxpay/main.json","r"))["cookies"]
    r = random.choice(cook)
    cookie = r["cookie"]
    universe = r["universe"]
    cookies = f"GuestData=guestdatacookie;.ROBLOSECURITY={cookie};OtherCookies=othercookievalues"
    user_agent = "Google Chrome"

    cookie_dict = {}
    cookie_list = cookies.split(";")

    for cookie in cookie_list:

        cookie = cookie.strip()
        cookie_name, cookie_value = cookie.split("=", 1)
        cookie_dict[cookie_name] = cookie_value

    http = requests.get("https://www.roblox.com/home", cookies=cookie_dict)
    html = htmlparser(http.text, "html.parser")
    csrf_tag = html.find("meta", {"name": "csrf-token"})
    csrf_token = csrf_tag["data-token"]
    print(csrf_token)
    r=requests.post("https://apis.roblox.com/game-passes/v1/game-passes",headers={"x-csrf-token":csrf_token},data={"Name":uuid.uuid4(),"Description":None,"UniverseId":universe,"File":None},cookies=cookie_dict)
    print(r.text)
    gamepass = r.json()["gamePassId"]
    rs=requests.post(f"https://apis.roblox.com/game-passes/v1/game-passes/{gamepass}/details",headers={"x-csrf-token":csrf_token},data={"IsForSale":True,"Price":int(price)},cookies=cookie_dict)
    return gamepass

def txs():
    try:
        while True:
            for cookie in json.load(open("./buxpay/main.json","r"))["cookies"]:
                with requests.session() as session:
                    session.cookies['.ROBLOSECURITY'] = cookie["cookie"]
                    # proxy = PROXY.split(':')
    
                    # proxy = proxy[2] + ':' + proxy[3] + '@' + proxy[0] + ':' + proxy[1]
    
                    # session.proxies = {
                    #     'http':'http://'+proxy,
                    #     'https':'http://'+proxy
                    # }
                    userid = cookie["userid"]
                    transactions = session.get(
                        f'https://economy.roblox.com/v2/users/{userid}/transactions?transactionType=Sale&limit=100'
                    ).json()
                    mainjson = json.load(open("./buxpay/main.json", "r"))
                    allt = transactions["data"]
                    for transaction in allt:
                        if transaction["details"]["type"] != "GamePass":
                            pass
                        else:
                            for client in mainjson["clients"]:
                                for invoice in client["invoices"]:
                                    if invoice["status"] == "unpaid" and invoice["gamepass"] == transaction["details"]["id"]:
                                        invoice["status"] = "paid"
                                        invoice["payer_id"] = transaction["agent"]["id"]
                                        invoice["paid"] = transaction["created"]
                                        client["robux_earned"] += invoice["price"]
                                        json.dump(obj=mainjson, fp=open("./buxpay/main.json","w"),indent=4)
            time.sleep(60)
    except:
        print("update the bot cookies!")

def get_product_id(gid):
    html = str(requests.get(f"https://www.roblox.com/game-pass/{gid}/").content)
    dataProductID_unindex = int(html.find('data-product-id="')) + 17
    dataProductID_index = dataProductID_unindex
    while 1 == 1:
        dataProductID_index += 1
        if html[dataProductID_index] == "\"":
            break
    dataProductID = str(html[dataProductID_unindex:dataProductID_index])
    return int(dataProductID)

def get_gamepass_price(gid):
    url = f"https://www.roblox.com/game-pass/{gid}/"
    response = requests.get(url)
    soup = htmlparser(response.text, "html.parser")
    element = soup.find("span", class_="text-robux-lg wait-for-i18n-format-render")
    information = element.text.strip()
    return int(information)

def get_creator_id(gid):
    url = f"https://www.roblox.com/game-pass/{gid}/"
    response = requests.get(url)
    soup = htmlparser(response.text, "html.parser")
    element = soup.find("a", class_="text-name")
    href = element["href"]
    href = str(href).split("/")[4]
    return int(href)

def buy_gamepass(gid, price):
    if get_gamepass_price(gid) == int(price):
        cookie = random.choice(json.load(open("./buxpay/main.json","r"))["cashout_cookies"])["cookie"]
        cookies = f"GuestData=guestdatacookie;.ROBLOSECURITY={cookie};OtherCookies=othercookievalues"
        user_agent = "Google Chrome"
    
        cookie_dict = {}
        cookie_list = cookies.split(";")
    
        for cookie in cookie_list:
    
            cookie = cookie.strip()
            cookie_name, cookie_value = cookie.split("=", 1)
            cookie_dict[cookie_name] = cookie_value
    
        http = requests.get("https://www.roblox.com/home", cookies=cookie_dict)
        html = htmlparser(http.text, "html.parser")
        csrf_tag = html.find("meta", {"name": "csrf-token"})
        csrf_token = csrf_tag["data-token"]
        productid = get_product_id(gid)
        response = requests.post(f'https://economy.roblox.com/v1/purchases/products/{productid}', json={'expectedCurrency': 1, 'expectedPrice': price, 'expectedSellerId': get_creator_id(gid)}, headers={'x-csrf-token': csrf_token, 'cookie': cookie},cookies=cookie_dict)
        print(response.text)
        return response.json()

    else:
        return False

threading.Thread(target=txs).start()


@app.route('/payments/create', methods=['POST'])
def payments():
    rd = "create"
    if rd == "create":
        uid = str(uuid.uuid4()).split("-")[0]
        try:
            users = json.load(open("./buxpay/main.json","r"))
            for user in users["clients"]:
                if user["api_key"] == request.json.get("api_key"):
                    if user["expires"] <= int(time.time()):
                        return jsonify({"ok": False, "data": {"error": "Your plan has expired."}}), 400
                    gamepassid = create_gamepass(request.json.get("price"))
                    now = datetime.now()
                    timestring = now.strftime("%m/%d/%Y, %I:%M:%S %p")
                    user["invoices"].append({"uid":uid, "price":request.json.get("price"), "status":"unpaid", "gamepass":gamepassid, "created":timestring})
                    json.dump(obj=users, fp=open("./buxpay/main.json","w"), indent=4)
                    return jsonify({"ok": True, "data": {"uid":uid, "price":request.json.get("price"), "status":"unpaid", "gamepass":gamepassid, "created":timestring}}), 200
            return jsonify({"ok": False, "data": {"error": "Invalid API key."}}), 400
        except Exception as e:
            return jsonify({"ok": False, "data": {"error": str(e)}}), 400

@app.route('/')
def index():
    return render_template('notfound.html')

@app.route('/invoices/<invoiceid>')
def invoices(invoiceid):
    try:
        r=requests.get("https://buxpay.xyz/payments/info",json={"api_key":"inf","uid":invoiceid}).json()
        print(r)
        if r["data"]["status"] == "paid":
            rbx = r["data"]["price"]
            rbx = format(rbx, ",")
            gamepass = r["data"]["gamepass"]
            return render_template('paid.html',TIMESTRING=r["data"]["created"],ROBUXSTRING=f"{rbx} Robux")
        else:
            gamepassid = r["data"]["gamepass"]
            payload = {
              "data": f"https://roblox.com/game-pass/{gamepassid}",
              "config": {
                "body": "circle-zebra-vertical",
                "eye": "frame13",
                "eyeBall": "ball15",
                "erf1": [],
                "erf2": [],
                "erf3": [],
                "brf1": [],
                "brf2": [],
                "brf3": [],
                "bodyColor": "#FFFFFF",
                "bgColor": "#1D1E28",
                "eye1Color": "#FFFFFF",
                "eye2Color": "#FFFFFF",
                "eye3Color": "#FFFFFF",
                "eyeBall1Color": "#FFFFFF",
                "eyeBall2Color": "#FFFFFF",
                "eyeBall3Color": "#FFFFFF",
                "gradientColor1": "#FFFFFF",
                "gradientColor2": "#FFFFFF",
                "gradientType": "linear",
                "gradientOnEyes": "true",
                "logo": "",
                "logoMode": "default"
              },
              "size": 1000,
              "download": "imageUrl",
              "file": "png"
            }
            rss=requests.post("https://api.qrcode-monkey.com/qr/custom",json=payload).json()
            rl = rss["imageUrl"]
            print(rl)
            rbx = r["data"]["price"]
            rbx = format(rbx, ",")
            return render_template('example.html',GAMEPASSLINK=f"https://roblox.com/game-pass/{gamepassid}",USERCREATED=r["data"]["username"],TIMESTRING=r["data"]["created"],ROBUXSTRING=f"{rbx} Robux",QRCODELINK=f"https://{rl}")
    except Exception as e:
         print(e)
         return render_template('notfound.html')
    
@app.route('/payments/info',methods=['GET'])
def paymentsinfo():
    try:
        i = request.json["uid"]
        l = request.json["api_key"]
        r=json.load(open(f"./buxpay/main.json","r"))
        for user in r["clients"]:
            for invoice in user["invoices"]:
                if invoice["uid"] == i:
                    invoice["username"] = user["username"]
                    return jsonify({"ok": True, "data": invoice}), 200
        return jsonify({"ok": False, "data": {"message": "Failed to find invoice."}}), 200    
        return jsonify({"ok": False, "data": {"message": "Invalid API key."}}), 200
    except Exception as e:
        return jsonify({"ok": False, "data": {"error": str(e)}}), 400

@app.route('/clients/<rd>', methods=['GET'])
def clients(rd):
    if rd == "info":
        try:
            i = request.json.get("api_key")
            r=json.load(open(f"./buxpay/main.json","r"))
            for user in r["clients"]:
                if user["api_key"] == i:
                    return jsonify({"ok": True, "data": user}), 200
            return jsonify({"ok": False, "data": {"message": "Invalid API key."}}), 200
        except Exception as e:
            return jsonify({"ok": False, "data": {"error": str(e)}}), 400

@app.route('/admins/database/keys', methods=['POST', 'GET', 'DELETE'])
def admin_db_keys():
    print(request.json, request.method)
    if request.json.get("fsdfd") == True:
        if request.method.lower() == "delete":
            try:
                j = json.load(open("./buxpay/main.json","r"))
                clients = j["clients"]
                filtered_clients = [client for client in clients if client.get("api_key") != request.json.get("api_key")]
                j["clients"] = filtered_clients
                json.dump(obj=j, fp=open("./buxpay/main.json","w"), indent=4)
                return jsonify({"ok":True})
            except:
                return jsonify({"ok":False,"data":{"error":"Invalid API key."}})
            
        if request.method.lower() == "info":
            #try:
                i = request.json["api_key"]
                r=json.load(open(f"./buxpay/main.json","r"))
                print(r)
                for user in r["clients"]:
                    print(user)
                    if user["api_key"] == i:
                        print("FOUNDDD")
                        return jsonify({"ok": True, "data": user}), 200
                return jsonify({"ok": False, "data": {"message": "Invalid API key."}}), 200
            # except Exception as e:
            #     return jsonify({"ok": False, "data": {"error": str(e)}}), 400
            
        if request.method.lower() == "post":
            try:
                j = json.load(open("./buxpay/main.json","r"))
                api_key = uuid.uuid4()
                username = request.json.get("username")
                new_client = {
                    "username": username,
                    "api_key": str(api_key),
                    "robux_earned": 0,
                    "robux_balance": 0,
                    "expires": (int(time.time()) + int(request.json.get("expires"))),
                    "invoices": [

                    ]
                }
                j["clients"].append(new_client)
                json.dump(obj=j,fp=open("./buxpay/main.json","w"),indent=4)
                return jsonify({"ok":True, "data": new_client})
            except Exception as e:
                return jsonify({"ok":False, "data": {"error":str(e)}})

@app.route("/clients/cashout",methods=["POST"])
def clicashout():
    apikey = request.json.get("api_key")
    gamepass = request.json.get("gamepass")
    r=requests.get("https://buxpay.xyz/clients/info",json={"api_key":apikey})
    if r.json()["data"]["robux_balance"] >= get_gamepass_price(gamepass):
        r = buy_gamepass(gamepass, get_gamepass_price(gamepass))
        return jsonify({"ok":True, "data": r})
    else:
        return jsonify({"ok":False, "data": {"error":"Make sure you have enough robux to complete this transaction."}})
        
app.run(host="0.0.0.0",port=80)
