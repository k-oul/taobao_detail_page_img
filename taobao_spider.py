#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/17/017 11:52
# @Author  : K_oul
# @File    : taobao_spider.py
# @Software: PyCharm

import requests
import re
import json
import time
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor, as_completed


ua = UserAgent()

class Spider:
    def __init__(self):

        self.url = 'https://item.taobao.com/item.htm?id=567611571486'

        self.headers = {
            'user-agent': ua.random
        }
        self.id = self.get_id()
        self.all_rate =[]

    def get_text(self, url):
        try:
            r = requests.get(url, headers=self.headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            print('get_text Error {}'.format(url))
            return None

    def get_id(self):
        id = re.findall(r'id=(\d+)',self.url)[0]
        return id




    def get_detal_img(self):
        base_url = 'https://mdetail.tmall.com/templates/pages/itemDesc?id={}'.format(self.id)
        html = self.get_text(base_url)
        pattern = re.compile(r'descUrl":"(.*?)".*?context', re.S)
        desc_url = 'http:' + re.findall(pattern, html)[0]

        html = self.get_text(desc_url)
        pattern = re.compile(r'src="(.*?)"', re.S)
        detail_img = re.findall(pattern, html)
        return detail_img


    def get_main_img(self):
        # 构造详情页api 返回详情页信息
        res = dict()
        detail_api = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?' \
                     'type=json&data=%7B"itemNumId"%3A"{}"%7D'.format(self.id)
        html = self.get_text(detail_api)
        data = json.loads(html).get('data')
        main_img = data.get('item').get('images')
        main_img = ['https:'+i for i in main_img]
        sku_info = data.get('skuBase').get('props')[0].get('values')

        if 'image' in sku_info[0]:
            for dt in sku_info:
                dt['image'] = 'https:' + dt['image']
        res['img'] = main_img
        res['sku'] = sku_info
        # print('商品SKU信息', res['sku'])
        # print('商品详情页图片', res['img'])
        return res


    def get_rate_img(self, page=1):

        res = dict()
        rate_api = 'https://rate.taobao.com/feedRateList.htm?auctionNumId={}' \
                   '&currentPageNum={}&pageSize=20&rateType=3&orderType=sort_weight' \
                   '&hasSku=false&folded=0&callback=jsonp_tbcrate_reviews_list'.format(self.id, page)
        html = self.get_text(rate_api)

        pattern = re.compile(r'"url":"(.*?)".*?"receiveId":(.*?),"status"', re.S)
        rate_img = re.findall(pattern, html)
        rate_img =[('https:' + url[:-12], id) for url, id in rate_img]

        rate_count = re.findall(r'"total":(\d+),', html)[0]
        rate_count = int(rate_count)
        res ={
            'rate_img': rate_img,
            'rate_count': rate_count
        }
        self.all_rate += res['rate_img']
        return res

    def get_all_rate_img(self):

        res = self.get_rate_img()
        self.all_rate += res.get('rate_img')
        rate_count = res.get('rate_count')
        pages = int(rate_count) // 20 + 1
        if rate_count > 1:
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.get_rate_img, range(2,pages+2))

        return self.all_rate



    def get_rate_video(self):
        pass





def main():
    start = time.time()
    res = dict()
    spider = Spider()
    main_img = spider.get_main_img()
    res['main_img'] = main_img.get('img')
    res['sku_info'] = main_img.get('sku')
    res['detail_img'] = spider.get_detal_img()
    res['rate_img'] = spider.get_all_rate_img()
    print(time.time() - start)
    print(res)
    print(len(res['rate_img']))





if __name__ == '__main__':
    main()

