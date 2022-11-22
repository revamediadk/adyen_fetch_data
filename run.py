import json
import requests

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from time import sleep
from fake_useragent import UserAgent
from selenium.webdriver.common.keys import Keys
import datetime as dt
import pandas as pd
from io import StringIO


def login_selenium(user_agent):
    cred = {
        'username': 'admin',
        'account': 'Rentola',
        'password': 'xvf.wpr3vef*FHC2kvu',
    }
    chrome_options = Options()
    chrome_options.add_argument("start-maximized")
    chrome_options.add_argument("disable-infobars")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--nogpu")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument('--ignore-ssl-errors=yes')
    chrome_options.add_argument('--ignore-certificate-errors')
    chrome_options.add_argument("--enable-javascript")
    chrome_options.add_argument("--window-size=1280,1280")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation"])
    chrome_options.add_experimental_option('useAutomationExtension', False)
    chrome_options.add_argument(
        '--disable-blink-features=AutomationControlled')
    chrome_options.add_argument(f'user-agent={user_agent}')
    url = 'https://ca-live.adyen.com/ca/ca/login.shtml'
    driver = webdriver.Chrome(
        executable_path='chromedriver/stable/chromedriver', options=chrome_options)
    driver.get(url)

    sleep(7)
    username = driver.find_element(by=By.NAME, value='userName')
    account = driver.find_element(by=By.NAME, value='account')
    password = driver.find_element(by=By.NAME, value='password')
    next = driver.find_element(
        by=By.XPATH, value='/html/body/div/div[1]/div/div[2]/form/footer/div/button')
    username.send_keys(cred['username'])
    next.send_keys(Keys.ENTER)
    sleep(0.5)
    account.send_keys(cred['account'])
    password.send_keys(cred['password'])
    login = driver.find_element(
        by=By.XPATH, value='/html/body/div/div[1]/div/div[2]/form/footer/div/button[1]')
    login.send_keys(Keys.ENTER)
    sleep(4)
    cookie = (driver.get_cookie(name='JSESSIONID'))
    return cookie


def login():

    headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
        "accept-language": "en-US,en;q=0.9",
        "sec-ch-ua": "\"Google Chrome\";v=\"107\", \"Chromium\";v=\"107\", \"Not=A?Brand\";v=\"24\"",
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": "\"Windows\"",
        "sec-fetch-dest": "document",
        "sec-fetch-mode": "navigate",
        "sec-fetch-site": "same-site",
        "sec-fetch-user": "?1",
        "upgrade-insecure-requests": "1"
    }
    s = requests.Session()
    x = s.post('https://ca-live.adyen.com/ca/ca/login.shtml',
               headers=headers, allow_redirects=True)
    cookie = x.headers['Set-cookie'].split(
        '; Path=/authn')[0].split('JSESSIONID=')[1]
    s.close()
    return cookie


def fetch_data(user_agent,start_date,end_date):
    user_cookie = login_selenium(user_agent)
    url = 'https://ca-live.adyen.com/ca/ca/ui-api/payments/v1/S3B-V325FVXdVUnM4L2JuVXNzQA/payments:download'
    s = requests.Session()
    start_date_str = start_date.strftime('%Y-%m-%dT%H:%M:%S')
    end_date_str = end_date.strftime('%Y-%m-%dT%H:%M:%S')

    headers = {
        'Accept': 'application/json, text/plain, */*',
        'Connection': 'keep-alive',
        "cookie": f"activeAccount=Company.Rentola; JSESSIONID={user_cookie['value']}",
        'Host': 'ca-live.adyen.com',
        'Origin': 'https://ca-live.adyen.com',
        'User-Agent': user_agent
    }
    payload = {"filter":{"datePicker":{"startDate":f"{start_date_str}.000Z","endDate":f"{end_date_str}.000Z","timeSpan":"last24hours"},"status":["Refused"],"query":"","orderBy":"date","orderDirection":"desc"},"visibleColumns":["pspReference","merchantReference","account","date","amount","method","status","fraudScore"]}
    r = s.post(url, headers=headers, json=(payload))
    if r.status_code == 200:
        s.close()
        r.close()
        return r.text
    else:
        raise Exception(f"data has not been fetched. status code {r.status_code}")
    

def post_data(csv):
    df = pd.read_csv(StringIO(csv))
    url = 'https://fbadmin:adminfb@godzilla.rentola.com/api/v1/adyen_fetch_data'
    for index, row in df.iterrows():
        s = requests.Session()
        payload = {
            'merchant_reference': row['Merchant Reference'],
            'account':row['Account'],
            'psp_reference':row['PSP Reference'],
            'creation_date':row['Creation Date'],
            'timezone':row['TimeZone'],
            'value':row['Value'],
            'currency': row['Currency'],
            'payment_method': row['Payment Method'],
            'status': row['Status']
        }
        r = s.post(url, json=(payload))
        
        

if __name__ == "__main__":
    now = dt.datetime.now()
    start_date = now - dt.timedelta(days=1)
    end_date = now
    ua = UserAgent()
    user_agent = ua.random
    csv = fetch_data(user_agent,start_date,end_date)
    post_data(csv)
