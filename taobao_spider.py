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
import sys
from fake_useragent import UserAgent
from concurrent.futures import ThreadPoolExecutor


class Spider:
    def __init__(self):
        '''
        初始化
        '''
        # self.url = 'https://item.taobao.com/item.htm?id=13477299941'
        self.url = input('请输入宝贝链接: ')
        self.ua = UserAgent()
        self.headers = {
            'user-agent': self.ua.random
        }
        self.id = self.get_id() # 获取宝贝ID
        self.all_rate = list()

    def get_text(self, url):
        '''
        requests请求函数
        :param url:
        :return: Html
        '''
        r = requests.get(url, headers=self.headers)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text

    def get_id(self):  # 获取宝贝ID
        id = re.findall(r'id=(\d+)', self.url)[0]
        return id

    def get_detal_img(self):
        '''
        获取详情页图片url
        :return: url 列表
        '''
        base_url = 'https://mdetail.tmall.com/templates/pages/itemDesc?id={}'.format(self.id)
        try:
            html = self.get_text(base_url)
        except:
            print('获取base_url失败！ : {} 重新发起请求中...'.format(base_url))
            html = self.get_text(base_url)
        else:
            print('请求base_url成功！！！')
        pattern = re.compile(r'descUrl":"(.*?)".*?context', re.S)
        desc_url = 'http:' + re.findall(pattern, html)[0]
        try:
            html = self.get_text(desc_url)
        except:
            print('获取desc_url失败！！！ : {} 重新发起请求中...'.format(desc_url))
            html = self.get_text(desc_url)
        else:
            print('请求desc_url成功！！！')

        pattern = re.compile(r'src="(.*?)"', re.S)
        detail_img = re.findall(pattern, html)
        print('获取详情页图片成功！！！')
        return detail_img

    def get_main_img(self):
        '''
        获取主图和sku图
        :return: 包含主图与sku图url的字典
        '''
        detail_api = 'https://h5api.m.taobao.com/h5/mtop.taobao.detail.getdetail/6.0/?' \
                     'type=json&data=%7B"itemNumId"%3A"{}"%7D'.format(self.id)
        try:
            html = self.get_text(detail_api)
        except:
            print('获取detail_api失败！！！ : {} 重新发起请求中...'.format(detail_api))
            html = self.get_text(detail_api)
        try:
            data = json.loads(html).get('data')
            main_img = data.get('item').get('images')
            print('请求detail_api成功！！！')
            print('获取主图成功！！！')
            main_img = ['https:'+i for i in main_img]
            sku_infos = data.get('skuBase').get('props')
            if sku_infos:
                for sku_info in sku_infos:
                    values = sku_info.get('values')
                    for value in values:
                        if 'image' in value:
                            value['image'] = 'https:' + value['image']
            print('获取sku信息成功！！！')
            res = {
                'img': main_img,
                'sku': sku_infos,
            }
            return res
        except:
            print('宝贝链接有误, 请重新输入！')
            return None


    def get_rate_img(self, page=1):
        '''
        获取一页评论图片
        :param page:
        :return: 评论总数 与 评论图片 id ，url
        '''
        rate_api = 'https://rate.taobao.com/feedRateList.htm?auctionNumId={}' \
                   '&currentPageNum={}&pageSize=20&rateType=3&orderType=sort_weight' \
                   '&hasSku=false&folded=0&callback=jsonp_tbcrate_reviews_list'.format(self.id, page)
        try:
            html = self.get_text(rate_api)
        except:
            print('请求rate_api失败！！！ : {} 重新发起请求中...'.format(rate_api))
            html = self.get_text(rate_api)
        else:
            print('请求rate_api成功！！！')
        pattern = re.compile(r'"url":"(.*?)".*?"receiveId":(.*?),"status"', re.S)
        rate_img = re.findall(pattern, html)
        rate_img = [(id, 'https:' + url[:-12]) for url, id in rate_img]
        rate_count = re.findall(r'"total":(\d+),', html)[0]
        rate_count = int(rate_count)
        res = {
            'rate_count': rate_count,
            'rate_img': rate_img,
        }
        self.all_rate.extend(res['rate_img'])
        return res

    def get_all_rate_img(self):
        '''
        获取所有评论图片
        :return: all_rate
        '''
        res = self.get_rate_img()
        self.all_rate += res.get('rate_img')
        rate_count = res.get('rate_count')
        pages = int(rate_count) // 20 + 1
        if rate_count > 1:
            with ThreadPoolExecutor(max_workers=10) as executor:
                executor.map(self.get_rate_img, range(2, pages+2))
        print('获取所有评论图片成功！！！')
        return self.all_rate

    def get_rate_video(self):
        pass


def main():
    # 实例化爬虫
    spider = Spider()
    start = time.time()
    main_img = spider.get_main_img()
    # 条件判断： 宝贝id是否有效，若无效则退出爬虫
    if main_img is None:
        raise SystemExit('宝贝id不存在')
        # sys.exit()
    res = {
        'main_img': main_img.get('img'), #  主图
        'sku_info': main_img.get('sku'), #  sku图
        'detail_img': spider.get_detal_img(),  # 详情页图
        'rate_img': spider.get_all_rate_img(),  # 评论图
    }
    print(time.time() - start)
    print(res)
    print(len(res['rate_img']))
    # 返回字典对象
    return res


if __name__ == '__main__':
    # 启动爬虫主函数
    main()
