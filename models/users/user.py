from common.database import Database as database
from recommender.core import r
from models.products.product import get_product_by_id
import common.utils as utils

class User:
    def __init__(self, email, password, name=None, id=None, type="normal"):
        self.email = email
        self.password = password
        if name is None:
            self.name = email
        else:
            self.name = name
        self.id = id
        self.type = type

    def exists(self):
        """Whether this user's email exists in the database"""
        return database.get_user_by_email(self.email)

    def exists_id(self):
        return database.get_user_by_id(self.id)

    def valid(self):
        """This method verifies whether that email:pw is valid in db
            Returns:
                user data (dict): if combo is valid
                False (bool): otherwise"""
        user_data = self.exists()
        if not user_data:
            # if user doesn't even exist, its not valid
            return False
        else:
            # if utils.is_pw_correct(self.password, user_data['password']):
            if user_data['type'] == "admin":
                if utils.is_pw_correct(self.password, user_data['password']):
                    return user_data
                else:
                    return False
            else:
                if self.password == user_data['password']:
                    return user_data
                else:
                    return False

    def is_admin(self):
        """This methods verifies whether this user is an admin."""
        user_data = self.exists()
        if user_data:
            return user_data['type'] == "admin"
        else:
            return False

    def load(self):
        """Loads the user data if its valid"""
        valid = self.valid()
        if valid:
            self.id = valid['id']
            self.email = valid['email']
            self.password = valid['password']
            self.name = valid['password']
            self.type = valid['type']
            self.new = False
        else:
            # if user does not exist, generate unique id
            self.id = utils.get_unique_id()

            self.new = True

    def save(self):
        """Saves the user data if email doesn't exist and returns True.
            otherwise does nothing and return False"""
        if not self.exists():
            if not self.id:
                self.id = utils.get_unique_id()
            database.save_user(**self.json())
            self.new = True
            return True
        else:
            return False
            
    def json(self):
        return {
            "id": self.id,
            "email": self.email,
            # "password": utils.hash_pw(self.password),
            "password": self.password,
            "name": self.name,
            "type": self.type
        }

    def get_recommended_products(self):
        """Returns a list of products that are recommended for this user -- `self` --"""
        try:
            recommended_products_id = r.get_recommended_products(self.id).index
        except KeyError:
            return []
        return [ get_product_by_id(id) for id in recommended_products_id ]

    def __str__(self):
        return f"<User email={self.email} name={self.name} type={self.type}>"

    def __repr__(self):
        return self.__str__()



# Quick utilities

def new_user(**kwargs):
    return User(**kwargs).save()


def get_user_by_id(id):
    return User(**database.get_user_by_id(id))


def get_user_by_email(email):
    return database.get_user_by_email(email)    


def is_user_admin(email):
    user = User(email=email, password=None)
    return user.is_admin()

def get_user_fields():
        return [ field.capitalize() for field in database.USER_FIELDS ]

def get_all_users(formalize=True):
    return database.get_all_users(formalize=formalize)

def delete_user(user_id):
    return database.delete_user(user_id)

def edit_user(user_id, **fields):
    return database.edit_user(user_id, **fields)

def get_user_ratings_joined_with_products(user_id):
    # remove user_id field, because its used in user's profile

    fields, data = database.get_user_ratings_joined_by_products(user_id)
    # make static fields ( i know thats not a good idea )
    fields = ["PRODUCT_ID", "User Name", "Product name", "Product Image", "Review", "Delete"]
    return fields, data

def get_number_of_users():
    return database.get_number_of_users()