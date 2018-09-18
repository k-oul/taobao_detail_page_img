#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/9/17/017 11:52
# @Author  : K_oul
# @File    : spider.py
# @Software: PyCharm

import requests
import re
import json
from fake_useragent import UserAgent



ua = UserAgent()

class Spider:
    def __init__(self):

        self.url = 'https://item.taobao.com/item.htm?id=558823044757'
        self.headers = {
            'user-agent': ua.random
        }
        self.id = self.get_id()

    def get_text(self,url):
        try:
            r = requests.get(url, headers=self.headers)
            r.raise_for_status()
            r.encoding = r.apparent_encoding
            return r.text
        except:
            print('get_text Error {}'.format(url))
            return None
    #
    def get_id(self):
        id = re.findall(r'id=(\d+)',self.url)[0]
        return id



    # def parse(self,html):
    #     pattern = re.compile(r'<img.*?src="(.*?)"',re.S)
    #     img = re.findall(pattern,html)
    #     print(img)



    def get_main_img(self):
        html = self.get_text(self.url)
        pattern = re.compile(r'<div class="tb-pic tb-s50">.*?<img data-src="(.*?'
                             r')".*?data-src="(.*?)".*?data-src="(.*?)".*?data-src="(.*?'
                             r')".*?data-src="(.*?)".*?</ul>', re.S)
        main_img = re.findall(pattern, html)[0]
        main_img = ['http:' + i[:-10] for i in main_img]

        # print('商品主图URL',res)
        return main_img


    def get_detail_page(self):
        # 构造详情页api 返回详情页信息
        res = dict()
        detail_api = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?' \
                     'type=json&data=%7B"itemNumId"%3A"{}"%7D'.format(self.id)
        html = self.get_text(detail_api)
        data = json.loads(html).get('data')
        detail_page = data.get('item').get('images')
        detail_page = ['http:'+i for i in detail_page]
        sku_info = data.get('skuBase').get('props')[0].get('values')
        res['img'] = detail_page
        res['sku'] = sku_info
        # print('商品SKU信息', res['sku'])
        # print('商品详情页图片', res['img'])
        return res


    def get_rate_img(self,):

        res = dict()
        rate_api = 'https://rate.taobao.com/feedRateList.htm?auctionNumId={}&currentPageNum=4&pageSize=20&rateType=3&orderType=sort_weight&hasSku=false&folded=0&callback=jsonp_tbcrate_reviews_list'.format(self.id)
        html = self.get_text(rate_api)

        pattern = re.compile(r'"url":"(.*?)".*?"receiveId":(.*?),"status"', re.S)
        rate_img = re.findall(pattern, html)
        # print(rate_img)
        rate_count = re.findall(r'"total":(\d+),', html)[0]
        rate_count = int(rate_count)
        res ={
            'rate_img': rate_img,
            'rate_count': rate_count
        }

        return res

    def get_all_rate_img(self):
        res = self.get_rate_img()
        rate_count = res.get('rate_count')
        pages = int(rate_count) // 20 + 1
        if rate_count > 1:
            for i in range(2, pages + 1):
                temp = self.get_rate_img().get('rate_img')
                res['rate_img'].extend(temp)
        return res



    def get_rate_video(self):
        pass

def main():
    res = dict()
    spider = Spider()
    # detail_page = spider.get_detail_page()
    # res['detail_img'] = detail_page.get('img')
    # res['sku_info'] = detail_page.get('sku')
    # res['main_img'] = spider.get_main_img()
    # print(res)
    rate_imgs = spider.get_all_rate_img()
    print(rate_imgs)
    # print(len(rate_imgs['rate_img']))



if __name__ == '__main__':
    main()

