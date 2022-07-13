#!/usr/bin/python
'''
Author       : samiya
LastEditors  : samiya
Description  : 自动更新各 TestFlight 公共链接当前的状态并更新文档
FilePath     : /AutoFollowTestflight/scripts/update_status.py
'''

import sqlite3
import asyncio
import aiohttp
import re, os, sys, datetime, random

BASE_URL = "https://testflight.apple.com/"

TABLE_MAP = {
    "macos": "./data/macos.md",
    "ios": "./data/ios.md",
    "ios_game": "./data/ios_game.md",
    "chinese": "./data/chinese.md",
    "signup": "./data/signup.md"
}
README_TEMPLATE_FILE = "./data/README.template"
TODAY = datetime.datetime.utcnow().date().strftime("%Y-%m-%d")

FULL_PATTERN = re.compile(r"版本的测试员已满|This beta is full")
NO_PATTERN = re.compile(r"版本目前不接受任何新测试员|This beta isn't accepting any new testers right now")

def get_old_status(table):
    conn = sqlite3.connect('../db/sqlite3.db')
    cur = conn.cursor()
    res = cur.execute(f"SELECT testflight_link, status FROM {table};")
    res_dict = {}
    for row in res:
        res_dict[row[0]] = row[1]
    conn.close()
    return res_dict

def update_status(table, change_list):
    conn = sqlite3.connect('../db/sqlite3.db')
    cur = conn.cursor()
    for update in change_list:
        cur.execute(f"UPDATE {table} SET status = '{update[1]}', last_modify = '{TODAY}' WHERE testflight_link = '{update[0]}';")
    conn.commit()
    total = conn.total_changes
    conn.close()
    return total

def renew_doc(data_file, table):
    # header
    markdown = []
    with open(data_file, 'r') as f:
        lines = f.readlines()
        for line in lines:
            columns = [ column.strip() for column in line.split("|") ]
            markdown.append(line)
            if len(columns) > 2 and re.match(r"^:?-+:?$", columns[1]):
                break
    # 
    conn = sqlite3.connect('../db/sqlite3.db')
    cur = conn.cursor()
    res = cur.execute(f"""SELECT app_name, testflight_link, status, last_modify FROM {table} ORDER BY 
        CASE status
            WHEN 'Y' THEN 0
            WHEN 'F' THEN 1
            WHEN 'N' THEN 2
            WHEN 'D' THEN 3
        END;""")
    for row in res:
        app_name, testflight_link, status, last_modify = row
        testflight_link = f"[https://testflight.apple.com/join/{testflight_link}](https://testflight.apple.com/join/{testflight_link})"
        markdown.append(f"| {app_name} | {testflight_link} | {status} | {last_modify} |\n")
    conn.close()
    # 
    with open(data_file, 'w') as f:
        lines = f.writelines(markdown)

def renew_readme():
    template = ""
    with open(README_TEMPLATE_FILE, 'r') as f:
        template = f.read()
    macos = ""
    with open(TABLE_MAP["macos"], 'r') as f:
        macos = f.read()
    ios = ""
    with open(TABLE_MAP["ios"], 'r') as f:
        ios = f.read()
    ios_game = ""
    with open(TABLE_MAP["ios_game"], 'r') as f:
        ios_game = f.read()
    chinese = ""
    with open(TABLE_MAP["chinese"], 'r') as f:
        chinese = f.read()
    signup = ""
    with open(TABLE_MAP["signup"], 'r') as f:
        signup = f.read()
    readme = template.format(macos=macos, ios=ios, ios_game=ios_game, chinese=chinese, signup=signup)
    with open("../README.md", 'w') as f:
        f.write(readme)

async def check_status(session, key, retry=10):
    status = 'N'
    for i in range(retry):
        try:
            async with session.get(f'/join/{key}') as resp:
                resp.raise_for_status()
                resp_html = await resp.text()
                if NO_PATTERN.search(resp_html) is not None:
                    status = 'N'
                elif FULL_PATTERN.search(resp_html) is not None:
                    status = 'F'
                else:
                    status = 'Y'
                return (key, status)
        except aiohttp.ClientResponseError as e:
            if resp.status == 404:
                return (key, 'D')
            rand = round(random.random(), 3)
            print(f"[warn] {e}, wait {i*(rand+1)+1} s.")
            await asyncio.sleep(i*(rand+1)+1)

    return (key, status)

async def main():
    # 稳妥起见限制同时 5 个同 host 的请求
    conn = aiohttp.TCPConnector(limit=10, limit_per_host=3)
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/53.0.2357.130 Safari/537.36 qblink wegame.exe QBCore/3.70.66.400 QQBrowser/9.0.2524.400"
    }
    async with aiohttp.ClientSession(BASE_URL, connector=conn, headers=headers) as session:
        for table in TABLE_MAP:
            if table == "signup": # 数据库没有此表
                continue
            old_status = get_old_status(table)
            link_keys = old_status.keys()
            coroutines_list = []
            for key in link_keys:
                coroutines_list.append(check_status(session, key))
            result = await asyncio.gather(*coroutines_list) # 正常情况下返回列表的顺序与传入顺序相同，稳妥起见&方便后续处理还是在 check_status() 返回值加个 key
            change_list = []
            for row in result:
                if old_status[row[0]] != row[1]:
                    change_list.append(row)

            changed = update_status(table, change_list)
            print(f"[info] Changed {changed} rows in {table}.")
            renew_doc(TABLE_MAP[table], table)

if __name__ == "__main__":
    os.chdir(sys.path[0])
    
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
    renew_readme()

    print(f"[info] All Done!")
