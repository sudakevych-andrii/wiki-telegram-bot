import mongoengine as me

me.connect('wiki_bot_bd')


class Query(me.Document):
    query = me.StringField(min_length=1, max_length=128)


class User(me.Document):
    chat_id = me.IntField(required=True, unique=True)
    queries = me.ListField(me.ReferenceField(Query))



