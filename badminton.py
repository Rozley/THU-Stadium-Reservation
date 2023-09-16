from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import UnexpectedAlertPresentException, NoSuchElementException
import time
import json
from logger import logger

import math
# 登陆页
login_url = "https://50.tsinghua.edu.cn/dl.jsp"
# 抢票目标页
target_url = "https://50.tsinghua.edu.cn/gymbook/gymBookAction.do?ms=viewGymBook"
# 账户信息json
account_path = "./accounts.json"
# 场馆运动项目id
gym_id_path = "./gym_ids.json"
# 是否需要刷新等待
need_refresh = True
# 加载策略改为none，禁用alert
options = Options()
# options.add_argument('--disable-alerts')
options.page_load_strategy = 'none'
# 初始化日志
logger = logger()


class Badminton:
    def __init__(self):

        # 默认Chrome浏览器
        self.driver = webdriver.Chrome(options=options)
        # 用户账户信息
        self.account_info = {}
        # 隐式等待，若组件未出现则进入等待，等待期间将持续寻找组件
        self.driver.implicitly_wait(1)

    def parse_account(self):
        try:
            with open(account_path, 'r', encoding='utf_8') as f:
                reader = json.load(f)
                self.account_info = reader['acc0']
        except BaseException.Exception.OSError.FileNotFoundError as e:
            logger.info('[信息]: 用户信息解析失败.\n' + 
                        '[失败原因]: accounts.json文件不存在.\n')
        # 解析完成
        logger.info('[信息]: 用户' + self.account_info['user_id'] + '信息解析成功.\n')
        return

    def parse_gym_id(self):
        with open(gym_id_path, 'r', encoding='utf_8') as f:
            reader = json.load(f)
            gym_ids = reader['gym_ids']
            for task in self.account_info['tasks']:
                task['gym_id'] = gym_ids[task['gym']+task['sport']][0]
                task['sport_id'] = gym_ids[task['gym']+task['sport']][1]
                logger.info('[信息]: ' + task['gym'] + task['sport'] + '信息加载成功.\n')
        # 解析完成
        logger.info('[信息]: 全部场馆运动信息加载成功.\n')
        return

    def login(self):
        try:
            # 打开登录页
            self.driver.get("https://50.tsinghua.edu.cn/dl.jsp")
            username = self.driver.find_element(By.ID, "login_username")
            password = self.driver.find_element(By.ID, "login_password")
            username.send_keys(self.account_info['user_id'])
            password.send_keys(self.account_info['user_password'])
            login_btn = self.driver.find_element(By.XPATH, "//input[@alt='Login']")
            login_btn.click()
            # 打开目标页面
            self.driver.find_element(By.XPATH, '//*[@id="nav-main"]/ul/li[3]/a').click()
            self.driver.find_element(By.XPATH, '//*[@id="bookInfo"]/div/div[2]/a').click()
            # 登录成功
            logger.info('[信息]: 用户' + self.account_info['user_id'] + '登录成功.\n')
        except NoSuchElementException as e:
            # 登录失败
            logger.info('[信息]: 用户' + self.account_info['user_id'] + '登录失败.\n' + 
                        '[失败原因]: 用户名或密码错误.\n')
        return

    def choose_field(self):
        WebDriverWait(self.driver, 10, 1).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='同意']")))
        agree_btn = self.driver.find_element(By.XPATH, "//*[text()='同意']")
        agree_btn.click()

        for task in self.account_info['tasks']:
            for i in range(len(task['time'])):
                self.driver.get(target_url +
                                "&gymnasium_id=" + task['gym_id'] +
                                "&item_id=" + task['sport_id'] +
                                "&time_date=" + task['date'] +
                                "&userType=")

                while need_refresh:
                    try:
                        self.driver.implicitly_wait(0)
                        iframe = self.driver.find_element(By.ID, "overlayView")
                        self.driver.implicitly_wait(1)
                        break
                    except Exception as e:
                        self.driver.refresh()
                        time.sleep(0.2)

                iframe = self.driver.find_element(By.ID, "overlayView")
                self.driver.switch_to.frame(iframe)

                non_ava_fields = self.driver.find_elements(By.XPATH, "//td[@time_session=\'" + task['time'][i] +
                                                       "\' and string-length(@style)>0]")
                all_fields = self.driver.find_elements(By.XPATH, "//td[@time_session=\'" + task['time'][i] + "\']")
                ava_fields = list(set(all_fields).difference(set(non_ava_fields)))
                if len(ava_fields) == 0:
                    logger.info('[任务]: ' + task['gym'] + task['sport'] + task['time'][i] + '失败!\n' +
                                '[失败原因]: 没有找到合适场次.\n')
                    continue
                else:
                    try:
                        # 选择一个被选中几率较小的场
                        idx = round(len(ava_fields)/4)
                        ava_fields[idx].click()

                        self.driver.switch_to.default_content()

                        odd_btn = self.driver.find_element(By.XPATH, "//span[@onclick='saveOdder()']")
                        odd_btn.click()

                        WebDriverWait(self.driver, 100, 0.5).until(EC.alert_is_present())
                        alert = self.driver.switch_to.alert
                        logger.info('[任务]: ' + task['gym'] + task['sport'] + task['time'][i] + '失败!\n' +
                                    '[失败原因]: ' + alert.text + '\n')
                        alert.accept()
                        self.driver.switch_to.default_content()
                        continue

                    except UnexpectedAlertPresentException as e:
                        continue


    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    # initialize badminton class
    bm = Badminton()
    try:
        # 加载账户信息
        bm.parse_account()
        # 加载体育场馆信息
        bm.parse_gym_id()
        # 登录
        bm.login()
        # 选择场次
        bm.choose_field()

    except Exception as e:
        print(e)
        bm.finish()
