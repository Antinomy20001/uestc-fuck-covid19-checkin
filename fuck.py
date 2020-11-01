from http.cookies import SimpleCookie
import datetime
import random
import aiohttp
import time

headers = {'Host': 'eportal.uestc.edu.cn',
           'Connection': 'keep-alive',
           'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36',
           'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
           'Referer': 'http://eportal.uestc.edu.cn/new/index.html',
           'Accept-Encoding': 'gzip, deflate',
           'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
           'Cookie': None}


def update_cookie(response_headers, cookie):
    new_cookie = SimpleCookie()
    if 'Set-Cookie' not in response_headers:
        return cookie.output(header='', sep=';')[1:]
    new_cookie.load(response_headers['Set-Cookie'])
    cookie.update(new_cookie)
    return cookie.output(header='', sep=';')[1:]


def convert_headers(string):
    string = [i.strip() for i in string.split('\n') if len(i.strip()) > 0]
    string = map(lambda x: x.split('; '), string)
    return dict(string)


async def get_userid(origin_index_cookie):
    result = False
    async with aiohttp.ClientSession() as session:
        cookie = SimpleCookie()
        cookie.load(origin_index_cookie)
        headers['Cookie'] = cookie.output(header='', sep=';')[1:]

        async with session.get(f'http://eportal.uestc.edu.cn/jsonp/userDesktopInfo.json?type=&_={int(time.time() * 1000)}', headers=headers, allow_redirects=False) as response:
            response_json = await response.json()
            result = response_json['userId']

    return result


