<<<<<<< HEAD
# import vk_api
import json as js

# session = vk_api.VkApi(login='79252578111',
#                        password='Rkfcnthbpfwbz2020!',
#                        app_id=7897293, 
#                        client_secret="1DklqV9PntvezFClHMOM",
#                        api_version="5.131",
#                        scope='8192')

# auth = session.server_auth()

# print(dir(auth))

# vk = session.code_auth('5977c6005977c6005977c600f5590f46cd559775977c6003991c1542e60ad76efcdcdb2', 'https://oauth.vk.com/blank.html')

with open('stuff/config.json', 'r', encoding='utf8') as file:
    config = js.load(file)
    roles_id = config['gorails']['roles_id']
    lst = list(map(int, roles_id.values()))
    print(lst)
    for thing in lst:
        print(thing)

=======
# import vk_api
import json as js

# session = vk_api.VkApi(login='79252578111',
#                        password='Rkfcnthbpfwbz2020!',
#                        app_id=7897293, 
#                        client_secret="1DklqV9PntvezFClHMOM",
#                        api_version="5.131",
#                        scope='8192')

# auth = session.server_auth()

# print(dir(auth))

# vk = session.code_auth('5977c6005977c6005977c600f5590f46cd559775977c6003991c1542e60ad76efcdcdb2', 'https://oauth.vk.com/blank.html')

with open('stuff/config.json', 'r', encoding='utf8') as file:
    config = js.load(file)
    roles_id = config['gorails']['roles_id']
    lst = list(map(int, roles_id.values()))
    print(lst)
    for thing in lst:
        print(thing)

>>>>>>> 75b13045fc71e61cb736d610ba0be5d6d89e8926
# https://oauth.vk.com/authorize?client_id=7897293&display=page&redirect_uri=https://oauth.vk.com/blank.html&scope=8192&response_type=token&v=5.131&state=123456