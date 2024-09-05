from telethon import TelegramClient
from telethon.errors import TakeoutInitDelayError
from telethon.tl.types import PeerUser, PeerChannel, PeerChat, InputMessagesFilterEmpty, InputPeerUser, InputPeerChat, InputPeerChannel
from telethon.utils import get_display_name
import ujson, os, asyncio, time
from backend.views import MessageView, ProfileView, UserView
from backend.db import get_session
from ui.signal.Signal import Signal
from util import get_input_entity_id, get_msg_count
import weakref

class DumpMsg():
    def __init__(self, client: TelegramClient, entity, signal, start_id = None, start_date=None, end_date=None, is_bak_self=False):
        print('start dump')
        # print('total', total)
        self.limit_interval = 5000
        self.count = 0
        print('enter dump loop')
        self.session = get_session()
        self.is_bak_self = is_bak_self
        self.msg_view = MessageView(self.session)
        self.usr_view = UserView(self.session)
        self.pro_view = ProfileView(self.session)
        self.is_continue = False
        self.last_id = None
        self.is_takeout = True
        self.signal = signal
        self.is_stop = False

        self.client = client
        self.entity = entity

        self.start_id = start_id
        self.start_date = start_date
        self.end_date = end_date

        self.error_msg = []
        self.errors = []

    def setupSignal(self):
        self.signal.stop_signal.connect(self.on_stop)

    def on_stop(self):
        self.is_stop = True

    async def setup_takeout(self):
        if self.client.session.takeout_id:
            print("Cancel takeout...")
            try:
                await self.client.end_takeout(success=False)
                if not client.session.takeout_id:
                    print("Takeout canceled!")
                else:
                    print("Fale to cancel takeout!")
                    print("Fallback to client mode!")
                    self.is_takeout = False
            except Exception as e:
                print("Fale to cancel takeout!")
                print("Fallback to client mode!")
                self.is_takeout = False

    async def get_channel_name(self, channel_id):
        peer_channel = PeerChannel(channel_id)
        channel = await self.client.get_entity(peer_channel)
        channel_name = channel.username
        return channel_name

    async def dump_msg_loop(self, takeout = None):

        async def save_msg(msg):
            print('')
            print('---------------------------------------------------------')
            print('')
            print('msg',msg.to_dict())
            print('')
            print('---------------------------------------------------------')
            print('')
            message = msg.message
            # date = msg.date
            # print('                ' + message)
            sender_id = None
            if isinstance(msg.from_id, PeerChannel):
                sender_id = msg.from_id.channel_id
            elif isinstance(msg.from_id, PeerUser):
                sender_id = msg.from_id.user_id
            elif isinstance(msg.from_id, PeerChat):
                sender_id = msg.from_id.chat_id
            elif not msg.from_id:
                msg.from_id = None
            else:
                print(msg)
                raise RuntimeError("Get sender_id error!")
            message_id = msg.id
            grouped_id = msg.grouped_id
            # print(message, date, sender_id, entity_id)
            if sender_id:
                if self.usr_view.get(user_id=sender_id):
                    print('start save msg')
                    self.msg_view.save(date, entity_id, message_id=message_id, message=message, sender_id=sender_id, grouped_id = grouped_id)
                    print('msg saved')
                    # raise ValueError('User not exist!')
                else:
                    print('start save user')
                    usr_entity = await self.client.get_entity(sender_id)
                    print('usr_entity', usr_entity)
                    name = get_display_name(usr_entity)
                    usr_name = usr_entity.username if hasattr(usr_entity, 'username') else None
                    print('usr_name', usr_name)
                    print('name', name)
                    print(sender_id, sender_id)
                    # usr_id = usr_entity.username if hasattr(usr_entity,'username') else None
                    self.usr_view.save(sender_id, name, usr_name)
                    self.msg_view.save(date, entity_id, message_id=message_id, message=message, sender_id=sender_id, grouped_id = grouped_id)
                    print('save user finished')
            else:
                self.msg_view.save(date, entity_id, message_id=message_id, message=message, grouped_id= grouped_id)

        async def bak_msg(msg):
            print('')
            print('---------------------------------------------------------')
            print('')
            print('msg',msg.to_dict())
            print('')
            print('---------------------------------------------------------')
            print('')
            try:
                kwargs = {}
                date = msg.date
                msg_id = msg.id
                grouped_id = msg.grouped_id
                kwargs['message_id'] = msg_id
                if grouped_id: kwargs['grouped_id'] = grouped_id

                fwd_info = msg.fwd_from

                saved_peer = msg.saved_peer_id
                if isinstance(saved_peer, PeerUser):
                    kwargs['is_user'] = True
                    fwd_entity_id = msg.peer_id.user_id
                    fwd_msg_id = msg.id
                elif isinstance(saved_peer, PeerChannel):
                    kwargs['is_user'] = False
                    fwd_entity_id = msg.saved_peer_id.channel_id
                    fwd_msg_id = fwd_info.saved_from_msg_id

                    try:
                        channel_name = await self.get_channel_name(fwd_entity_id)
                        if channel_name: kwargs['channel_name'] = channel_name
                    except Exception as e:
                        print('Get channel_name error!', e)
                elif not saved_peer:
                    await save_msg(msg)
                    print('forward msg')
                    return
                else:
                    raise TypeError('Msg type error!')
                print('fwd_entity_id', fwd_entity_id)
                    # channel_name = None
                    # exit()
                    # fwd_msg_date = None
                    # exit()
                kwargs['fwd_msg_id'] = fwd_msg_id

                try:
                    fwd_msg_date = fwd_info.date if fwd_info else None
                    if fwd_msg_date: kwargs['fwd_msg_date'] = fwd_msg_date
                except Exception as e:
                    print('Get fwd_msg_date error!', e)

                kwargs['fwd_entity_id'] = fwd_entity_id

                if message := msg.message: kwargs['message'] = message
                self.msg_view.save(date, entity_id, **kwargs )
            except Exception as e:
                # kwargs = {}
                # date = msg.date
                # if message := msg.message: kwargs['message'] = message
                # kwargs['message_id'] = msg_id
                # self.msg_view.save(date, entity_id, **kwargs)
                self.error_msg.append(msg)
                self.errors.append(e)
                return

        total = await get_msg_count(self.client, self.entity)
        print('total',total)
        if not self.is_bak_self:
            entity_id = get_input_entity_id(self.entity)
        else:
            entity_id = 100

        def init_kwargs():
            kwargs = {'limit': self.limit_interval, 'reverse': True}
            if not self.is_bak_self:
                kwargs['filter'] = InputMessagesFilterEmpty
            return kwargs

        while True:
            fmark = time.time()
            kwargs = init_kwargs()
            kwargs['offset_id'] = self.last_id
            if self.is_continue:
                if self.is_takeout:
                    msgs = await takeout.get_messages(self.entity, **kwargs)
                else:
                    msgs = await self.client.get_messages(self.entity, **kwargs)
                print('continue...')
            else:
                kwargs = init_kwargs()
                if self.start_id:
                    kwargs['offset_id'] = self.start_id
                if self.start_date:
                    kwargs['offset_date'] = self.start_date
                if self.is_takeout:
                    msgs = await takeout.get_messages(self.entity,**kwargs)
                else:
                    msgs = await self.client.get_messages(self.entity,**kwargs)

                self.is_continue = True
                print('start')
            print('Get data time',time.time() - fmark)
            # print(msgs)
            fmark = time.time()
            self.last_id = msgs[-1].id if msgs else None
            # if not self.start_id:
            # r_msgs = msgs
            # msgs.reverse()
            print(len(msgs))
            for msg in msgs:
                if self.is_stop:
                    break
                
                date = msg.date

                if self.end_date:
                    if date:
                        if date > self.end_date:
                            print('date',date)
                            print('self.end_date',self.end_date)
                            break
                    else:
                        continue
                    # exit()

                if not msg.fwd_from:
                    await save_msg(msg)
                else:
                    await bak_msg(msg)

            self.count += self.limit_interval
            if total < self.count or not msgs or self.is_stop:
                print('exit loop')
                if not self.is_stop:
                    print(' Start commit')
                    self.session.commit()
                    # self.msg_view.commit()
                    # self.usr_view.commit()
                    if not self.start_id:
                        full_entity = await self.client.get_entity(self.entity)
                        display_name = get_display_name(full_entity) if not self.is_bak_self else 'Saved Message'
                        self.pro_view.save(display_name, entity_id)

                if takeout:
                    await self.client.end_takeout(success=False)
                for i in range(len(self.error_msg)):
                    print('--------------------------------------------------------------------------------------')
                    print(self.error_msg[i].to_dict())
                    print('**************************************************************************************')
                    print('error', self.errors[i])
                    print('--------------------------------------------------------------------------------------')
                break
            print('Save data time', time.time() - fmark)
            print(self.count)
            await asyncio.sleep(0)

    async def dump_msg(self):
        print('start dump')
        await self.setup_takeout()

        while True:
            try:
                if self.is_takeout:
                    async with self.client.takeout(finalize=False, contacts=True, chats=True) as takeout:
                        await self.dump_msg_loop(takeout=takeout)
                    break
                else:
                    await self.dump_msg_loop()
                    break
            except TakeoutInitDelayError as e:
                print('Must wait', e.seconds, 'before takeout')
                print('Retry without take out.')
                if not self.is_takeout:
                    break
                self.is_takeout = False
