import requests
import json
import os
import time
import re
import argparse
import sys


def get_id_from_username(username, oauth, client_id):
    # using twitch's api to get id from username
    # expects to get a username, oauth token and client_id as strings
    response = requests.get('https://api.twitch.tv/helix/users?login=' + username,
                            headers={'Authorization': 'Bearer ' + oauth,
                                     'Client-ID': client_id})
    if response.status_code != 200:
        raise Exception(
            'Response not successful: ' + str(response.status_code) + ' ' + str(response.json()))
    else:
        response = response.json()
        user_id = response.get('data', 'none')
        if user_id != 'none':
            user_id = user_id[0].get('id',
                                     'none')  # response is JSON with a list (with one item) in 'data' var
        return user_id


def validate_token(oauth):
    # checking if oauth token matches entered username
    response = requests.get('https://id.twitch.tv/oauth2/validate',
                            headers={'Authorization': 'OAuth ' + oauth})
    if response.status_code == 200:
        # if response is 200 token is valid
        response = response.json()
        if 'login' in response.keys():
            print('login is ' + response['login'])
            return response['login']
    return False


parser = argparse.ArgumentParser('Download all of the clips clipped by you')
parser.add_argument('--cursor', '-cu', help='use this to continue from a previous session', default=None)
parser.add_argument('--client_id', '-c', help='using twitch\'s client id, if it doesn\'t work try your own',
                    default='kimne78kx3ncx6brgo4mv6wki5h1ko')
parser.add_argument('--oauth', '-o', required=True, help='your oauth token taken from twitch. DO NOT SHARE THIS')
parser.add_argument('--views', '-v', help='to sort the clips downloaded by most viewed', action='store_true')
parser.add_argument('--limit', '-li', help='to limit the amount of clips downloaded, '
                                           'default behavior is to download all', default=0, type=int)
parser.add_argument('--fname', '-fn', help='this can be use to structure each clip\'s file name using.'
                                           ' please read the readme for an extensive guide of how to'
                                           ' format the name. also make sure your filename + path are not pass 260 '
                                           'chars or windows might be angry', default=['%v', '%n'],
                    choices=['%t', '%d', '%v', '%l', '%g', '%s', '%li', '%sl'], nargs='+')
parser.add_argument('--append_char', '-ac', help='character used between two variables in file name'
                                                 ' e.g: -ac _ default formatting will be- views: 1_name: clipname.mp4'
                    , default='_')
args = parser.parse_args()

# assigning all arguments
append_char = args.append_char
if re.match('<|>|:|\"|/|\\|\||\?|\*', append_char):
    sys.exit('windows doesn\'t like your append character, please choose another')
cursor = args.cursor
client_id = args.client_id
oauth = args.oauth
sort_by_views = args.views
limit = args.limit
fname = args.fname
login = validate_token(oauth)
if not login:
    sys.exit('oauth token doesn\'t work')
twitch_id = get_id_from_username(login, args.oauth, args.client_id)
append_word = {'%t': 'title- ', '%d': 'date- ', '%v': 'views- ', '%l': 'user- ', '%g': 'game- ', '%s': 'streamer- ',
               '%li': 'link- ', '%sl': 'slug- '}
# this is the template we must follow if we want twitch to answer us
body = [{'operationName': 'ClipsManagerTable_User', 'variables': {'login': login, 'limit': 20, 'criteria':
    {'sort': 'CREATED_AT_DESC', 'period': 'ALL_TIME', 'curatorID': twitch_id}, 'cursor': cursor}, 'extensions':
    {'persistedQuery': {'version': 1, 'sha256Hash': '0bc0fef26eb0739611d8ac1aa754ed44630d96a87854525bf38520ffe26460d4'}}}]

if sort_by_views:
    body[0]['variables']['criteria']['sort'] = 'VIEWS_DESC'
