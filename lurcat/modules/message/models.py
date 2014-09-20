# -*- coding: utf-8 -*-

from sqlalchemy import Column, ForeignKey, not_
from sqlalchemy.orm import relationship

from lurcat.addons.extensions import db
from lurcat.addons.utils import get_current_time, diff


class Message(db.Model):

    __tablename__ = 'message'

    message_id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer,ForeignKey('users.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    text = Column(db.Text, nullable=False)
    pub_date = Column(db.DateTime, default=get_current_time)
    publish_user = relationship('User', backref = 'message', primaryjoin = "Message.user_id == User.id")
    parent_id = Column(db.Integer,ForeignKey('message.message_id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=True)
    root_id = Column(db.Integer,ForeignKey('message.message_id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=True)
    response = Column(db.Boolean, nullable=True)
    last_activity = Column(db.DateTime, default=get_current_time)

    def save(self):
        db.session.add(self)
        db.session.commit()


    def get_responses(cls,id):
        query = cls.query.filter(Message.parent_id == id)
        return query.all()


    def get_all_messages(cls,limit=None,offset=0):
    	query = cls.query.filter(cls.parent_id == None)
    	if limit:
    		query = query.limit(limit)
    	if offset:
    		query = query.offset(offset)
    	return query.all()

    def get_message_from_user(cls,user,limit=None,offset=0):
        query = cls.query.filter(Message.user_id == user.id).filter(Message.parent_id == None)
        if limit:
            query = query.limit(limit)
        if offset:
            query = query.offset(offset)
        return query.all()

    def get_messages_feed(cls,user):
        star_messages = StaredMessages()

        ##Get the messages which user hasn't reponded to
        new_messages = cls.get_response_message(user,0)

        ##Get the messages that are stared by the user
        stared_messages = TimeLine()
        stared_messages = stared_messages.get_user_starred_messages(user.id)
        stared_messages = cls.get_all_ordered_by_activity(stared_messages)
        # stared_messages = star_messages.get_user_starred_messages(user.id)
        # stared_messages = [cls.get_by_id(x) for x in stared_messages]
        new_messages = diff(new_messages,stared_messages)
        # new_messages = list(set(new_messages) - set(stared_messages))
        ##Get the messages that the user has replied to
        replied_messages = TimeLine()
        replied_messages = replied_messages.get_user_agreed_messages(user.id)
        replied_messages = cls.get_all_ordered_by_activity(replied_messages)    
        stared_messages = diff(stared_messages,replied_messages)
        # stared_messages = list(set(stared_messages)-set(replied_messages))
        print "new_messages:%s"%new_messages
        print "stared_messages:%s"%stared_messages
        print "replied_messages:%s"%replied_messages
        return {'replied_messages':replied_messages,'stared_messages':stared_messages,'new_messages':new_messages}
  


    def get_response_message(cls,user,offset):
        #Get All messages which the user has replied to
        query = cls.query.with_entities(Message.parent_id).filter_by(user_id = user.id)

        ids = query.all()
        ids = [x.parent_id for x in ids]
        ids = filter(lambda x: x is not None ,ids)
        # Gell all messages whose parent Ids are none i.e they are root messages and specifically the ones which the user hasn't replied too
        return cls.query.filter(Message.parent_id == None).filter(not_(Message.message_id.in_(ids))).order_by(Message.last_activity.desc()).offset(offset).limit(5).all()
    @classmethod
    def get_all_ordered_by_activity(cls,message_ids):
        return cls.query.filter(Message.message_id.in_(message_ids)).order_by(Message.last_activity.desc()).limit(5).all() 

    def get_user_replied_messages(cls,user):
        parent_ids = cls.query.with_entities(Message.parent_id).filter_by(user_id = user.id).filter(not_(Message.parent_id == None)).all()
        lis =  [cls.get_by_id(x) for x in parent_ids]
        print lis
        return lis


    @classmethod
    def get_by_id(cls, message_id):
        return cls.query.filter_by(message_id=message_id).first_or_404()



class StaredMessages(db.Model):
    __tablename__ = 'stared_messages'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer,ForeignKey('users.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    message_id = Column(db.Integer,ForeignKey('message.message_id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    publish_user = relationship('User', backref = 'star_message', primaryjoin = "StaredMessages.user_id == User.id")
    message = relationship('Message', backref = 'star_id', primaryjoin = "StaredMessages.message_id == Message.message_id")

    def add(self,user_id,message_id):
        self.user_id = user_id
        self.message_id = message_id
        db.session.add(self)
        db.session.commit()

    def get_user_starred_messages(cls,user_id):
        return cls.query.with_entities(StaredMessages.message_id).filter(StaredMessages.user_id == user_id).all()

    def get_by_id(cls, star_id):
        return cls.query.filter_by(id=star_id).first_or_404()

    def delete_by_id(cls, message_id):
        print message_id
        cls.query.filter_by(message_id=message_id).delete(synchronize_session='fetch')
        db.session.commit()

#Tells which messages are most active for a user
#This is very naive and will be replaced in future
class TimeLine(db.Model):
    __tablename__ = 'timeline'

    id = Column(db.Integer, primary_key=True)
    user_id = Column(db.Integer,ForeignKey('users.id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    message_id = Column(db.Integer,ForeignKey('message.message_id', onupdate="CASCADE", ondelete="RESTRICT"), nullable=False)
    score = Column(db.Integer, default=0)
    starred = Column(db.Boolean, default=False)
    agreed =  Column(db.Boolean, default=False)


    publish_user = relationship('User', backref = 'timeline', primaryjoin = "TimeLine.user_id == User.id")
    message = relationship('Message', backref = 'timeline', primaryjoin = "TimeLine.message_id == Message.message_id")

    def add(self,user_id,message_id,starred = False,agreed = False):            
        if self.exists(user_id,message_id):
            self = self.get_by_id(user_id,message_id)
            if starred:
                self.starred = True
            if agreed:
                self.agreed = True
        else:
            self.user_id = user_id
            self.message_id = message_id
            self.starred = starred
            self.agreed = agreed
        db.session.add(self)
        db.session.commit()


    @classmethod
    def get_user_agreed_messages(cls,user_id):
        return cls.query.with_entities(TimeLine.message_id).filter(TimeLine.user_id == user_id).filter(TimeLine.agreed == True).all()

    @classmethod
    def get_user_starred_messages(cls,user_id):
         return cls.query.with_entities(TimeLine.message_id).filter(TimeLine.user_id == user_id).filter(TimeLine.starred == True).all()
       

    @classmethod
    def exists(cls,user_id, message_id):
        return cls.query.filter(TimeLine.user_id == user_id).filter(TimeLine.message_id == message_id).count()

    def get_by_id(cls,user_id,message_id):
        return cls.query.filter(TimeLine.user_id == user_id).filter(TimeLine.message_id == message_id).first_or_404()


