import requests
from lxml import etree
import time
import datetime

def get_next_url(next_url_str):
    import re
    temp = re.search(r'360xs\|(.*?)\|book\|com', next_url_str,  re.M | re.I)
    return '/'.join(temp.group(1).split('|'))


# 360小说网
i360xs_Info = {
    'headers': {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    },
    'base_url': 'https://m.i360xs.com/book',
    'host': 'https://m.i360xs.com',
    'url': 'https://m.i360xs.com/book/105017/128708245.html',
    'title_xpath': '/html/body/form/div[@class="readMain"]/div[@id="readercontainer"]/div/h3',
    'content_xpath': '/html/body/form/div[@class="readMain"]/div[@id="readercontainer"]/div/div//p/text()',
    'next_page_xpath': '/html/body/form/div[@class="readMain"]/div/img/@onerror',
    'next_chapter_xpath': '//a[@id="btnNext"]/@href',
    'get_next_url': get_next_url
}


class NovelSpider:
    def __init__(self, website_info):
        self.base_url = website_info['base_url']
        self.host = website_info['host']
        self.url = website_info['url']
        self.headers = website_info['headers']
        self.title_xpath = website_info['title_xpath']
        self.content_xpath = website_info['content_xpath']
        self.next_page_xpath = website_info['next_page_xpath']
        self._get_next_url = website_info['get_next_url']
        self.next_chapter_xpath = website_info['next_chapter_xpath']
        self.content = ''
        self.next_url = self.url
       

    def request(self, url = ''):
        print('request url:', url)
        if url == '':
            url = self.url
        startTime = datetime.datetime.now()
        res = requests.get(url, headers=self.headers)
        # print((datetime.datetime.now() - startTime).seconds)
        return res.text

    def _get_tree(self, html=''):
        if html != '':
            return etree.HTML(html)
        return etree.parse(r'C:\Users\MJCAT\Desktop\new.html', etree.HTMLParser(encoding='utf-8'))

    def get_title(self, tree=''):
        if tree == '':
            return self._get_tree().xpath(self.title_xpath)[0].text.split('（')[0]
        else:
            return tree.xpath(self.title_xpath)[0].text.split('（')[0]

    def get_content(self, tree):
        content_array = tree.xpath(self.content_xpath)
        if len(content_array) > 0:
            count = 0
            for i in content_array:
                if '点击下一页翻页继续阅读' in i:
                    url = self.base_url + '/' + self.get_next_url(tree)
                    time.sleep(1)
                    res = self.request(url)
                    self.get_content(self._get_tree(res))
                elif '本章节完结' in i:
                    self.next_url = self.get_next_chapter_url(tree)
                else:
                    self.content += i +  ('' if count == 0 else '\n')
                    count += 1

    def get_next_url(self, tree):
        next_url_str = tree.xpath(self.next_page_xpath)
        return self._get_next_url(next_url_str[0])  + '.html'
    
    def get_next_chapter_url(self, tree):
        return self.host + tree.xpath(self.next_chapter_xpath)[0]

    def write_to_file(self, title, content):
        with open('史上最强炼气期.txt', 'a+',encoding='utf-8') as f:
            f.write(title + '\n')
            f.write(content)
            
    def Start(self):
        while self.next_url != '':
            res = self.request(self.next_url)
            tree = self._get_tree(res)
            title = self.get_title(tree)
            print(title)
            self.get_content(tree)
            self.write_to_file(title, self.content)


i360Novel = NovelSpider(i360xs_Info)

# data = i360Novel.get_next_url()
i360Novel.Start()


# novalSpider => flow(url)
#                 1. request url
#                 2. get title  by etree  
#                 3. get content
#                 4. write to file
                
#                 5. get next artical url => flow