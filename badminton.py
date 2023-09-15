from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import time
import json
import math
# 登陆页
login_url = "https://50.tsinghua.edu.cn/dl.jsp"
# 抢票目标页
target_url = "https://50.tsinghua.edu.cn/gymbook/gymBookAction.do?ms=viewGymBook"
# 账户信息json
account_path = "./accounts.json"
# 不同体育馆的id，前面是体育馆id，后面是羽毛球项目id
gym_ids = {
    "综合体育馆羽毛球": ["4797914", "4797899"],
    "综合体育馆篮球": ["4797914", "4797898"],
    "西体育馆羽毛球": ["4836273", "4836196"],
    "西体育馆台球": ["4836273", "14567218"],
    "西体育馆篮球": ["4836273", "19071481"],
    "气膜体育馆羽毛球": ["3998000", "4045681"],
    "气膜体育馆乒乓球": ["3998000", "4037036"],
}
# 是否需要刷新等待
need_refresh = True
options = Options()
options.add_argument('--disable-notifications')


class Badminton:
    def __init__(self):
        # 默认Chrome浏览器
        self.driver = webdriver.Chrome(options=options)
        # 用户账户信息
        self.account_info = {}
        # 隐式等待，若组件未出现则进入等待，等待期间将持续寻找组件
        self.driver.implicitly_wait(1)

    def parse_account(self):
        with open(account_path, 'r') as f:
            reader = json.load(f)
            self.account_info = reader['acc0']
            print(self.account_info)

    def login(self):
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
        for task in self.account_info['tasks']:
            WebDriverWait(self.driver, 10, 0.1).until(EC.element_to_be_clickable((By.XPATH, "//*[text()='同意']")))
            agree_btn = self.driver.find_element(By.XPATH, "//*[text()='同意']")
            agree_btn.click()
            self.driver.get(target_url +
                            "&gymnasium_id=" + gym_ids[task['gym']+task['sport']][0] +
                            "&item_id=" + gym_ids[task['gym']+task['sport']][1] +
                            "&time_date=" + task['date'] +
                            "&userType=")
            while need_refresh:
                try:
                    self.driver.implicitly_wait(0)
                    iframe = self.driver.find_element(By.ID, "overlayView")
                    self.driver.implicitly_wait(10)
                    break
                except Exception as e:
                    self.driver.refresh()
                    time.sleep(0.2)

            iframe = self.driver.find_element(By.ID, "overlayView")
            self.driver.switch_to.frame(iframe)

            for i in range(len(task['time'])):
                non_ava_fields = self.driver.find_elements(By.XPATH, "//td[@time_session=\'" + task['time'][i] +
                                                       "\' and string-length(@style)>0]")
                all_fields = self.driver.find_elements(By.XPATH, "//td[@time_session=\'" + task['time'][i] + "\']")
                ava_fields = list(set(all_fields).difference(set(non_ava_fields)))
                if len(ava_fields) == 0:
                    continue
                else:
                    # 选择一个被选中几率较小的场
                    idx = round(len(ava_fields)/4)
                    ava_fields[idx].click()

                    self.driver.switch_to.default_content()

                    odd_btn = self.driver.find_element(By.XPATH, "//span[@onclick='saveOdder()']")
                    odd_btn.click()

                    time.sleep(1000)

    def choose_field(self):
        self.parse_account()
        self.login()

    def finish(self):
        self.driver.quit()


if __name__ == '__main__':
    # initialize badminton class
    bm = Badminton()
    try:
        bm.choose_field()

    except Exception as e:
        print(e)
        bm.finish()