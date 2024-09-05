from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel, PeerUser
from telethon.utils import get_display_name
import os, asyncio, random, time

async def _send_by_id(target_id,group_id,client=None):
    async for message in client.iter_messages(group_id):
        sender = await message.get_sender()
        if  sender and sender.id == target_id:
            print('find')
            return sender.id
        else:
            continue
        print('not find')

async def send_msg_by_name(client, msgs, target_name = None):
        entity = None

        try:
            print('get_entity')
            print('target_name',target_name)
            entity = await client.get_entity(target_name)
        except Exception as e:
            print('ERROR' + str(e))

        count = 0

        for msg in msgs:
            # try:
            count += 1
            msg_content = msg['msg']
            delay = int(msg['delay'])
            await client.send_message(entity,msg_content )
            await asyncio.sleep(delay)
            print(str(time.time()) + "    " + "msg " + str(count) + " send")
            # except Exception as e:
            #     print('ERROR:  ' + str(e))

async def send_msg_by_id(client, msgs, target_id=0, group_id=0):
    n = 0

    sender_id = await _send_by_id(target_id, group_id, client=client)

    for msg in msgs:
        # try:
        n += 1
        msg_content = msg['msg']
        delay = int(msg['delay'])
        print(msg)
        await client.send_message(sender_id, msg_content)
        rand_int = random.uniform(35.0, 120.0)
        await asyncio.sleep(delay)
        print(str(time.time()) + "    " + "msg " + str(n) + "send")
        # except Exception as e:
        #     print('ERROR:  ' + str(e))
