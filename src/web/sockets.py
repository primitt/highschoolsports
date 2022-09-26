import websockets
import asyncio
import json
import pymongo
import hashlib
import dotenv
import os

dotenv.load_dotenv()
client = pymongo.MongoClient(os.getenv("PYMONGO"))

def hash_password(password):
    # Hash a password for storing.
    hashedpassword = hashlib.sha256(password.encode('utf-8')).hexdigest()
    return hashedpassword
def passwordValidate(password, hashedpassword):
    if hash_password(password) == hashedpassword:
        return True
    else:
        return False

# setup mongodb
db = client["LS"]
col = db["LS-SCORE"]
schools = db["LS-SCHOOLS"]
accounts = db["LS-ACCOUNTS"]
async def loop(websocket):
    # TODO: Add way way more commands and such
    cmd = await websocket.recv()
    command = cmd.split(":")
    #try:
    if command[0] == "GET":
        if command[1].split("/")[0] == "SCORE":
            try:
                data = list(col.find({"id":int(command[1].split("/")[1])}))
                print({"id":command[1].split("/")[1]})
            except Exception as e:
                print(e)
                data = []
            if data == []:
                await websocket.send(json.dumps({"status": "error", "message": "No data found"}))
            else:
                while True:
                    try:
                        await websocket.send(str(data))
                    except Exception as e:
                        print(e)
                        print("Connection Closed from a Client")
                        break
                    await asyncio.sleep(1)
                while True:
                    try:
                        await websocket.send("This is every 5 seconds")
                    except Exception as e:
                        print(e)
                        print("Connection Closed from a Client")
                        break
                    await asyncio.sleep(5)
    # except:
    #     websocket.send("MSG:INVALID_COMMAND")
async def main():
    async with websockets.serve(loop, "localhost", 2000):
        print("Started Websocket Server")
        await asyncio.Future()  # run forever
asyncio.run(main())

# 