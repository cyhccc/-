import time
from io import BytesIO
import requests
from PIL import Image
from selenium import webdriver
from selenium.webdriver import ActionChains
import cv2 #opencv 读取格式是BGR
import matplotlib.pyplot as plt
import numpy as np

class crackxujc() :
     a=1
     def __init__(self,use,pwd):
         self.use=use
         self.pwd=pwd
         self.url='http://ijg.xujc.com'
         self.browser = webdriver.Chrome()


     def real_webdriver(self):
         pass

     def login(self):


         self.browser.get(self.url)
         time.sleep(0.5)
         button = self.browser.find_element_by_xpath("//button[text()='平台账号登录']")
         button.click()  # 点击初始按钮
         username = self.browser.find_element_by_xpath("//div[@class='account']/input")
         password = self.browser.find_element_by_xpath("//div[@class='password']/input")
         loginbtn = self.browser.find_element_by_xpath("//span[text()='登   录']")

         username.send_keys(self.use)
         password.send_keys(self.pwd)
         loginbtn.click()  # 点击登录按钮

     def get_img(self,browser):
         time.sleep(1)
         '''
         获取按钮图片
         '''
         image1 = browser.find_element_by_xpath("//div[@class='dx_captcha_basic_sub-slider']/img")
         img_url = image1.get_attribute('src')
         data = requests.get(img_url)

         with open("front.png", 'wb') as f:
             f.write(data.content)
         front = Image.open('front.png').convert("RGBA")
         front = front.resize((50, 50), Image.ANTIALIAS)
         front.save('front.png', "png")
         image2 = cv2.imread('front.png')
         w, h = image2.shape[:2]
         location1 = image1.location
         '''
         获取截图
         
         '''
         image = browser.find_element_by_xpath("//div[@id='dx_captcha_basic_bg_1']/canvas")
         location = image.location  # 获取图片(WebElement 对象)的位置
         size = image.size          # 获取图片(WebElement 对象)的大小
         top, bottom, left, right = location1['y'], location1['y'] + h, location1['x'] + w, location['x'] + size[
             'width']
         screenshot = browser.get_screenshot_as_png()  # 获取浏览器页面截图 数据类型以utf-8编码
         screenshot = Image.open(BytesIO(screenshot))  # 将utf-8编码转化为二进制，并以图片的方式打开
         captcha = screenshot.crop((left, top, right, bottom))  # 进行裁剪
         captcha.save("bg.png")  # 保存在ddd.png中

     def imagechange(self):

         front = cv2.imread("front.png", cv2.IMREAD_UNCHANGED)  # 以png格式打开

         w, h = front.shape[:2]
         for i in range(w):  # 将透明部分变为白色
             for j in range(h):
                 front[i, j][3] = 255


         front=cv2.cvtColor(front,6)

         ret, th2 = cv2.threshold(front, 5, 255, cv2.THRESH_BINARY_INV)  # 将front进行二值化处理
         # cv2.imshow('th2.png',th2)
         # cv2.waitKey(0)
         sobelx = cv2.Sobel(th2, cv2.CV_16S, 1, 0, ksize=1)  # 梯度处理
         sobelx = cv2.convertScaleAbs(sobelx)
         sobely = cv2.Sobel(th2, cv2.CV_16S, 0, 1, ksize=1)
         sobely = cv2.convertScaleAbs(sobely)
         sobelxy = cv2.addWeighted(sobelx, 0.5, sobely, 0.5, 0)

         # cv2.imshow('th2', sobely)
         # cv2.waitKey(0)

         th2 = cv2.Canny(sobelxy, 50, 100) #边缘检测

         # cv2.imshow('th2', th2)
         # cv2.waitKey(0)

         cv2.imwrite('th2.png', th2)

         img1 = cv2.imread("bg.png", cv2.IMREAD_GRAYSCALE)

         dstx = cv2.Sobel(img1, cv2.CV_16S, 1, 0, ksize=1)# 梯度处理
         dstxcmp = cv2.convertScaleAbs(dstx)
         dsty = cv2.Sobel(img1, cv2.CV_16S, 0, 1, ksize=1)
         dstycmp = cv2.convertScaleAbs(dsty)
         dstxy = cv2.addWeighted(dstxcmp, 0.5, dstycmp, 0.5, 0)
         #
         # cv2.imshow('th2', dstxy)
         # cv2.waitKey(0)
         dstxy = cv2.Canny(dstxy , 100, 200)  # Canny边缘检测
         # cv2.imshow('th2', dstxy)
         # cv2.waitKey(0)
         cv2.imwrite("th1.png",dstxy)
     def matchcmp(self):  #模板匹配
         bg = cv2.imread('th1.png')
         front = cv2.imread('th2.png')

         w, h = front.shape[:2]
         img2 = bg.copy()
         res = cv2.matchTemplate(bg, front, cv2.TM_CCOEFF_NORMED)
         min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
         top_left = max_loc
         bottom_right = (top_left[0] + w, top_left[1] + h)

         qqq = cv2.rectangle(img2, top_left, bottom_right, 255, 2)

         # cv2.imshow('qqq', qqq)
         # cv2.waitKey(0)

         print('匹配位置' + str(top_left[0]))
         return top_left[0] + w -5

     def get_track(self, distance):  #模拟滑动距离
         """
         根据偏移量获取移动轨迹
         :param distance: 偏移量
         :return: 移动轨迹
         """
         # 移动轨迹
         track = []
         # 当前位移
         current = 0
         # 减速阈值
         mid = distance * 4 / 5
         # 计算间隔
         t = 0.3
         # 初速度
         v = 0
         while current < distance:
             if current < mid:
                 # 加速度为正2
                 a = 2
             else:
                 # 加速度为负3
                 a = -3
             # 初速度v0
             v0 = v
             # 当前速度v = v0 + at
             v = v0 + a * t
             # 移动距离x = v0t + 1/2 * a * t^2
             move = v0 * t + 1 / 2 * a * t * t
             # 当前位移
             current += move
             # 加入轨迹
             track.append(round(move))
         print("位移" + str(current))
         return track
     def move_to_gap(self,track): #移动滑块
         drop = self.browser.find_element_by_xpath("//div[@class='dx_captcha_basic_slider-cover']")
         ActionChains(self.browser).click_and_hold(drop).perform()
         for x in track:
             ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=0).perform()
         time.sleep(0.5)
         ActionChains(self.browser).release().perform()

     def temp(self):  #登录后操作
        time.sleep(2)
        try:
         button = self.browser.find_element_by_xpath("//div[@class='grow_1 box_flex column justify_center']")
         button.click()
         time.sleep(1.3)
         self.browser.switch_to_window(self.browser.window_handles[1])
         button = self.browser.find_element_by_xpath("//div[@title='我的表单']")
         button.click()
         time.sleep(2)
         span0 = self.browser.find_element_by_xpath("//span[@title='未打卡']")
         span0.click()

         span1 = self.browser.find_element_by_xpath("//span[text()='37.3以下']")
         span1.click()

         span21=self.browser.find_element_by_xpath("//div[@id='select_1588863625331']//span[@title='否']")
         span21.click()

         span2 = self.browser.find_element_by_xpath("//li[@class='dropdown-items active']//span[text()='否']")
         span2.click()

         span3 = self.browser.find_element_by_xpath("//span[@class='form-save position-absolute']/i")
         span3.click()
         self.a=0
        except:
         print('异常')
         self.a=self.a+1

     def start(self):
         while self.a > 0 and self.a <= 4:
             print( '第'+str(self.a)+'次尝试')
             self.crack()
         self.close()

     def crack(self):
         self.login()
         self.get_img(self.browser)
         self.imagechange()
         distance=self.matchcmp()
         track=self.get_track(distance)
         self.move_to_gap(track)
         self.temp()

     def close(self):
        self.browser.close()

if __name__ == '__main__':

 dj = crackxujc('CST19036', '110018')
 dj.start()

