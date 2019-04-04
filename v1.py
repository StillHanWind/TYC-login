#!/usr/bin/env python
# -*- coding:utf-8 -*-
# author: stillhanwind
# e-mail: stillhanwind@163.com

import json
import time
import random
from io import BytesIO
from selenium import webdriver
from selenium.webdriver import ActionChains
from PIL import Image


class GeeTestR(object):
    def __init__(self):
        # 启动项设置
        self.chromeOpitons = webdriver.ChromeOptions()
        self.chromeOpitons.add_argument('--headless')  # 无头
        self.chromeOpitons.add_argument('--disable-infobars')  # 禁用自动化提示
        self.chromeOpitons.add_argument('user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36"')  # 防止headless请求头被ban
        # self.chromeOpitons.add_argument("--start-maximized")  # 最大化
        self.dc = webdriver.DesiredCapabilities.CHROME
        self.dc['loggingPrefs'] = {'performance': 'ALL'}
        self.browser = None
        self.im_bg = None
        self.im_cc = None
        self.user = ''
        self.password = ''

    def __del__(self):
        time.sleep(10)
        self.browser.close()

    def open(self):
        self.browser = webdriver.Chrome(
            desired_capabilities=self.dc,
            chrome_options=self.chromeOpitons,
            executable_path='/Users//Desktop/drivers/chromedriver'
        )
        # self.browser.maximize_window()  # 设置浏览器大小：全屏 15寸mac no headless
        self.browser.set_window_size(1680, 979)  # 设置浏览器大小：1680*979 neadless
        self.browser.get('https://www.tianyancha.com/')
        time.sleep(2)

    def close(self):
        self.browser.close()

    def login(self):
        # 点击登陆/注册
        self.browser.find_element_by_xpath('//a[@class="link-white"]').click()
        time.sleep(2)
        # 点击密码登陆
        self.browser.find_element_by_xpath('//div[@class="title" and @active-tab="1"]').click()
        time.sleep(2)
        # 输入账号
        self.browser.find_element_by_xpath('//div[contains(@class, "modulein1")]/div/input[@class="input contactphone"]').send_keys(self.user)
        time.sleep(2)
        # 输入密码
        self.browser.find_element_by_xpath('//div[contains(@class, "modulein1")]/div/input[@class="input contactword input-pwd"]').send_keys(self.password)
        time.sleep(2)
        # 点击登陆
        self.browser.find_element_by_xpath('//div[@tyc-event-ch="LoginPage.PasswordLogin.Login"]').click()
        time.sleep(4)
        # self.browser.save_screenshot('full.png')
        # time.sleep(1)
        # 获取点击前背景图
        self.im_bg = self.get_img('bg.png', '//div[@class="gt_box_holder"]/div[@class="gt_box"]')

        # 左键按住滑块
        click_elem = self.browser.find_element_by_xpath('//div[@class="gt_slider_knob gt_show"]')
        ActionChains(self.browser).click_and_hold(click_elem).perform()
        time.sleep(0.5)

        # 获取点击后验证码
        self.im_cc = self.get_img('captcha.png', '//div[@class="gt_box_holder"]/div[@class="gt_box"]')

        # 获取偏移量
        offset = self.get_offset() - 8
        track = self.get_track(offset)
        print(track)

        # 移动并松开
        y = 1
        # t = random.randrange(10, 15) if offset > 100 else random.randrange(15, 20)
        # t = random.randrange(10, 15)/1000

        for x in track:
            y = -y if x else y
            ActionChains(self.browser).move_by_offset(xoffset=x, yoffset=y).perform()
            time.sleep(0.01)
        time.sleep(0.3)
        ActionChains(self.browser).release().perform()
        time.sleep(5)
        self.browser.save_screenshot('moved.png')

    def get_img(self, file, elem_xpath):
        # 截图
        # self.browser.save_screenshot(file)
        # im = Image.open(file)
        sc = self.browser.get_screenshot_as_png()
        im = Image.open(BytesIO(sc))

        # 找到验证码区域元素
        img_elem = self.browser.find_element_by_xpath(elem_xpath)

        # 获取浏览器大小
        b_size = self.browser.get_window_size()
        b_width = b_size['width']
        b_height = b_size['height']

        # 设置大小为浏览器大小
        im = im.resize((b_width, b_height), Image.ANTIALIAS)

        # 获取验证码区域坐标
        left = int(img_elem.location['x'])
        top = int(img_elem.location['y'])
        right = left + int(img_elem.size['width'])
        bottom = top + int(img_elem.size['height'])

        # 切图并存储
        im = im.crop((left, top, right, bottom))
        # im.save(file)
        return im

    def get_offset(self):
        bg = self.im_bg
        cc = self.im_cc
        left = 60
        for i in range(left, bg.size[0]):
            for j in range(bg.size[1]):
                if not self.is_pixel_equal(bg, cc, i, j):
                    left = i
                    return left
        return left

    @staticmethod
    def get_track(distance):
        print('distance:', distance)
        # 移动轨迹
        track = []
        # 当前位移
        current = 0
        # 减速阈值
        # t = random.randrange(30, 40) if distance > 100 else random.randrange(20, 30)
        # t = random.randrange(30, 40)/10
        mid = distance * 30 / 5
        # 计算间隔
        t = 0.2
        # 初速度
        v = 0

        # x = random.randrange(15, 20)/10
        # y = random.randrange(10, 15)/10

        while current < distance:
            if current < mid:
                # 加速度为正2
                a = 2
                # a = x
            else:
                # 加速度为负3
                a = -1
                # a = -y
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
        return track

    @staticmethod
    def is_pixel_equal(img1, img2, x, y):
        pix1 = img1.load()[x, y]
        pix2 = img2.load()[x, y]

        # 像素RGB差阈值
        threshold = 80

        if (abs(pix1[0] - pix2[0] < threshold) and abs(pix1[1] - pix2[1] < threshold) and abs(
                        pix1[2] - pix2[2] < threshold)):
            return True
        else:
            return False

    def is_successed(self):
        if '登录/注册' in self.browser.page_source:
            print('登录失败')
            return False
        else:
            print('登录成功')
            return True

    def run(self):
        try:
            self.open()
            self.login()
            print(self.is_successed())
            time.sleep(10)
            self.browser.close()
        except Exception as e:
            self.browser.close()
            raise e

    def main(self):
        count = 1
        success_c = 0
        while count <= 100:
            print('='*50)
            print('count:', count)
            print('success_c:', success_c)
            self.open()
            self.login()
            if self.is_successed():
                success_c += 1
            time.sleep(5)
            self.browser.close()
            count += 1
        print('{}/{}'.format(success_c, count-1))


if __name__ == '__main__':
    gt = GeeTestR()
    gt.run()
    # gt.main()
