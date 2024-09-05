from telethon import TelegramClient
from telethon.tl.types import InputPeerChannel
from telethon.utils import get_display_name
from backend.views import ChannelView, GroupView
import asyncio
from tel.Client import Client

async def SyncEntity(session):
    channel_view = ChannelView(session)
    channel_view.clear()
    group_view = GroupView(session)
    group_view.clear()
    client = await Client().get()
    print('start')
    async for dialog in client.iter_dialogs():
        print('get entity')
        entity = dialog.entity
        if dialog.is_channel:
            channel_name = get_display_name(entity)
            channel_id = entity.id
            try:
                channel_username = entity.username if entity.username else "Private Channel"
            except Exception as e:
                channel_username = None
                print(e)
            channel_view.save(channel_id,channel_username,channel_name)
            print(f"Channel Name: {channel_name}")
            print(f"Channel ID: {channel_id}")
            print(f"Channel Username: {channel_username}")
            # print(f"Channel URL: {channel_url}")
            print('-----------------------')
        elif dialog.is_group:
            group_name = get_display_name(entity)
            group_id = entity.id
            try:
                group_username = entity.username if entity.username else "Private Channel"
            except Exception as e:
                group_username = None
                print(e)
            group_view.save(group_id, group_username, group_name)
            print(f"Group Name: {group_name}")
            print(f"Group ID: {group_id}")
            # print(f"Group Username: {group_username}")
            # print(f"Group URL: {group_url}")
            print('-----------------------')

async def get_entity_list(session, is_update = False):
    g_view = GroupView(session)
    c_view = ChannelView(session)
    if is_update or (not g_view.get() and not c_view.get()):
        await SyncEntity(session)
        print('Sync finished!')
    channel_list = c_view.get()
    group_list = g_view.get()
    return channel_list,group_list
