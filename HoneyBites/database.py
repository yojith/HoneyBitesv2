import pymongo
import open_ai_categorize as categorize
from bson import json_util
import json

def parse_json(data):
    return json.loads(json_util.dumps(data))


client = categorize.initialize()

class HoneyBitesDB:
    _myclient = pymongo.MongoClient("mongodb://localhost:27017/")

    _honeybitesdb = _myclient["Honey_Bites"]

    _userdb = _honeybitesdb["User_Data"]
    _foodcategorydb = _honeybitesdb["Food_Category_Data"]

    def __init__(self):
        pass

    @classmethod
    def create_new_user(cls, data: dict):
        '''
        Add a new user to the user database.
        Data should be a dictionary with the fields.
        If the username is already present, do not add a new user
        '''
        
        query = {"username": data["username"]}
        if cls._userdb.find_one(query):
            return "User already exists!"
        else:
            doc = cls._userdb.insert_one(data)
            return doc.inserted_id

    @classmethod
    def get_user_data(cls, username: str, password: str):
        '''
        Gets the data of the user based on the username and password.
        Won't return anything if user doesn't exist or password is wrong.
        '''
        query = {"username": username}
        doc = cls._userdb.find_one(query)
        if doc:
            if doc["password"] == password:
                return doc
            else:
                return f"Password for {username} is incorrect!"
        else:
            return "No user found!"
    
    @classmethod
    def get_user_data_unprotected(cls, username: str):
        username = username.strip()
        query = {"username": username}
        doc = cls._userdb.find_one(query)
        doc = parse_json(doc)
        print(doc)
        if doc:
            print("returning")
            return doc
        else:
            return "No user found!"

        
    @classmethod
    def get_food_category(cls, food: str):
        '''
        Returns the category of a particular food.
        If category not present, a new category is created.
        '''
        query = {"foods": food}
        doc = cls._foodcategorydb.find_one(query)
        if doc:
            return doc["_id"]
        else:
            # ChatGPT API gives the category from the food name
            category = categorize.sort_cuisine(client, food)
            
            query = {"_id": category}
            category_doc = cls._foodcategorydb.find_one(query)
            if category_doc:
                update = {"$push": {"foods": food}} # Appending food to category
                cls._foodcategorydb.update_one({"_id": category}, update)
            else:
                category_doc = {"_id": category, "foods": [food]}
                cls._foodcategorydb.insert_one(category_doc)
            
            return category
    
    @classmethod
    def get_users_by_preference(cls, cuisine: str):
        '''
        Gets the data of users who have a particular cuisine preference.
        '''
        query = {"cuisine_preference": cuisine}
        docs = cls._userdb.find(query).limit(3)
        results = list(docs)
        return results

    @classmethod
    def add_user_preference(cls, username: str, food: str):
        '''
        Adds user's cuisine preference to database.
        '''
        cuisine = cls.get_food_category(food)
        query = {"username": username}
        doc = cls._userdb.find_one(query)
        if cuisine not in doc["cuisine_preference"]:
            update = {"$push": {"cuisine_preference": cuisine}}
            cls._userdb.update_one({"_id": doc["_id"]}, update)
        else:
            print("Cuisine already present")

if __name__ == "__main__":
    client = categorize.initialize()
    myusers = [
        {"name": "Yojith", "username": "YoBird123", "password": "abc123", "cuisine_preference": ["Italian", "Chinese"]},
        {"name": "Mihir", "username": "Mirp123", "password": "abc123", "cuisine_preference": ["Italian", "Japanese"]},
        {"name": "Adam", "username": "MrGray123", "password": "abc123", "cuisine_preference": ["Italian", "Indian"]},
        {"name": "Dmitri", "username": "Crimzn123", "password": "abc123", "cuisine_preference": ["Chinese", "Japanese"]}
    ]
    for user in myusers:
        id = HoneyBitesDB.create_new_user(user)
        print(id)
    data = HoneyBitesDB.get_user_data("YoBird123", "abc123")

    y = HoneyBitesDB.get_food_category("Spaghetti")
    print(y)

    x = HoneyBitesDB.get_users_by_preference("Italian")
    print(x)
