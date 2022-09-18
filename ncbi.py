#!/usr/bin/python
# -*- coding: UTF-8 -*-
import random

import requests
from lxml import etree
import os
import time
from urllib.parse import urlparse,urlencode
import re

user_agent_list = [
    'Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10_6_8; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (Windows; U; Windows NT 6.1; en-us) AppleWebKit/534.50 (KHTML, like Gecko) Version/5.1 Safari/534.50',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0;',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 6.0; Trident/4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0)',
    'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1)',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.6; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Mozilla/5.0 (Windows NT 6.1; rv:2.0.1) Gecko/20100101 Firefox/4.0.1',
    'Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; en) Presto/2.8.131 Version/11.11',
    'Opera/9.80 (Windows NT 6.1; U; en) Presto/2.8.131 Version/11.11',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_0) AppleWebKit/535.11 (KHTML, like Gecko) Chrome/17.0.963.56 Safari/535.11',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Maxthon 2.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; TencentTraveler 4.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; The World)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Trident/4.0; SE 2.X MetaSr 1.0; SE 2.X MetaSr 1.0; .NET CLR 2.0.50727; SE 2.X MetaSr 1.0)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; 360SE)',
    'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1; Avant Browser)'
]
username = 'tiancong2022'
password = '9y0udocm'


headers = {
    'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36'
}
PDF_DIR = './nibc_pdf'

#成功下载的论文列表
sucess_pdf = []


#获取通过关键字搜索的文章列表
def get_article_list(url):
    response = get_response(url)
    root = etree.HTML(response.text)
    article_list = root.xpath('//*[@id="search-results"]/section[1]/div[1]/div/article')
    url_list = []
    for article in article_list:
        titile = ''.join(article.xpath('./div[@class="docsum-wrap"]/div[1]/a//text()')).strip()
        # print(titile)
        href = article.xpath('./div[@class="docsum-wrap"]/div[1]/a/@href')[0]
        # print(href)
        dict = {'title':titile,'url':"https://pubmed.ncbi.nlm.nih.gov"+href}
        url_list.append(dict)
    return url_list

#获取文章下载地址
def get_download_url(url):
    response = get_response(url)
    root = etree.HTML(response.text)
    #前往文章下载页面获取下载地址
    href_list = root.xpath('//*[@id="article-page"]/aside/div/div[1]/div[1]/div/a[2]/@href')
    if len(href_list) == 0:
        # print(url,"没有免费下载链接！！！！")
        return None
    else:
        href = href_list[0]
        response = get_response(href)
        # new_root = etree.HTML(response.text)
        # download_href = new_root.xpath('//*[@id="main-content"]/aside/div/section[1]/ul/li[2]/a/@href | //*[@id="maincontent"]/div[1]/div/div/a/@href')[0]
        # download_href = new_root.xpath('//*[@id="jr-pdf-sw"]/@href | //*[@id="maincontent"]/div[1]/div/div/a/@href')[0]
        lines = response.text.split('\n')
        download_href = None
        for line in lines:
            a = re.findall('<a .*?href=".*.pdf.*?".*?>',line)
            if len(a) > 0:
                # download_href_list = re.findall('<a .*?href="(.*?.pdf.*?)".*?>',a[0])
                download_href_list = re.findall('href="(.*?)"',a[0])
                flag = False
                for item in download_href_list:
                    if '.pdf' in item:
                        download_href = item
                        flag = True
                        break
                    if flag:
                        break
        u = urlparse(href)
        download_url = u.scheme +'://' + u.hostname + download_href
        return download_url


#下载文件
def download_pdf(url):
    print('正在下载论文:',url)
    response = get_response(url)
    file_name = re.sub(r'\?.*', '', url.split('/')[-1])
    file_path = PDF_DIR + '/' + file_name
    with open(file_path,'wb') as fp:
        fp.write(response.content)
    print('-----------------论文下载成功---------------------')
    sucess_pdf.append(url)

def get_page(url):
    article_url_list = get_article_list(url)
    for article_url in article_url_list:
        print('准备下载论文:',article_url['title'])
        time.sleep(2)
        download_url = get_download_url(article_url['url'])
        if download_url is not None:
            download_pdf(download_url)
        else:
            print(article_url['title'],'-----------没有免费的下载链接,无法下载-------------')


def get_response(url):
    while True:
        try:
            # #获取代理ip
            # api_url = 'https://dps.kdlapi.com/api/getdps/?secret_id=o580q9w1t7vf6utos8le&num=1&signature=ortbhvf8o8b0jdwvxxszv0i25u&pt=1&sep=1'
            # proxy_ip = requests.get(api_url).text
            # print('代理ip:',proxy_ip)
            # proxies = {
            #     'https': f'http://{username}:{password}@{proxy_ip}',
            # }
            headers['User-Agent'] = random.choice(user_agent_list)
            #通过代理访问
            # response = requests.get(url=url, headers=headers, proxies=proxies)
            response = requests.get(url=url, headers=headers)

            if response.status_code == 200:
                return response
        except Exception as e:
            print(e)
            time.sleep(1)
    return response

if __name__ == '__main__':
    if not os.path.exists(PDF_DIR):
        os.mkdir(PDF_DIR)
    kw = input('请输入搜索关键字:')
    articleNum = input('请输入你想下载的文章数量:')
    pageNum = input('请输入你希望从搜索结果的第几页开始下载:')
    articleNum = int(articleNum)
    pageNum = int(pageNum)
    while True:
        params = urlencode({'term': kw, 'page': pageNum})
        url = f'https://pubmed.ncbi.nlm.nih.gov/?{params}'
        print(f'正在访问关键字{kw}搜索结果第{pageNum}页:',url)
        get_page(url)
        if  len(sucess_pdf) >= articleNum:
            print(f'-----------下载结束(最后访问的是搜索结果的第{pageNum}页)-------------')
            break
        pageNum += 1




