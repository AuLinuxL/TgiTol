from sqlalchemy import Column, Integer, String, create_engine
from sqlalchemy.orm import declarative_base, Session
from sqlalchemy import func, select
from sqlalchemy.exc import MultipleResultsFound
from backend.models import MsgConf, Config, Channel, Group, Message, Profile, User, ForwardInfo
from util import get_refered_id

class MsgConfView():
    def __init__(self, session: Session):
        self.session = session

    def save(self, obj = None, content = None, delay = None):
        if not obj and content and delay:
            obj = MsgConf()
            obj.content = content
            obj.delay = delay
        if obj and content: obj.content = content
        if obj and delay: obj.delay = delay
        self.session.add(obj)
        self.session.commit()

    def update(self, obj, content = None, delay = None):
        obj.content = content
        obj.delay = delay
        self.session.commit()

    def delete(self, obj):
        self.session.delete(obj)
        self.session.commit()

    def query(self,id: int):
        return self.session.query(MsgConf).filter(MsgConf.id == id).first()

    def load(self):
        return self.session.query(MsgConf).all()

class ConfigView():
    def __init__(self, session: Session):
        self.session = session

    def get(self):
        conf = self.session.query(Config).first()
        if not conf:
            conf = Config()
            self.session.add(conf)
            self.session.commit()
        return conf

    def save(self,**kwargs):
        conf = self.get()
        for key,value in kwargs.items():
            if hasattr(conf,key):
                setattr(conf,key,value)
            else:
                print('No attribute',key)
        self.session.commit()

class ChannelView():
    def __init__(self, session: Session):
        self.session = session

    def save(self, channel_id, channel_username, channel_name):
        channel = Channel()
        channel.channel_id = channel_id
        channel.channel_username = channel_username
        channel.channel_name = channel_name

        self.session.add(channel)
        self.session.commit()

    def get(self):
        return self.session.query(Channel).all()

    def get(self):
        channels = self.session.query(Channel).all()
        return channels

    def clear(self):
        self.session.query(Channel).delete()
        self.session.commit()

class GroupView():
    def __init__(self, session: Session):
        self.session = session

    def save(self, group_id, group_username, group_name):
        group = Group()
        group.group_id = group_id
        group.group_username = group_username
        group.group_name = group_name

        self.session.add(group)
        self.session.commit()

    def get(self):
        groups = self.session.query(Group).all()
        return groups

    def clear(self):
        self.session.query(Group).delete()
        self.session.commit()

class UserView():
    def __init__(self, session: Session):
        self.session = session

    def save(self,user_id, name,user_name):
        usr = User()
        usr.id = user_id
        usr.name = name
        usr.user_name = user_name
        self.session.add(usr)

    def get(self, name=None,user_name=None,user_id=None):
        query = self.session.query(User)
        if name:
            query = query.filter(User.name == name)
        elif user_name:
            query = query.filter(User.user_name == user_name)
        elif user_id:
            query = query.filter(User.id == user_id)

        return query.first()

class FwdInfoView():
    def __init__(self, session: Session):
        self.session = session

    def save(self, fwd_msg_id, fwd_entity_id, is_user = False, channel_name=None, fwd_msg_date=None):
        info = ForwardInfo()
        info.fwd_msg_id = fwd_msg_id
        info.fwd_entity_id = fwd_entity_id
        info.is_user = is_user
        info.fwd_msg_date = fwd_msg_date
        info.channel_name = channel_name
        self.session.add(info)
        self.session.flush()
        return info.id

