from appium import webdriver
import time
from lxml import etree
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC

PLATFROM = "Android"
DEVIE_NAME = "127.0.0.1:62001"
APP_PACKAGE = "com.tencent.mm"
APP_ACTIVITY = ".ui.LauncherUI"
DEIVER_SERVER = "http://localhost:4723/wd/hub"
TIMROUT = 10  # 单位秒

FLICK_START_X = 300
FLICK_START_Y = 300
FLICK_DISTANCE = 700

class WX(object):
    def __init__(self):
        """
        初始化操作
        """
        # 驱动配置操作
        self.desired_caps = {
            "platformName": PLATFROM,
            "deviceName": DEVIE_NAME,
            "appPackage": APP_PACKAGE,
            "appActivity": APP_ACTIVITY,
            "noReset": True,
            "unicodeKeyboard": True,
            "resetKeyboard": True
        }
        self.desired_caps["platformVersion"] = '5.1.1'
        self.driver = webdriver.Remote(DEIVER_SERVER, self.desired_caps)
        self.wait = WebDriverWait(self.driver, TIMROUT)

    def touch_tap(self, x, y, duration=1):  # 点击坐标  ,x1,x2,y1,y2,duration
        '''
        method explain:点击坐标
        parameter explain：【x,y】坐标值,【duration】:给的值决定了点击的速度
        Usage:
            device.touch_coordinate(277,431)      #277.431为点击某个元素的x与y值
        '''
        screen_width = self.driver.get_window_size()['width']  # 获取当前屏幕的宽
        screen_height = self.driver.get_window_size()['height']  # 获取当前屏幕的高
        a = (float(x) / screen_width) * screen_width
        x1 = int(a)
        b = (float(y) / screen_height) * screen_height
        y1 = int(b)
        self.driver.tap([(x1, y1), (x1, y1)], duration)

    def enter(self, name, item_num):
        tab = self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@text="通讯录"]')))
        tab.click()
        # 点击公众号
        self.wait.until(EC.presence_of_element_located((By.XPATH, '//*[@text="公众号"]'))).click()
        for i in range(50):
            # 因为只能点击当前页面的标签，所以需要循环向下滑动，找到需要点击的标签，在进行点击
            # 滑动查找需要爬取的公众号，并点击进入这个公众号
            tab_list = self.wait.until(
                EC.presence_of_all_elements_located((By.XPATH, """//*[@resource-id="com.tencent.mm:id/a6e"]""")))
            for tab in tab_list:
                name1 = tab.get_attribute("text")
                if name == name1:
                    tab.click()
                    # 点击右上角进历史页面
                    tab = self.wait.until(EC.presence_of_element_located(
                        (By.ID, "com.tencent.mm:id/j1")))
                    tab.click()
                    tab = self.wait.until(EC.presence_of_all_elements_located((By.XPATH, """//*[@resource-id="com.tencent.mm:id/axy"]""")))[item_num]
                    tab.click()
                    time.sleep(12)
                    return
            self.driver.swipe(FLICK_START_X, FLICK_START_Y + FLICK_DISTANCE, FLICK_START_X, FLICK_START_Y, 1000)
            time.sleep(1)

if __name__ == '__main__':
    """
    1.需要事先将所有需要爬取的公众号进行关注
    2.在进行爬取的时候 ，不要开chrome://inspect/#devices 这个页面，好像是占用chromedriver,造成程序异常
    3.这里对于爬取的过程，其实可以使用 requests 库来进行请求完成 ，只是现在对于每一个加密参数的生成不熟，
    后期进行修改，可以不使用手机完成内容的获取
    """
    wx = WX()
    wx.enter(name="交通银行私人银行")