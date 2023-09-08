from appium import webdriver
import time,xlrd,xlwt,logging,threading
from datetime import datetime
import subprocess,os
from appium.webdriver.common.touch_action import TouchAction         #用于模拟触摸操作的类。它提供了各种方法来执行单个或多个触摸操作，例如点击、滑动、长按等。
from selenium.common import NoSuchElementException, WebDriverException


class Myraise(Exception):    #自定义的异常
    pass




class MobileTest:


    def __init__(self):
        self.driver = ''
        self.i = 0
        self.scode = ''
        self.sname = ''
        self.spws = ''
        self.acc = ['admin,1234567','van,123456','pda1,654321']         #客户账号密码

        self.desired = {                                       # 定义字典 配置链接设备信息
            "automationName": "Appium",
            "platformName": "Android",
            "platformVersion": "9",
            "deviceName": "127.0.0.1:62025",
            "udid": "127.0.0.1:62025",
            "appPackage": "com.greenstar.gsf",
            "appActivity": "io.dcloud.PandoraEntryActivity",
            "noReset": True
        }
        #"deviceName": "127.0.0.1:62001",
        #"udid": "127.0.0.1:62001"

        # APP账号密码定位元素
        self.account = '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/android.widget.FrameLayout/' \
                       'android.widget.FrameLayout/android.widget.FrameLayout/android.view.ViewGroup/android.widget.FrameLayout/' \
                       'android.widget.LinearLayout/android.webkit.WebView/android.webkit.WebView/android.view.View[3]/android.view.View/' \
                       'android.widget.EditText'
        self.password = '/hierarchy/android.widget.FrameLayout/android.widget.LinearLayout/' \
                        'android.widget.FrameLayout/android.widget.FrameLayout/android.widget.FrameLayout/' \
                        'android.view.ViewGroup/android.widget.FrameLayout/android.widget.LinearLayout/' \
                        'android.webkit.WebView/android.webkit.WebView/android.view.View[5]/' \
                        'android.view.View/android.widget.EditText'
        self.fail_acc = []
        self.sus_acc = []
        self.filename = ''




    def login(self, time):
        if int(time) == 0 :      #time为0则为死循环
            while True:
                self.i += 1
                for us in self.acc:  # 循环获取客户信息
                    try:
                        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub',self.desired)  # 把配置的字典作为请求参数发给appium服务器
                        self.wait(1)
                        self.get_log('正在登录客户：' + us.split(',')[0])

                        if 'Update Version' in self.get_page():      # 判断是否需要更新，处于则取消更新
                            self.if_update()

                        if 'Remember me?' in self.get_page():  # 判断是否处于登录页面，处于则直接登录
                            self.get_log('用户：' + us.split(',')[0] + '登录中')
                            self.is_loging(us.split(',')[0], us.split(',')[1])
                            self.wait()

                        else:  # 不在登录页面则先退出账户再登录
                            self.if_log()
                            self.wait()
                            self.get_log('用户：' + us.split(',')[0] + '登录中')
                            self.is_loging(us.split(',')[0], us.split(',')[1])
                            self.wait()
                        self.page_source = self.driver.page_source  # 获取页面内容
                        if 'Skip' in self.page_source:  # 判断是否处于选择线路页面，处于则点击跳过按钮再退出账户
                            self.wait(1)
                            self.if_skip()
                            self.wait()
                            self.is_exit()
                            self.wait()
                        else:  # 否则直接退出账号
                            self.is_exit()
                            self.wait()
                        self.wait(1)
                        self.get_log('账户' + us.split(',')[0] + '登录成功')
                        self.app_quit()  # 关闭APP服务
                        self.wait(1)
                    except NoSuchElementException as nee:    #捕获定位错误信息
                        err_msg3 = str(nee)
                        self.get_log('找不到定位元素，错误信息：%s'%(err_msg3.split(';')[0]))
                        self.fail_acc.append(us.split(',')[0])
                        self.save_screen(self.get_local_time() + '.png')
                        self.app_quit()
                        continue
                    except WebDriverException as wde:
                        err_msg5 = str(wde)
                        self.get_log('上个进程未关闭，driver启动失败，错误信息：%s' % (err_msg5.split('.')[1]))
                        self.fail_acc.append(us.split(',')[0])
                        self.save_screen(self.get_local_time() + '.png')
                        self.app_quit()
                        continue
                    except Exception as esc:     #捕获其他错误信息
                        err_msg4 = str(esc)
                        self.get_log('未知错误：%s'%(err_msg4.split(':')[1]))
                        self.fail_acc.append(us.split(',')[0])
                        self.save_screen(self.get_local_time() + '.png')
                        self.app_quit()
                        continue
                    else:
                        self.sus_acc.append(us.split(',')[0])

                self.sus_acc = [x for i, x in enumerate(self.sus_acc) if x not in self.sus_acc[:i]]
                self.fail_acc = [x for i, x in enumerate(self.fail_acc) if x not in self.fail_acc[:i]]
                self.get_log('全部客户第' + str(self.i) + '次循环登录完成' + '，成功客户：%s，失败客户：%s'%(self.sus_acc ,self.fail_acc))
                self.app_quit()
                self.sus_acc.clear()
                self.fail_acc.clear()
                self.wait()
        else:
            for i in range(time):         #time不为0则普通循环
                self.i += 1
                for us in self.acc:              #循环获取客户信息
                    try:
                        self.driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', self.desired)           # 把配置的字典作为请求参数发给appium服务器
                        self.wait()
                        self.get_log('正在登录客户：' + us.split(',')[0])

                        if 'Update Version' in self.get_page():                    #检查更新
                            self.if_update()

                        if 'Remember me?' in self.get_page() :                        #判断是否处于登录页面，处于则直接登录
                            self.get_log('用户：' + us.split(',')[0] + '登录中')
                            self.is_loging(us.split(',')[0], us.split(',')[1])
                            self.wait()

                        else:                       #不在登录页面则先退出账户再登录
                            self.if_log()
                            self.wait()
                            self.get_log('用户：' + us.split(',')[0] + '登录中')
                            self.is_loging(us.split(',')[0], us.split(',')[1])
                            self.wait()

                        self.page_source = self.driver.page_source            #获取页面内容
                        if 'Skip' in self.page_source:                     #判断是否处于选择线路页面，处于则点击跳过按钮再退出账户
                            self.wait(1)
                            self.if_skip()
                            self.wait()
                            self.is_exit()
                            self.wait()
                        else:                                           #否则直接退出账号
                            self.wait()
                            self.is_exit()
                            self.wait()
                        self.wait(1)
                        self.get_log('账户' + us.split(',')[0] + '登录成功')

                        self.app_quit()                              #关闭APP服务
                        self.wait(1)
                    except NoSuchElementException as ese:               #捕获定位错误信息
                        err_msg1 = str(ese)
                        self.get_log('发生错误，错误信息：%s'%(err_msg1.split(';')[0]))
                        self.fail_acc.append(us.split(',')[0])
                        self.save_screen(self.get_local_time() + '.png')
                        # self.wait(3)
                        self.app_quit()
                        continue
                    except WebDriverException as wde:
                        err_msg5 = str(wde)
                        self.get_log('上个进程未关闭，driver启动失败，错误信息：%s' % (err_msg5.split('.')[1]))
                        self.save_screen(self.get_local_time() + '.png')
                        self.fail_acc.append(us.split(',')[0])
                        self.app_quit()
                        continue
                    except Exception as esc:                    #捕获其他错误信息
                        err_msg2 = str(esc)
                        self.get_log('未知错误：%s' % (err_msg2.split(':')[1]))
                        self.fail_acc.append(us.split(',')[0])
                        self.save_screen(self.get_local_time() + '.png')
                        self.app_quit()
                        continue
                    else:
                        self.sus_acc.append(us.split(',')[0])

                self.sus_acc = [x for i, x in enumerate(self.sus_acc) if x not in self.sus_acc[:i]]          #列表排序
                self.fail_acc = [x for i, x in enumerate(self.fail_acc) if x not in self.fail_acc[:i]]        #列表排序
                self.get_log('全部客户第' + str(self.i) + '次循环登录完成' + '，成功客户：%s，失败客户：%s'%(self.sus_acc ,self.fail_acc))
                self.sus_acc.clear()         #清空列表
                self.fail_acc.clear()        #清空列表
                self.wait()
            self.get_log('循环结束，Finish')
            # print(self.format_time + '全部客户第' + str(i+1) +'次循环登录完成' )



    def wait(self,times = 2):
        time.sleep(times)



    def if_log(self):           #退出操作
        self.driver.find_element('xpath', "//*[@text='Me']").click()
        self.wait()
        self.driver.find_element("xpath", "//*[@text='Exit']").click()



    def if_skip(self):          #跳过
        self.driver.find_element('xpath', "//*[@text='Skip']").click()



    def app_quit(self):          #关闭APP服务
        self.driver.quit()


    def is_loging(self,username,password):       #登录操作
        self.driver.find_element('xpath', self.account).send_keys(username)
        self.driver.find_element('xpath', self.password).send_keys(password)
        self.wait()
        self.driver.find_element('xpath', "//*[@text='Sign In']").click()


    def is_exit(self):
        self.driver.find_element('xpath', "//*[@text='Me']").click()
        self.wait(3)
        self.driver.find_element("xpath", "//*[@text='Exit']").click()



    def move_to(self):            #滑动
        # self.touch_action = TouchAction(self.driver)
        # start_el = self.driver.find_element("xpath", "//*[@text='Collect Product Barcodes']")
        # end_el = self.driver.find_element("xpath", "//*[@text='Picking']")
        # time.sleep(3)
        # self.touch_action.press(start_el).move_to(end_el).release().perform()
        pass



    def long_press(self):           #长按
        # self.touch_action = TouchAction(self.driver)
        # el = self.driver.find_element('xpath','//android.widget.TextView[@content-desc="为33333"]')
        # self.touch_action.long_press(el).perform()
        pass


    def local_time(self):             #获取当前时间
        self.current_time = datetime.now()
        self.format_time = self.current_time.strftime("%Y-%m-%d %H:%M:%S")
        return self.format_time


    def if_update(self):      #取消更新
        self.driver.find_element('id', 'android:id/button1').click()
        self.wait()



    def get_page(self):            #获取页面内容
        return self.driver.page_source


    def get_log(self,msg):
        # 配置日志输出的格式
        logging.basicConfig(format='%(asctime)s - %(levelname)s - %(message)s',level=logging.INFO)

        # 创建一个FileHandler，指定日志文件的路径和文件名
        self.file_handler = logging.FileHandler('log.txt')

        # 设置FileHandler的日志级别和格式
        self.file_handler.setLevel(logging.INFO)
        self.file_handler.setFormatter(logging.Formatter('%(asctime)s - %(levelname)s - %(message)s'))


        # 将FileHandler添加到logger中
        self.logger = logging.getLogger()
        self.logger.addHandler(self.file_handler)

        # 打印日志
        self.logger.info(msg)

        #每次运行之前，移除handler
        self.logger.removeHandler(self.file_handler)



    def get_local_time(self):
        # 获取当前时间的datetime对象
        current_time = datetime.now()
        # 将datetime对象格式化为字符串表示形式
        #formatted_time = current_time.strftime("%Y-%m-%d %H:%M:%S")
        formatted_time = current_time.strftime("%Y%m%d%H%M%S")
        return formatted_time



    def save_screen(self,filename):
        self.driver.save_screenshot(filename)




