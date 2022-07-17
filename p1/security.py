import pymongo
client = pymongo.MongoClient()
db = client.ecommerce
user_coll = db.users



def authenticate(username, password):
    user = client.ecommerce.users.find_by_username(username)
    if user and user.__getattribute__('password') == password:
        return user
    
def identity(payload):
    user_id = payload['identity']
    return client.ecommerce.users.find_by_id(user_id)