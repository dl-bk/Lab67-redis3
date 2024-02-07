import redis
import bcrypt
import json
import datetime

class SocialNetworkApp:
    def __init__(self, redis_host='localhost', redis_port=6379, redis_db=1) -> None:
        self.redis_client = redis.StrictRedis(host=redis_host, port=redis_port, db=redis_db)
    def add_user(self, username, password) -> bool:
        if self.redis_client.hexists('users', username):
            print('User already exists')
            return False
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        user_data = {
            'password_hash': password_hash.decode('utf-8'),
            'fullname': '',
            'friends': [],
            'posts': []
        }
        self.redis_client.hset('users', username, json.dumbs(user_data))
        print("User successfully registered")
        return True
    
    def log_in(self, username, password):
        stored_user_data = self.redis_client.hget('users', username)
        if stored_user_data:
            user_data = json.loads(stored_user_data)
            stored_password_hash = user_data.get('password_hash')
            if stored_password_hash and bcrypt.checkpw(password.encode('utf-8'), stored_password_hash.encode('utf-8')):
                print(f"You are log in as {username}")
                self.current_user = username
                return True
            print("Incorrect login or password")
            return False
        else:
            print("User is not found")
            return False
    def delete_user(self, username):
        if self.redis_client.hexists('users', username):
            self.redis_client.hdel('users', username)
            print("User deleted")
        else:
            print("User is not found")
    
    def edit_user(self, username, new_data):
        if not self.redis_client.hexists('users', username):
            print("User is not found")
            return
        stored_data = self.redis_client.hget('user', username)
        if stored_data:
            try:
                user_data = json.loads(stored_data)
            except json.JSONDecodeError:
                print("ERROR: Decode Error")
                return
        else:
            print("User data is empty or corrupted")
            return
        for key, value in new_data.items():
            if value:
                user_data[key] = value
        
        self.redis_client.hset('users', username, json.dumps(user_data))
        print("Information udated")
    
    def search_user_by_name(self, fullname):
        all_users = self.redis_client.hgetall('users')
        for username, user_info in all_users.items():
            user_data = json.loads(user_info)
            if user_data.get('fullname') == fullname:
                return user_data
        return "User is not found"
    
    def view_user_info(self, username):
        if self.redis_client.hexists('users', username):
            return json.loads(self.redis.hget('users', username))
        else:
            return "User is not found"
    
    def view_user_friends(self, username):
        pass
    
    def view_user_posts(self, username):
        pass
    
    def add_friends(self, username, friend_username) -> bool:
        if not self.redis_client.hexists('users', username) or not  self.redis_client.hexists('users', friend_username):
            print("One of users is not found")
            return False
        user_data = json.loads(self.redis_client.hget('users', username))
        if 'friends' not in user_data:
            user_data['friends'] = []
        if friend_username not in user_data['friends']:
            user_data['friends'].append(friend_username)
            self.redis_client.hset('users', username, json.dumps(user_data))
            print(f'{friend_username} was added to friends list')
            return True
        else:
            print(f'{friend_username} already in friends list')
            return False
    
    def add_post(self, username, text):
        if not self.redis_client.hexists('users', username):
            print("User is not found")
            return False
        user_data = json.loads(self.redis_client.hget('users', username))
        post = {
            'text': text,
            'date': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        if 'posts' not in user_data:
            user_data['posts'] = []
        user_data['posts'].append(post)
        self.redis_client.hset('users', username, json.dumps(user_data))
        print(f"New post created by {username}")
        return True