if __name__ == '__main__':
    mt = MobileTest()
    # mt.login(2)
    t1 = threading.Thread(target=mt.login,args=(2,))
    t1.start()
    t1.join()





# for i in acc:
# 把配置的字典作为请求参数发给appium服务器
#     driver = webdriver.Remote('http://127.0.0.1:4723/wd/hub', desired)
#     time.sleep(5)
#     driver.find_element('xpath',account).send_keys(i)
#     driver.find_element('xpath',password).send_keys(psw)
#     time.sleep(3)
#     driver.find_element('xpath',"//*[@text='Sign In']").click()
#     time.sleep(3)
#     mess = driver.find_element('id','android:id/message')
#     print(mess.text)
#     page_source = driver.page_source
#     if mess.text in page_source:          #进入APP时如果是已登录状态，先退出登录
#         print('1')
        # time.sleep(3)
        # driver.find_element("xpath", "//*[@text='Exit']").click()
        # time.sleep(3)
    # else:
    #     print('2')
    # time.sleep(3)
    # driver.find_element('xpath',acount).send_keys(i)
    # driver.find_element('xpath',password).send_keys(psw)
    # time.sleep(3)
    # driver.find_element('xpath',"//*[@text='Sign In']").click()
    # time.sleep(3)
    # page_source = driver.page_source
    # print(page_source)
    # choose_line = driver.find_element("xpath","//*[@text='Skip']")
    # if 'Skip' in page_source: #如果登录时需要先选择线路才能进入APP，先跳过
    #     print('1')
    #     choose_line.click()
    #     time.sleep(3)
    # else:
    #     print('2')
    #     continue
    # driver.find_element('xpath',"//*[@text='Me']").click()
    # time.sleep(3)
    # driver.find_element("xpath","//*[@text='Exit']").click()
    # print(i + '登录正常')
    # driver.quit()














