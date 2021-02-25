import requests
import json
import execjs
import os
import time

class QQmusic(object):
    
    def __init__(self):

        self.headers = {
            "origin": "https://y.qq.com",
            "referer": "https://y.qq.com/",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/88.0.4324.150 Safari/537.36"
        }
        # self.playlist_url = 

    def parse_url(self,url):
        
        response = requests.get(url,headers=self.headers)
        return response.content
        
    def get_song_info(self,playlist_response):
        
        playlist = json.loads(playlist_response)
        songlist = playlist["cdlist"][0]["songlist"]
        total_song_num = playlist["cdlist"][0]["total_song_num"]
        song_list = []

        print("该歌单共有 %-3s首歌，详情如下：" % total_song_num)

        for key,song in enumerate(songlist):
            s = {}
            song_name = song["title"]
            singer_name = song["singer"][0]["title"]
            #获取下载地址的关键信息：mid和sign
            mid = song["mid"]
            #获取sign
            # 获取sign的关键参数
            song_id = song["id"]
            data = '{"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"9316375552","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"9316375552","songmid":["%s"],"songtype":[0],"uin":"278178352","loginflag":1,"platform":"20","ctx":1}},"comm":{"uin":278178352,"format":"json","ct":24,"cv":0}}' % (mid,)
            sign = self.get_sign(data)
            # print(sign)

            s["song_name"] = song_name
            s["singer_name"] = singer_name
            s["mid"] = mid
            s["sign"] = sign
            song_list.append(s)
            s = {}
            print("%s.%s------>%s" % (key+1,song_name,singer_name))
        return song_list,total_song_num
    def get_sign(self,data):

        with open(r'sign.js', "r", encoding='utf-8') as f:
            ctx = execjs.compile(f.read())
            sign = ctx.call('get_sign', data)
        return sign

    def get_purl(self,sign,mid):
        vkey_url = 'https://u.y.qq.com/cgi-bin/musics.fcg?-=getplaysongvkey7760853817973581&g_tk=1259945497&sign=%s&loginUin=278178352&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0&data={"req":{"module":"CDN.SrfCdnDispatchServer","method":"GetCdnDispatch","param":{"guid":"9316375552","calltype":0,"userip":""}},"req_0":{"module":"vkey.GetVkeyServer","method":"CgiGetVkey","param":{"guid":"9316375552","songmid":["%s"],"songtype":[0],"uin":"278178352","loginflag":1,"platform":"20","ctx":1}},"comm":{"uin":278178352,"format":"json","ct":24,"cv":0}}' % (sign,mid)
        purl = json.loads(self.parse_url(vkey_url))["req_0"]["data"]["midurlinfo"][0]["purl"]
        return purl 

    def get_song_content(self,purl):
        time.sleep(3)
        murl = 'https://isure.stream.qqmusic.qq.com/'+purl
        music = self.parse_url(murl)
        return music
    def save_music(self,music,filename):
        with open('./QQMusic/'+filename+'.mp3','wb') as f:
            f.write(music)
        



    def run(self):

        #1 获取的歌单的url##disstid=6371097821disstid这个改变可下载别的歌单
        playlist_url = 'https://c.y.qq.com/qzone/fcg-bin/fcg_ucc_getcdinfo_byids_cp.fcg?type=1&json=1&utf8=1&onlysong=0&new_format=1&disstid=7893127872&g_tk_new_20200303=1259945497&g_tk=1259945497&loginUin=278178352&hostUin=0&format=json&inCharset=utf8&outCharset=utf-8&notice=0&platform=yqq.json&needNewCode=0'
    
        #2 发送请求，获取响应
        playlist_response = self.parse_url(playlist_url)

        #3 取出歌单中的需要的信息
        song_list,total_song_num = self.get_song_info(playlist_response)

        while True:
            is_sure = input("请确认是否下载？(y/n)")
            if is_sure=='y':
                if not os.path.exists('QQMusic'):
                    os.mkdir('QQMusic')

                i=0
                #4 获取purl
                for song in song_list:

                    print('%s' %song["song_name"],'-'*10,'>正在下载')

                    purl = self.get_purl(song["sign"],song["mid"])
                    #5 构造关键的音乐数据地址,获取音乐文件内容
                    music = self.get_song_content(purl)
                    #6 保存为音乐文件
                    self.save_music(music,song["song_name"])

                    i+=1
                    if i==total_song_num:
                        print('%s' %song["song_name"],'-'*10,'>下载完成')
                        print('下载完成')
                    else:
                        print('%s' %song["song_name"],'-'*10,'>下载完成')
                        print('剩余%s首歌未下载' % (total_song_num-i))
                if i==total_song_num:
                    break

            elif is_sure=='n':
                break

if __name__ == '__main__':
    music = QQmusic()
    music.run()