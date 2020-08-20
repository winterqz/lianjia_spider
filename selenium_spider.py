from parsel import Selector
from selenium import webdriver
import requests
import random
import pymysql
# get_house_url()
import logging  # 引入logging模块
import os.path
import time
import threading

st = threading.Semaphore(2)
targets = '''
松江 闵行 浦东新区 宝山区 
嘉定区   徐汇区  杨浦区
'''

fileds = '''
租金价格、公交、地铁、公园、超市、医院、学校、房屋面积、朝向、房龄、有无车位、水 电'''

fileds_ok = '''
公交、地铁、公园、超市、医院、学校、房龄'''

# chrome_options = webdriver.ChromeOptions()
# chrome_options.add_argument('--headless')

# 第一步，创建一个logger
logger = logging.getLogger()
logger.setLevel(logging.INFO)  # Log等级总开关
# 第二步，创建一个handler，用于写入日志文件
# rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))
log_path = os.path.dirname(os.getcwd()) + '/Logs/'
log_name = log_path + "xuhui" + '.log'
logfile = log_name
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关
# 第三步，定义handler的输出格式
formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
# 第四步，将logger添加到handler里面
logger.addHandler(fh)


def each_house(house_url):
    '''
    单个租房的链接
    :param house_url:
    :return:
    '''
    # example_house_url = "https://sh.lianjia.com/zufang/SH2563082393556615168.html"
    driver = webdriver.Chrome(executable_path="chromedriver.exe")
    # driver.set_page_load_timeout(8)
    # driver.implicitly_wait(30)

    driver.get(house_url)
    if "你访问的房源已失效" in driver.page_source or "你访问的房源已下架" in driver.page_source:
        driver.quit()
    driver.maximize_window()
    # time.sleep(1)
    # driver.refresh()
    # time.sleep(1)

    # 关闭窗口提示
    try:
        notice = driver.find_element_by_class_name("notice-close").click()
    except:
        print("无需关闭提示")

    # driver.execute_script('window.scrollTo(0,700)')
    # time.sleep(500)

    try:
        # 下滑页面
        div = driver.find_element_by_xpath('//*[@id="around"]')
        # 滑动滚动条到某个指定的元素
        js4 = "arguments[0].scrollIntoView();"
        # 将下拉滑动条滑动到当前div区域
        driver.execute_script(js4, div)
    except:
        logger.info("下滑失败")

    time.sleep(1.5)
    # print(driver.page_source)
    _dict = {}
    sel = Selector(text=driver.page_source)
    try:
        # 价格
        price_num = sel.xpath('//div[@class="content__aside--title"]/span/text()').get()
        price_unit = sel.xpath('//div[@class="content__aside--title"]/text()').getall()
        # print(price_unit)
        price = str(price_num) + "".join(price_unit).strip().replace("\n", "").replace(" ", "")
        # print(price)
        _dict['price'] = price
    except:
        _dict['price'] = ''
    # 租赁方式
    # lease_way = sel.xpath('//ul[@class="content__aside__list"]/li[1]/text()').get().strip()
    try:
        # 房屋面积
        house_area = sel.xpath('//div[@class="content__article__info"]/ul/li[2]/text()').get().strip()
        print(house_area)
        _dict['house_area'] = house_area
    except:
        _dict['house_area'] = ""
    try:
        # 朝向
        house_towards = sel.xpath('//div[@class="content__article__info"]/ul/li[3]/text()').get().strip()
        _dict['house_towards'] = house_towards
    except:
        _dict['house_towards'] = ""
    try:
        # 车位
        car = sel.xpath('//div[@class="content__article__info"]/ul/li[11]/text()').get().strip()
        _dict['car'] = car
    except:
        _dict['car'] = ""

    try:
        # 水
        water = sel.xpath('//div[@class="content__article__info"]/ul/li[12]/text()').get().strip()
        _dict['water'] = water
    except:
        _dict['water'] = ""

    try:
        # 电
        electricity = sel.xpath('//div[@class="content__article__info"]/ul/li[14]/text()').get().strip()
        _dict['electricity'] = electricity
    except:
        _dict['electricity'] = ""

    # print(_dict)
    # subway_button = driver.find_element_by_id('//*[@id="around"]/div/div[2]/ul/li').click()
    try:
        # 地铁
        # print(driver.page_source)
        subway_all = sel.xpath('//*[@class="content__map--overlay__list"]/li')
        subway_info_list = []
        for info in subway_all:
            subway_station = info.xpath('./p/text()').get()
            subway_distance = info.xpath('./p/span/text()').get()
            subway_num = info.xpath('./p[2]/text()').get()

            subway_dict = {}
            subway_dict["地铁站点名称"] = subway_station
            subway_dict["距地铁距离"] = subway_distance
            subway_dict["地铁线路"] = subway_num
            subway_info_list.append(subway_dict)
        # print(subway_info_list)
        _dict['subway'] = subway_info_list
    except:
        _dict['subway'] = []

    # subway = sel.xpath('//*[@id="around"]/div/div[2]/ul[2]/li/p[2]/text()').get()
    # print(subway)
    try:
        bus_button = driver.find_element_by_xpath('//*[@id="around"]/div/div[2]/ul/li[2]').click()
        time.sleep(0.8)
        # bus = driver.find_element_by_xpath('//*[@id="around"]/div/div[2]/ul[2]/li[1]/p[2]').text
        # print(bus)
        sel = Selector(text=driver.page_source)
        # print(driver.page_source)
        # print("===========")
        bus_all = sel.xpath('//*[@class="content__map--overlay__list"]/li')
        # print(bus_all)
        bus_info_list = []
        for info in bus_all:
            bus_station = info.xpath('./p/text()').get()
            bus_distance = info.xpath('./p/span/text()').get()
            bus_num = info.xpath('./p[2]/text()').get()

            bus_dict = {}
            bus_dict["公交站点名称"] = bus_station
            bus_dict["距公交站距离"] = bus_distance
            bus_dict["公交车线路"] = bus_num
            bus_info_list.append(bus_dict)
        # print(bus_info_list)
        _dict['bus'] = bus_info_list
    except:
        _dict['bus'] = []

    # time.sleep(5)
    # driver.close()
    try:
        # 学校
        school_button = driver.find_element_by_xpath('//*[@id="around"]/div/div[2]/ul[1]/li[3]').click()
        time.sleep(0.8)
        sel = Selector(text=driver.page_source)
        school_all = sel.xpath('//*[@class="content__map--overlay__list"]/li')
        # print(bus_all)
        school_info_list = []
        for info in school_all:
            school_name = info.xpath('./p/@title').get()
            school_dictance = info.xpath('./p/span/text()').get()
            school_address = info.xpath('./p[2]/text()').get()

            school_dict = {}
            school_dict["学校名称"] = school_name
            school_dict["距学校距离"] = school_dictance
            school_dict["学校地址"] = school_address
            school_info_list.append(school_dict)
        # print(school_info_list)
        _dict['school'] = school_info_list
    except:
        _dict['school'] = []
    # print(_dict)
    try:
        # 医院
        hospital_button = driver.find_element_by_xpath('//*[@id="around"]/div/div[2]/ul[1]/li[4]').click()
        time.sleep(0.8)
        sel = Selector(text=driver.page_source)
        hospital_all = sel.xpath('//*[@class="content__map--overlay__list"]/li')
        # print(bus_all)
        hospital_info_list = []
        for info in hospital_all:
            hospital_name = info.xpath('./p/@title').get()
            hospital_dictance = info.xpath('./p/span/text()').get()
            hospital_address = info.xpath('./p[2]/text()').get()

            hospital_dict = {}
            hospital_dict["医院名称"] = hospital_name
            hospital_dict["距医院距离"] = hospital_dictance
            hospital_dict["医院地址"] = hospital_address
            hospital_info_list.append(hospital_dict)
        print(hospital_info_list[0])
        _dict['hospital'] = hospital_info_list
    except:
        _dict['hospital'] = []

    # print(_dict)
    try:
        # 超市餐饮
        supermarket_button = driver.find_element_by_xpath('//*[@id="around"]/div/div[2]/ul[1]/li[6]').click()
        time.sleep(1)
        sel = Selector(text=driver.page_source)
        supermarket_all = sel.xpath('//*[@class="content__map--overlay__list"]/li')
        # print(bus_all)
        supermarket_info_list = []
        for info in supermarket_all:
            supermarket_name = info.xpath('./p/@title').get()
            supermarket_dictance = info.xpath('./p/span/text()').get()
            supermarket_address = info.xpath('./p[2]/text()').get()

            supermarket_dict = {}
            supermarket_dict["超市|餐饮 名称"] = supermarket_name
            supermarket_dict["距 超市|餐饮 距离"] = supermarket_dictance
            supermarket_dict["超市|餐饮 地址"] = supermarket_address
            supermarket_info_list.append(supermarket_dict)
        print(supermarket_info_list[0])
        _dict['supermarket'] = supermarket_info_list
    except:
        _dict['supermarket'] = []

    # print(_dict)
    # print(driver.window_handles)
    # time.sleep(500)
    driver.quit()
    # if len(driver.window_handles) == 5:
    #     driver.quit()
    return _dict


