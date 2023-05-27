# Import required libraries and modules
import os
import vk_api
from datetime import datetime
from operator import itemgetter
from typing import Dict, List
from dotenv import load_dotenv

# Import environment variables
load_dotenv()

# Import environment variables
access_token = os.getenv('a_token')

# Initialization of the backend built on the VK api tool
class VkTools:
    def __init__(self, access_token):
        self.api = vk_api.VkApi(token=access_token)

    # Get user profile information
    def get_profile_info(self, user_id):
        fields = 'city,bdate,sex'
        info = self.api.method('users.get', {'user_ids': user_id, 'fields': fields})[0]
        user_info = {
            'id': info['id'],
            'name': f"{info['first_name']} {info['last_name']}",
            'bdate': info.get('bdate', None),
            'city': info.get('city', {}).get('id', None),
            'sex': info.get('sex', None),
        }
        return user_info

    # User search by specified parameters
    def search_users(self, params):
        sex = 2 if params['sex'] == 1 else 1
        city = params['city']
        user_year = int(params['bdate'].split('.')[-1])
        age = datetime.now().year - user_year
        age_from = age - 5
        age_to = age + 5
        offset = 0
        count = 1000
        res = []

        while True:
            users = self.api.method('users.search', {
                'count': count,
                'offset': offset,
                'age_from': age_from,
                'age_to': age_to,
                'sex': sex,
                'city': city,
                'status': 6,
                'is_closed': False,
            }).get('items', [])

            users = [{'id': user['id'], 'name': f"{user['first_name']} {user['last_name']}"}
                     for user in users if not user.get('is_closed')]
            res.extend(users)

            if len(users) < count:
                break
            offset += count
        return res

    # Get User photo
    def get_photos(self, user_id: int) -> List[Dict[str, int]]:
        photos = self.api.method('photos.get', {
            'owner_id': user_id,
            'album_id': 'profile',
            'extended': 1
        })
        photos = photos.get('items', [])
        res = [{'owner_id': photo['owner_id'], 'id': photo['id'],
            'likes': photo['likes']['count'], 'comments': photo['comments']['count']}
            for photo in photos]
        res = sorted(res, key=itemgetter('likes', 'comments'), reverse=True)
        return res


if __name__ == '__main__':
    bot = VkTools(access_token)
    user_info = bot.get_profile_info(user_id=1)
    users = bot.search_users(user_info)
