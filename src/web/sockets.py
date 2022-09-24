import websockets
import asyncio
import json
import pymongo

# setup mongodb
client = pymongo.MongoClient("mongodb+srv://primitt:1016@primittdb.mvkeq.mongodb.net/")
db = client["LS"]
col = db["LS-SCORE"]
async def loop(websocket):
    cmd = await websocket.recv()
    command = cmd.split(":")
    #try:
    if command[0] == "GET":
        if command[1].split("/")[0] == "SCORE":
            try:
                data = list(col.find({"id":command[1].split("/")[1]}))
                print({"id":command[1].split("/")[1]})
                print(data)
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
    # except:
    #     websocket.send("MSG:INVALID_COMMAND")
async def main():
    async with websockets.serve(loop, "localhost", 8765):
        print("Started Websocket Server")
        await asyncio.Future()  # run forever
asyncio.run(main())