class MessageView():
    def __init__(self, session: Session):
        self.session = session
        # self.userView = userView(self.session)

    def save(self, date, entity_id, sender_id = None, message=None, message_id=None, grouped_id = None, fwd_msg_id = None, is_user = False, fwd_entity_id = None, channel_name = None, fwd_msg_date = None):
        # if sender_id and self.userView.get(user_id=sender_id):
        #     raise ValueError('User not exist!')
        msg = Message()
        msg.message = message
        msg.date = date
        msg.message_id = message_id
        msg.sender_id = sender_id
        msg.entity_id = entity_id
        msg.grouped_id = grouped_id
        if fwd_msg_id or fwd_entity_id:
            fwd_info = FwdInfoView(self.session)
            id = fwd_info.save(fwd_msg_id, fwd_entity_id, is_user = is_user, channel_name = channel_name, fwd_msg_date = fwd_msg_date)
            print('forward_info',id)
            msg.forward_info = id
        self.session.add(msg)

    def commit(self):
        self.session.commit()

    def get_all(self, entity_id):
        query = self.session.query(Message).filter(Message.entity_id == entity_id)
        total = query.count()
        return total, query.all()

    def get(self, entity_id, keyword = None, split_count=0, split_interval=5000):
        query = self.session.query(Message).filter(Message.entity_id == entity_id)

        if keyword:
            query = query.filter(Message.message.contains(keyword))

        total = query.count()
        query = split_query(query, split_count, split_interval)

        return total, query.all()

    def get_by_id(self, entity_id, keyword, split_count=0, split_interval=5000):
        id_list = get_refered_id(keyword)
        if not id_list:
            return None
        id_list = [int(id) for id in id_list]
        for id in id_list:
            id = int(id)
            query = self.session.query(Message).filter(Message.entity_id == entity_id, Message.sender_id == id)
            total = query.count()
            query = split_query(query, split_count, split_interval)
            return total, query.all()
        return total, None

    def get_by_name(self, entity_id, keyword, split_count=0, split_interval=5000, is_usr_name = False):
        if not is_usr_name:
            query = (self.session.query(Message)
                    .filter(Message.entity_id == entity_id)
                    .join(User,Message.sender_id == User.id)
                    .filter(User.name.contains(keyword))
                     )
            total = query.count()
            query = split_query(query, split_count, split_interval)
            return total, query.all()
        else:
            if keyword.startswith('@'):
                keyword = keyword[1:]
            query = (self.session.query(Message)
                    .filter(Message.entity_id == entity_id)
                    .join(User,Message.sender_id == User.id)
                    .filter(User.user_name.contains(keyword))
                    )
            total = query.count()
            print('get_by_name','total',total)
            query = split_query(query, split_count, split_interval)
            return total, query.all()

    def get_usr_name(self,sender_id):
        query = select(User.name).where(User.id == sender_id)
        result = self.session.execute(query).scalar_one_or_none()
        # query = select(User.name).join(Message,Message.sender_id == User.id).where(Message.sender_id == sender_id)
        # try:
            # result = self.session.execute(query).scalar_one_or_none()
        #     result = self.session.execute(query).first()
        # except MultipleResultsFound as e:
        #     print(e)
        #     result = self.session.execute(query).first()
        #     print(result)
        #     exit()
        return result

    def get_fwd_info(self, forward_id):
        self.session.flush()
        # fwd_info = self.session.query(ForwardInfo).all()
        fwd_info = self.session.query(ForwardInfo).filter(ForwardInfo.id==forward_id).first()
        # query = select(ForwardInfo).where(ForwardInfo.id == forward_id)
        # fwd_info = self.session.execute(query).scalar_one_or_none()
        return fwd_info

    def get_max_entity_id(self, entity_id):
        max_entity_id = (
            self.session.query(func.max(Message.message_id))
            .filter(Message.entity_id == entity_id)
            .scalar()
        )
        return max_entity_id

    def exist(self, entity_id):
        id_list = get_refered_id(entity_id)
        for id in id_list:
            if self.session.query(Message).filter((Message.entity_id == id)).first():
                return id, True
        return None, False
            #     return False
            # else:
            #     return True

    def delete(self, entity_id):
        self.session.query(Message).filter((Message.entity_id == entity_id)).delete()
        self.session.commit()

class ProfileView():
    def __init__(self, session: Session):
        self.session = session

    def save(self, name, entity_id):
        if self.session.query(Profile).filter(Profile.entity_id==entity_id).first():
            return
        profile = Profile()
        profile.name = name
        profile.entity_id = entity_id
        self.session.add(profile)
        self.session.commit()

    def get(self):
        return self.session.query(Profile).all()

    def delete(self, entity_id):
        instance = self.session.query(Profile).filter(Profile.entity_id == entity_id).first()
        self.session.delete(instance)
        self.session.commit()

def get_username(session,entity_id):
    id_list = get_refered_id(entity_id)
    for id in id_list:
        group = session.query(Group).filter(Group.group_id == id).first()
        channel = session.query(Channel).filter(Channel.channel_id == id).first()
        if group:
            username = group.group_username
            if username:
                return True if username == 'Private Group' else False,group.group_username
        elif channel:
            username = channel.channel_username
            if username:
                return True if username == 'Private Channel' else False,channel.channel_username
        else:
            if id == id_list[-1]:
                return False, None

# def split_query(query, split_count, split_interval):
#     offset = split_count * split_interval
#     query = query.offset(offset).limit(split_interval)
#     return query

def split_query(query, split_count, split_interval):
    total_count = query.count()
    total_pages = ((total_count - 1) // split_interval) + 1
    reverse_split_count = total_pages - split_count - 1
    if reverse_split_count < 0:
        return query.limit(0)

    offset = reverse_split_count * split_interval

    print('offset',offset,'split_interval',split_interval)

    # query = query.order_by(Message.id.desc()).offset(offset).limit(split_interval)
    query = query.offset(offset).limit(split_interval)

    return query





