import requests
import pandas as pd
from sqlalchemy import create_engine


def main():
    # owner_id = [-29534144,-30666517,-26419239,-45441631,-12382740, -460389]
    domainsf = open('domains.txt', 'r')
    print(type(domainsf))
    domains = domainsf.read().split('\n')
    domains.remove('')
    print(domains)

    all_list = []
    cur_list = []
    likes_list = []

    for public in domains:
        r = requests.get('https://api.vk.com/method/wall.get',
                         params={'type': 'post', 'domain': public, 'count': 100, 'offset': 1, 'v': 5.68,
                                 'access_token': "3dfbbd3c3dfbbd3c3dfbbd3c233da747e033dfb3dfbbd3c6455c9cf7ed4c76fa76babb4"})

        data = r.json()

        for post in range(99):
           # print(data)
            try:
                likes_list.append(data['response']['items'][post]['likes']['count'])
                cur_list.append(data['response']['items'][post]['attachments'][0]['photo']['photo_604'])
            except KeyError:
                continue

            tmp_dict= []
            tmp_dict.append(data['response']['items'][post]['likes']['count'])
            tmp_dict.append(data['response']['items'][post]['attachments'][0]['photo']['photo_604'])
            tmp_str = "https://vk.com/wall" + str(data['response']['items'][post]['owner_id'])\
                  +'_'+str(data['response']['items'][post]['id'])
            tmp_dict.append(tmp_str)
            print(tmp_dict)
            all_list.append(tmp_dict)


    print(all_list)
    frame = pd.DataFrame(all_list, columns = ['likes', 'img', 'post'])
    print(frame)
    engine = create_engine('postgresql://sammyq:sammy-password@localhost:5432/sammy')

    frame.to_sql("bd3", engine)


if __name__ == '__main__':
    main()
