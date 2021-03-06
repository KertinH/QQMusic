import requests
import time
from sqlalchemy import create_engine,MetaData#引入数据库引擎create_engine以及引入MetaData来创建表格
from sqlalchemy.orm import sessionmaker#引入sessionmaker（用来创建数据工厂）
from sqlalchemy import Table,Column,Text,String,DateTime#引入我们需要用到的属性
from sqlalchemy.sql import insert#引入插入语句



#创建一个数据库引擎，调用create_engin方法，连接postgresql数据库，用户名为postgres，密码为123456，储存地址为本地存储，端口为5432数据库名为postgres
engine = create_engine('postgresql://postgres:123456@localhost:5432/postgres')
meta = MetaData(bind = engine)#将MetaData绑定到引擎上
Session = sessionmaker(bind = engine)#将sessionmaker绑定到引擎上，创建一个session工厂
session = Session()#调用工厂方法来创建一个session对象

QQMusic_table = Table('t_QQmusic',meta,#表名为t_QQmusic,数据库内一定不能有相同表名！！！
                    Column('Album_name',Text,primary_key = True),#将id作为列名（key）,并用primary设置为主key，用Text类型显示
                    Column('Singer',Text),
                    Column('Language',Text),
                    Column('Public_time',DateTime),
                    Column('Album_url',Text),
                    Column('Song_num',String),
                    Column('Song_name', Text),
                    Column('Song_url', Text),
                    Column('Song_src', Text))

meta.create_all()#建立表格



#有的字符串里有空值，用eval将字符串转换成字典的话，有空值会报错，所以我们自己定义一下null且将它作为一个全局变量
global null
null ='tianchong'#填充，也可以直接''