# example_house_url = "https://sh.lianjia.com/zufang/SH2563082393556615168.html"


def read_url_and_beging(name):
    # 连接database
    conn = pymysql.connect(
        host="47.105.33.84",
        user="root", password="wzawzj14",
        database="lianjia",
    )

    # 得到一个可以执行SQL语句的光标对象
    cursor = conn.cursor(cursor=pymysql.cursors.DictCursor)  # 执行完毕返回的结果集默认以元组显示
    query_sql = '''SELECT * FROM {} WHERE STATUS = "2"'''.format(name)
    cursor.execute(query_sql)
    query_res = cursor.fetchall()
    conn.commit()
    # print(query_res)
    for item in query_res:
        if "独栋" in item['name']:
            continue
        url = item['url']
        try:
            logger.info("正在爬取第{}/{}个".format(query_res.index(item), len(query_res)))
            print("正在爬取第{}/{}个".format(query_res.index(item), len(query_res)))
            start = time.time()
            info_dict = each_house(url)
            price = info_dict['price']
            house_area = info_dict['house_area']
            house_towards = info_dict['house_towards']
            car = info_dict['car']
            water = info_dict['water']
            electricity = info_dict['electricity']
            subway = str(info_dict['subway'])
            bus = str(info_dict['bus'])
            school = str(info_dict['school'])
            hospital = str(info_dict['hospital'])
            supermarket = str(info_dict['supermarket'])

            update_sql = '''update %s set price="%s",house_area="%s",house_towards="%s",car="%s",water="%s",electricity="%s",subway="%s",bus="%s",school="%s",hospital="%s",supermarket="%s",status="3" where url="%s";''' % (
                name, price, house_area, house_towards, car, water, electricity, subway, bus, school, hospital,
                supermarket,
                url)
            cursor.execute(update_sql)
            conn.commit()
            end = time.time()

            logger.info("链接为|{}|爬取完毕，共花费|{}|秒".format(url, end - start))
            print("链接为|{}|爬取完毕，共花费|{}|秒".format(url, end - start))
            # break
        except:
            spider_fail_sql = '''update %s set status="4" where url="%s";''' % (name, url)
            cursor.execute(spider_fail_sql)
            conn.commit()
            logger.info("链接为|{}|爬取失败".format(url))
            print("链接为|{}|爬取失败".format(url))