print('loading clips')
headers = {'Client-ID': client_id, 'Authorization': 'OAuth ' + oauth}
response = requests.post('https://gql.twitch.tv/gql', data=json.dumps(body), headers=headers)
clips = response.json()
regex = re.compile('<|>|:|\"|/|\\|\||\?|\*')  # will be used later to remove chars windows doesn't like as file names
edges = []
hasClips = True
while hasClips:
    if limit < 20:
        body[0]['variables']['limit'] = limit
        limit -= 20  # when limit is below 0 we don't hasClips will be false so we don't really care
    response = requests.post('https://gql.twitch.tv/gql', data=json.dumps(body), headers=headers)
    clips = response.json()
    if response.status_code == 200 and 'errors' not in clips[0].keys():  # making sure the response has clips
        for clip in clips[0]['data']['user']['clips']['edges']:
            # all the clips are in a list under edges
            # collecting interesting values into a tuple, also removing the chars mentioned above with regex
            # (title+views, download_link, created_at)
            title = regex.sub(' ', clip['node']['title'])
            views = clip['node']['viewCount']
            download_url = clip['node']['videoQualities'][0]['sourceURL']
            date = clip['node']['createdAt']
            streamer = clip['node']['broadcaster']['login']
            game = clip['node']['game']['name']
            link = clip['node']['url']
            slug = clip['node']['slug']
            edges.append({'%t': title, '%s': streamer, '%v': str(views), '%d': date, '%l': login, '%g': game, '%li': link,
                          '%sl': slug, 'download_url': download_url})
        if clips[0]['data']['user']['clips']['pageInfo']['hasNextPage'] is True and clips[0]['data']['user']['clips']['edges'][-1]['cursor'] and limit > 0:
            # checking if there's a next page and making sure the cursor is not null
            # adding the cursor to the next request because we need it to access the next page of clips
            body[0]['variables']['cursor'] = clips[0]['data']['user']['clips']['edges'][-1]['cursor']
            # appending the cursor as a makeshift way of splitting the list to pages, will print it between clips downloaded
            # so users don't have to start from the first page every time they use the script
            edges.append(body[0]['variables']['cursor'])
        else:
            hasClips = False
    else:
        sys.exit('couldn\'t get clips from twitch. please make sure the oauth is taken as instructed in the readme '
                 'page. here\'s the response we received from twitch: ' + str(clips))
print(str(len(edges)) + ' clips found, starting download')
for slugger in edges:
    if isinstance(slugger, str):
        # if the item is the cursor string only print it for the user
        print('cursor is ' + slugger + ' you could use this as a checkpoint next time you start a download with the'
                                       ' argument --cursor ' + slugger)
    else:
        # slicing clip time to bits
        clip_year = slugger['%d'][:4]
        clip_month = slugger['%d'][5:7]
        clip_day = slugger['%d'][8:10]
        clip_hour = slugger['%d'][11:13]
        clip_minute = slugger['%d'][14:16]
        clip_second = slugger['%d'][17:19]
        formatted_time = clip_year + ' ' + clip_month + ' ' + clip_day + ' ' + clip_hour + ' ' + clip_minute + ' ' + clip_second
        struct_time = time.strptime(formatted_time, '%Y %m %d %H %M %S')
        epoch = time.mktime(struct_time)
        slugger['%d'] = time.ctime(epoch).replace(':', '-')  # replacing : with - for windows file name.
        # building the file name based on the format given as run arg
        file_name = ''
        for field in fname:
            file_name += append_word[field]
            file_name += str(slugger[field]) + append_char
        slugger['file_name'] = regex.sub(' ', file_name[:-1])  # the loop above also added the appended char at the end
        # also removing chars windows might dislike again just to be sure
        # downloading the clip
        response = requests.get(slugger['download_url'], stream=True)
        data = b''
        try:
            for chunk in response.iter_content(chunk_size=None):
                if chunk:
                    data += chunk
            # saving the clip
            open(slugger['file_name'] + '.mp4', 'wb').write(data)
            # changing modified time to time of clip creation
            os.utime(slugger['file_name'] + '.mp4', (epoch, epoch))
            print(slugger['file_name'] + ' downloaded successfully')
        except OSError:
                print('OS ERROR NUMBER 22. Windows probably didn\'t like the '
                      'name of the clip. Try to change it by removing special characters ' + slugger['file_name'])