#这个for循环控制页数
for page in range(0,56080,20):
    print('第',str(page / 20 + 1),'页')
    url = 'https://u.y.qq.com/cgi-bin/musicu.fcg'#这个url挺难找的.Chorme的networ下的js里找到的


    #伪造请求头的时候一定记得加referer参数，不然会返回空值
    header = {
        'user-agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
        'cookie':'pt2gguin=o0793832771; RK=uI1Ps5UfHy; ptcz=542d3d9746ec5a0db3088084d36939d99855ad2d6828dcb8779fd96f9c45506c; tvfe_boss_uuid=af179654c3c3dc3c; pgv_pvid=6200432640; o_cookie=793832771; pgv_pvi=2051125248; ts_uid=2694797554; yq_index=0; pgv_si=s8468989952; pgv_info=ssid=s2972046000; ts_refer=www.baidu.com/link; yqq_stat=0; ts_last=y.qq.com/portal/album_lib.html',
        'referer':'https://y.qq.com/portal/album_lib.html'
    }

    #伪造params参数
    pdata = '{"albumlib":{"method":"get_album_by_tags","param":{"area":1,"company":-1,"genre":-1,"type":-1,"year":-1,"sort":2,"get_tags":1,"sin":100,"num":20,"click_albumid":0},"module":"music.web_album_library"}}'.replace('100',str(page))#控制翻页
    parameters = {
        'callback':'getUCGI5812144734908555',
        'g_tk':'5381',
        'jsonpCallback':'getUCGI5812144734908555',
        'loginUin':'0',
        'hostUin':'0',
        'format':'jsonp',
        'inCharset':'utf8',
        'outCharset':'utf-8',
        'notice':'0',
        'platform':'yqq',
        'needNewCode':'0',
        'data':pdata
    }

    response = requests.get(url,headers=header,params=parameters)
    data = eval(response.text.lstrip('getUCGI5812144734908555(').rstrip(')'))#去掉多余的成分，然后用eval将str强转成字典
    data = data['albumlib']['data']['list']
    #print(data)

    #这段用来获取每一页的专辑数据
    aurl = 'https://y.qq.com/n/yqq/album/{}.html#stat=y_new.album_lib.album_name'#url寻找方法跟开始一样
    surl = 'https://y.qq.com/n/yqq/song/{}.html'
    for every in data:
        time.sleep(2)
        album_name = every['album_name']
        singer = every['singers'][0]['singer_name']
        public_time = every['public_time']
        albums_url = aurl.format(every['album_mid'])
        #print('专辑名：',album_name,'\n''歌手：',singer,'\n','发行时间：',public_time,'\n','专辑链接：',albums_url)


        content_url = 'https://shc.y.qq.com/v8/fcg-bin/fcg_v8_album_info_cp.fcg'
        referer = 'https://y.qq.com/n/yqq/album/{}.html'.format(every['album_mid'])
        header = {
            'user-agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
            'cookie': 'pt2gguin=o0793832771; RK=uI1Ps5UfHy; ptcz=542d3d9746ec5a0db3088084d36939d99855ad2d6828dcb8779fd96f9c45506c; tvfe_boss_uuid=af179654c3c3dc3c; pgv_pvid=6200432640; o_cookie=793832771; pgv_pvi=2051125248; ts_uid=2694797554; yq_index=0; pgv_si=s8468989952; pgv_info=ssid=s2972046000; ts_refer=www.baidu.com/link; yqq_stat=0; ts_last=y.qq.com/portal/album_lib.html',
            'referer': referer
        }
        parameters = {
            'albummid': every['album_mid'],
            'g_tk': '5381',
            'jsonpCallback': 'albuminfoCallback',
            'loginUin': '0',
            'hostUin': '0',
            'format': 'jsonp',
            'inCharset': 'utf8',
            'outCharset': 'utf - 8',
            'notice': '0',
            'platform': 'yqq',
            'needNewCode': '0'
        }

        response = requests.get(content_url, headers=header, params=parameters)
        album_data = response.text.lstrip(' albuminfoCallback(').rstrip(')').replace('""','"1"')#数据里有空的""，用"1"替代
        #print(album_data)
        album_data = eval(album_data)#开始这里有是会报语法错误，后来自己好了..不知道为什么，可能是数据有问题？
        album_data = album_data['data']
        company = album_data['company']
        album_desc = album_data['desc']
        song_num = album_data['cur_song_num']
        language = album_data['lan']
        list_data = album_data['list']
        print('\n','-----------------------------------------------------------------------','\n','专辑名：',album_name,'\n''歌手：',singer,'\n','语种：',language,'\n','发行时间：',public_time,'\n','专辑链接：',albums_url,'\n','歌曲数：',song_num)

        #这段获取歌曲数据
        for every_album in list_data:
            #有的专辑没有版权，看不了专辑里的歌曲信息，所以做一个判断，避免异常
            if type(every_album) is not str:
                song_name = every_album['songname']
                song_id = every_album['songid']
                song_url = surl.format(every_album['songmid'])
                print('歌名：',song_name, '\n','歌曲链接：',song_url)
            else:
                print('抱歉，因版权限制，暂无法查看该专辑下歌曲')
                continue

            #获取歌曲的源地址
            song_content_url = 'https://c.y.qq.com/v8/fcg-bin/fcg_play_single_song.fcg'
            song_referer = 'https://y.qq.com/n/yqq/song/{}.html'.format(every_album['songmid'])
            song_header = {
                'user-agent':'ozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.108 Safari/537.36',
                'cookie':'pt2gguin=o0793832771; RK=uI1Ps5UfHy; ptcz=542d3d9746ec5a0db3088084d36939d99855ad2d6828dcb8779fd96f9c45506c; tvfe_boss_uuid=af179654c3c3dc3c; pgv_pvid=6200432640; o_cookie=793832771; pgv_pvi=2051125248; ts_uid=2694797554; yq_index=0; ts_refer=www.baidu.com/link; pgv_si=s3682846720; yqq_stat=0; ts_last=y.qq.com/n/yqq/song/000y3R4D3Lcdsj.html',
                'referer':song_referer
            }
            song_parameters = {
                'songmid': every_album['songmid'],
                'tpl':'yqq_song_detail',
                'format': 'jsonp',
                'callback': 'getOneSongInfoCallback_menu_share',
                'g_tk': '5381',
                'jsonpCallback': 'getOneSongInfoCallback_menu_share',
                'loginUin': '0',
                'hostUin': '0',
                'format': 'jsonp',
                'inCharset': 'utf8',
                'outCharset': 'utf - 8',
                'notice': '0',
                'platform': 'yqq',
                'needNewCode': '0'
            }

            song_response = requests.get(song_content_url,headers=song_header,params=song_parameters)
            song_data = song_response.text.lstrip('getOneSongInfoCallback_menu_share(').rstrip(')')
            song_data = eval(song_data)
            song_src = song_data['url'][str(song_id).lstrip(' ')]
            print('源地址：',song_src)

            i = insert(QQMusic_table)
            # 插入数据
            i = i.values({'Album_name': album_name,
                          'Singer': singer,
                          'Language': language,
                          'Public_time': public_time,
                          'Album_url': albums_url,
                          'Song_name': song_name,
                          'Song_url': song_url,
                          'Song_src': song_src})
            session.execute(i)#将数据插入表格
session.commit()#提交到数据库中


#####################################
#其实就是分析网站比较麻烦..其他都不算难
#####################################
#不想换成函数块了.....................愉快地决定不换了 