# house_area, house_towards, car, water, electricity, subway, bus, school, hospital, supermarket

def main():
    t1 = threading.Thread(target=read_url_and_beging, args=("songjiang",))
    t1.start()
    t2 = threading.Thread(target=read_url_and_beging, args=("baoshan",))
    t2.start()


targets_all = '''
松江 闵行 浦东新区 宝山区 
嘉定区   徐汇区  杨浦区
'''

targets_ok = '''
 
嘉定区   杨浦区
'''
# read_url_and_beging()
if __name__ == '__main__':
    main()


def get_house_url():
    '''
    松江 闵行 浦东新区 宝山区
    嘉定区   徐汇区  杨浦区
    杨浦区
    松江
    闵行
    浦东新区
    宝山区
    嘉定区
    徐汇区
    :return:
    '''
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/81.0.4044.138 Safari/537.36",
        "Cookie": "lianjia_uuid=e59d20dd-8625-4dc6-8e5c-8864082874bc; _smt_uid=5f340084.401a8e66; sensorsdata2015jssdkcross=%7B%22distinct_id%22%3A%22173e32208ce226-06355f41006cec-d373666-2073600-173e32208cfb8c%22%2C%22%24device_id%22%3A%22173e32208ce226-06355f41006cec-d373666-2073600-173e32208cfb8c%22%2C%22props%22%3A%7B%22%24latest_traffic_source_type%22%3A%22%E8%87%AA%E7%84%B6%E6%90%9C%E7%B4%A2%E6%B5%81%E9%87%8F%22%2C%22%24latest_referrer%22%3A%22https%3A%2F%2Fwww.baidu.com%2Flink%22%2C%22%24latest_referrer_host%22%3A%22www.baidu.com%22%2C%22%24latest_search_keyword%22%3A%22%E6%9C%AA%E5%8F%96%E5%88%B0%E5%80%BC%22%7D%7D; _ga=GA1.2.1500481225.1597243527; select_city=310000; lianjia_ssid=28dd9fc3-2e53-4a2c-9590-35810ed4bd6f; _gid=GA1.2.1302293989.1597415470; srcid=eyJ0Ijoie1wiZGF0YVwiOlwiODZhMGY4MjBmOGNhNjczMDI0NzM3YjUwYzJiMDIxYzFjNDM4YTFhYTUzMmUwNjM5MDA1ODkzZDZiNzZiYWY5ZDVkOGQwNDY0YmIzMjg2Zjg0Njc2ODFlNzZhZTA1YjAxMjAwZTlmMmJkZGFkYTAyNzNmYTI3NzIxNzE0ZjVmN2MyZGVhMTA0M2E0ZTRmOGVkZTczOWI2YTNmOGEyYTQwOWIwMGE1YWQwMTFhMzA0YjU3MDY5ODMyMjM4MDAzYmQ1YTZjOTJlMjUxZDQzYTc5OWIwNmMzZjJjN2Y2NzRmYWNlZmVmNDI0ZTdhNGNlYjljMDFjMmMxZGZjMmE1NDVhZGFmNzIwOTliY2Q1YzQ0YWJiNGU2Y2Y3ZmEyM2MyNzE3NzAxZmI2ODRiZDg5YTg5NDliMmMyZTM3ODc0NGJhMzgwY2I3ZGEwOTEzZDBmYWZmYjkxMmM1ZWQ2ZTM5Zjc3MFwiLFwia2V5X2lkXCI6XCIxXCIsXCJzaWduXCI6XCJiNDMyNDQ2ZFwifSIsInIiOiJodHRwczovL3NoLmxpYW5qaWEuY29tL3p1ZmFuZy95YW5ncHUvcGcxLyNjb250ZW50TGlzdCIsIm9zIjoid2ViIiwidiI6IjAuMSJ9"
    }
    with open("xuhui.txt", "a+")as f:
        for num in range(1, 59):
            url = "https://sh.lianjia.com/zufang/xuhui/pg{}/#contentList".format(num)
            res = requests.get(url, headers=headers)
            print("正在爬取第{}页的租房列表".format(num))
            print(res)
            res.encoding = res.apparent_encoding
            sel = Selector(text=res.text)
            all_info = sel.xpath('//div[@class="content__list"]/div')
            for info in all_info:
                each_info = {}
                house_url = info.xpath('./div/p/a/@href').get()
                title = info.xpath('./div/p/a/text()').get().strip()
                each_info['house_url'] = "https://sh.lianjia.com" + house_url
                each_info['title'] = title
                print(each_info)
                f.write(str(each_info) + "@#$%")
                # break
            # break
            time.sleep(random.randint(2, 4))
