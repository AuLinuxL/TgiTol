from sqlalchemy import Column, Integer, String, Boolean, ForeignKey, Date, DateTime

from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

class Config(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    api_id = Column(String,unique=True, default='')
    api_hash = Column(String,unique=True, default='')
    usr_name = Column(String, default='')
    usr_id = Column(String, default='')
    group_id = Column(String, default='')
    random = Column(Boolean, default=False)
    r_from = Column(String, default='')
    r_to = Column(String, default='')
    his_entity = Column(String, default='')
    his_search = Column(String, default='')
    dump_fdate = Column(Date)
    dump_tdate = Column(Date)
    dump_fid = Column(Integer)
    dump_tid = Column(Integer)
    dump_mode = Column(Integer)

class MsgConf(Base):
    __tablename__ = 'msg_conf'
    id = Column(Integer, primary_key=True)
    content = Column(String)
    delay = Column(String)

class Channel(Base):
    __tablename__ = 'channel'
    id = Column(Integer, primary_key=True)
    # channel_id = Column(Integer,unique=True)
    # channel_username = Column(String,unique=True, default='', nullable=True)
    channel_id = Column(Integer)
    channel_username = Column(String, default='', nullable=True)
    channel_name = Column(String,default='')

class Group(Base):
    __tablename__ = 'group'
    id = Column(Integer, primary_key=True)
    # group_id = Column(Integer,unique=True)
    # group_username = Column(String,unique=True, default='', nullable=True)
    group_id = Column(Integer)
    group_username = Column(String, default='', nullable=True)
    group_name = Column(String,default='')

class Message(Base):
    __tablename__ = 'message'
    id = Column(Integer, primary_key=True)
    message = Column(String, nullable=True)
    date = Column(String)
    message_id = Column(Integer, nullable=True)
    sender_id = Column(Integer, ForeignKey('user.id'), nullable=True)
    entity_id = Column(Integer)
    grouped_id = Column(Integer,nullable=True,default=None)
    forward_info = Column(Integer, ForeignKey('forward_info.id'), nullable=True)
    forward = relationship("ForwardInfo", back_populates="messages")
    # forward_info = Column(Integer, ForeignKey('forward_info.id', ondelete='CASCADE'), nullable=True)
    # forward = relationship("ForwardInfo", back_populates="messages", cascade="all, delete-orphan")
    user = relationship("User", back_populates="messages")

    def __repr__(self):
        return (f"<Message(id={self.id}, message_id={self.message_id}, sender_id={self.sender_id}, "
                f"entity_id={self.entity_id}, grouped_id={self.grouped_id}, forward_info={self.forward_info}),"
                f"message={self.message}>")

class ForwardInfo(Base):
    __tablename__ = 'forward_info'
    id = Column(Integer, primary_key=True)
    fwd_msg_id = Column(Integer)
    fwd_msg_date = Column(DateTime, nullable=True)
    fwd_entity_id = Column(Integer)
    channel_name = Column(String, nullable=True,default=None)
    is_user = Column(String, default=False)
    messages = relationship("Message", back_populates="forward")

class User(Base):
    __tablename__ = 'user'
    # id = Column(Integer, primary_key=True)
    name = Column(String)
    user_name = Column(String, nullable=True)
    id = Column(Integer, unique=True, primary_key=True)
    messages = relationship("Message", back_populates="user")

class Profile(Base):
    __tablename__ = 'profile'
    id = Column(Integer, primary_key=True)
    name = Column(String)
    entity_id = Column(Integer, unique=True)