async def daily_fuck_checkin(session, origin_index_cookie):
    cookie = SimpleCookie()
    cookie.load(origin_index_cookie)
    headers['Cookie'] = cookie.output(header='', sep=';')[1:]
    results = []
    try:
        userid = await get_userid(origin_index_cookie)
    except Exception as e:
        print(str(e))                      
        return False

    data = {
        'USER_ID': userid,
        'pageSize': '1',
        'pageNumber': '1',
    }
    results.append(userid)

    async with session.get(url='http://eportal.uestc.edu.cn/appShow?appId=5807167997450437', headers=headers, allow_redirects=False) as response:
        headers['Cookie'] = update_cookie(response.headers, cookie)
        url = response.headers['Location']

    async with session.get(url=url, allow_redirects=False, headers=headers) as response:
        headers['Cookie'] = update_cookie(response.headers, cookie)

    async with session.post(url='http://eportal.uestc.edu.cn/jkdkapp/sys/lwReportEpidemicStu/modules/tempReport/T_REPORT_TEMPERATURE_YJS_QUERY.do', headers=headers, data=data) as temperature_response:
        temperature_response_json = await temperature_response.json()
        last_report_date = temperature_response_json['datas']['T_REPORT_TEMPERATURE_YJS_QUERY']['rows'][0]['NEED_DATE']
        last_report_date = datetime.datetime.strptime(last_report_date, "%Y-%m-%d")

    async with session.post(url='http://eportal.uestc.edu.cn/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/getMyTodayReportWid.do', headers=headers, data=data) as response:
        data = await response.json()

    data = data['datas']['getMyTodayReportWid']['rows'][0]

    now = datetime.datetime.now()
    last_daily_date = datetime.datetime.strptime(data['CZRQ'], "%Y-%m-%d %H:%M:%S")

    data["PERSON_TYPE"] = "001"
    data["LOCATION_PROVINCE_CODE"] = "510000"
    data["LOCATION_CITY_CODE"] = "510100"
    data["LOCATION_COUNTY_CODE"] = "510117"
    data["LOCATION_DETAIL"] = "西源大道2006号电子科技大学清水河校区"
    data["HEALTH_STATUS_CODE"] = "001"
    data["HEALTH_UNSUAL_CODE"] = ''
    data["IS_HOT"] = "0"
    data["IS_IN_HB"] = "0"
    data["IS_HB_BACK"] = "0"
    data["IS_DEFINITE"] = "0"
    data["IS_QUARANTINE"] = "0"
    data["IS_KEEP"] = "0"
    data["TEMPERATURE"] = ''
    data["IS_SEE_DOCTOR"] = "NO"
    data["IS_IN_SCHOOL"] = "1"
    data["MEMBER_HEALTH_STATUS_CODE"] = "001"
    data["MEMBER_HEALTH_UNSUAL_CODE"] = ''
    data["REMARK"] = ''
    data["CREATED_AT"] = now.strftime("%Y-%m-%d %H:%M:%S")
    data["NEED_CHECKIN_DATE"] = now.strftime("%Y-%m-%d")
    data["DEPT_CODE"] = "1008"
    data["CZRQ"] = now.strftime("%Y-%m-%d %H:%M:%S")
    data["PERSON_TYPE_DISPLAY"] = "留校"
    data["LOCATION_PROVINCE_CODE_DISPLAY"] = "四川省"
    data["LOCATION_CITY_CODE_DISPLAY"] = "成都市"
    data["LOCATION_COUNTY_CODE_DISPLAY"] = "郫都区"
    data["HEALTH_STATUS_CODE_DISPLAY"] = "正常"
    data["HEALTH_UNSUAL_CODE_DISPLAY"] = ""
    data["IS_HOT_DISPLAY"] = "否"
    data["IS_IN_HB_DISPLAY"] = "否"
    data["IS_HB_BACK_DISPLAY"] = "否"
    data["IS_DEFINITE_DISPLAY"] = "否"
    data["IS_QUARANTINE_DISPLAY"] = "否"
    data["IS_KEEP_DISPLAY"] = "否"
    data["IS_SEE_DOCTOR_DISPLAY"] = "否"
    data["IS_IN_SCHOOL_DISPLAY"] = "是"
    data["MEMBER_HEALTH_STATUS_CODE_DISPLAY"] = "正常"
    data["MEMBER_HEALTH_UNSUAL_CODE_DISPLAY"] = ""

    if now.day != last_daily_date.day or now - last_daily_date > datetime.timedelta(days=1):
        async with session.post(url='http://eportal.uestc.edu.cn/jkdkapp/sys/lwReportEpidemicStu/modules/dailyReport/T_REPORT_EPIDEMIC_CHECKIN_YJS_SAVE.do', headers=headers, data=data) as response:
            response_json = await response.json()
            results.append(response_json)
    else:
        results.append(f'{userid} Daily Report Completed')

    if now.day != last_report_date.day or now - last_report_date > datetime.timedelta(days=1):
        for i, period in enumerate(['早上', '中午', '晚上']):
            data = temperature_response_json['datas']['T_REPORT_TEMPERATURE_YJS_QUERY']['rows'][0]

            data['WID'] = ''
            data['CZRQ'] = now.strftime("%Y-%m-%d %H:%M:%S")
            data['NEED_DATE'] = now.strftime("%Y-%m-%d")
            data['DAY_TIME_DISPLAY'] = period
            data['DAY_TIME'] = str(i + 1)
            data['TEMPERATURE'] = random.choice([f'36.{_}' for _ in range(1, 10)])
            data['CREATED_AT'] = now.strftime("%Y-%m-%d %H:%M:%S")

            async with session.post(url='http://eportal.uestc.edu.cn/jkdkapp/sys/lwReportEpidemicStu/modules/tempReport/T_REPORT_TEMPERATURE_YJS_SAVE.do', headers=headers, data=data) as response:
                response_json = await response.json()
            results.append(response_json)
    else:
        results.append(f'{userid} Temperature Report Completed')
    return results


async def work(userid, origin_index_cookie):
    async with aiohttp.ClientSession() as session:
        result = False
        try:
            result = await daily_fuck_checkin(
                session=session,
                origin_index_cookie=origin_index_cookie
            )
        except Exception as e:
            print(str(e))
            pass
        return (userid, result)
