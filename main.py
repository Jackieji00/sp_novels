#import area
import requests
from bs4 import BeautifulSoup
from tqdm import tqdm
import _thread
import time
#import re
import os

import makeEpub
EPUB= 1
TEXT = 0
DOMAIN = "https://m.yushubo.com/"
lst = []
threadpool={}
class getInfo:

    def __init__(self,link):
        self.link =link
        req = requests.get(url=link)
        req.encoding = "utf-8"
        wholePage = req.text
        self.bs = BeautifulSoup(wholePage,'lxml')
        self.title = self.bs.find(attrs={'property':'og:title'})['content']
        self.description = self.bs.find(attrs={'property':'og:description'})['content']
        self.auther = self.bs.find(attrs={'property':'og:novel:author'})['content']
        self.cover_link = self.bs.find(attrs={'class':'lazy'})["src"]
        self.threadwork=0
        self.lock_lst = _thread.allocate_lock()
        req.close()

    def getContents(self,target,chapter,count):
        while 1:
            try:
                id=_thread.get_native_id()
                print("thread "+str(id)+" start getting chapter "+chapter+"\n")
                sess = requests.Session()
                # sess.mount('http://', HTTPAdapter(max_retries=3))
                # sess.mount('https://', HTTPAdapter(max_retries=3))
                sess.keep_alive = False # 关闭多余连
                req = requests.get(url=target, stream=True, timeout=(5,5))
                req.encoding = "utf-8"
                wholePage = req.text
                bs = BeautifulSoup(wholePage,'lxml')
                content = bs.find('content',id='readContent')
                texts = bs.find_all('p')
                # delete last tag
                l = len(texts)
                #print(lst)
                del texts[l-3:l]
                self.lock_lst.acquire()
                d= lst[count]
                if not chapter in d:
                    d[chapter]=[]
                    d[chapter].append(texts)
                else:
                    d[chapter].append(texts)
                self.lock_lst.release()
                # for text in texts:
                #     self.fd.write(text.text)
                #     self.fd.write("\n")
                #针对1章分多页的情况
                nextPg = bs.find("a",string="下一页")
                req.close()
                if not nextPg==None: #如果没有下一页的link，就停止
                    # print(nextPg.get('href'))
                    link=DOMAIN+nextPg.get('href')
                    # print(link)
                    self.getContents(link,chapter,count)
                    break
                else:
                    threadpool[id]=0
                    self.lock.acquire()
                    self.threadwork-=1
                    self.lock.release()
                    return
            except requests.exceptions.ConnectTimeout as e:
                #如果请求太快，就暂停，然后重新开始

                print("Connection refused by the server..")
                print("Let me sleep for 5 seconds")
                print("ZZzzzz...")
                time.sleep(5)
            except Exception as f:
                print(f)
                break

    # def getContents(self,target,chapter,count):
    #     id=_thread.get_native_id()
    #     #print("thread "+str(id)+" start getting chapter "+chapter+"\n")
    #     sess = requests.Session()
    #     # sess.mount('http://', HTTPAdapter(max_retries=3))
    #     # sess.mount('https://', HTTPAdapter(max_retries=3))
    #     sess.keep_alive = False # 关闭多余连
    #     req = requests.get(url=target, stream=True, timeout=(5,5))
    #     req.encoding = "utf-8"
    #     wholePage = req.text
    #     bs = BeautifulSoup(wholePage,'lxml')
    #     content = bs.find('content',id='readContent')
    #     texts = bs.find_all('p')
    #     # delete last tag
    #     lst.append(dict())
    #     # print("len "+str(len(lst)))
    #     # print("lencount:"+str(count))
    #     l = len(texts)
    #     #print(lst)
    #     del texts[l-3:l]
    #     self.lock_lst.acquire()
    #     d= lst[count]
    #     if not chapter in d:
    #         d[chapter]=[]
    #         d[chapter].append(texts)
    #     else:
    #         d[chapter].append(texts)
    #     self.lock_lst.release()
    #     # for text in texts:
    #     #     self.fd.write(text.text)
    #     #     self.fd.write("\n")
    #     #针对1章分多页的情况
    #     nextPg = bs.find("a",string="下一页")
    #     req.close()
    #     if not nextPg==None: #如果没有下一页的link，就停止
    #         # print(nextPg.get('href'))
    #         link=DOMAIN+nextPg.get('href')
    #         # print(link)
    #         self.getContents(link,chapter,count)
    #     else:
    #         threadpool[id]=0
    #         self.lock.acquire()
    #         self.threadwork-=1
    #         self.lock.release()
    #         return
    def getIndex(self):
        # make index and get contents
        index_container = self.bs.find_all("li",id='chapter')
        count =0
        for i in range(len(index_container)):
            lst.append(dict())
        self.lock = _thread.allocate_lock()
        # for i in range(3):
        #     index = index_container[i]
        for index in tqdm(index_container):
            chapter = index.find('a')
            #self.getContents(DOMAIN+chapter.get('href'),chapter.text,count)
            while self.threadwork>=40:
                pass
            id = _thread.start_new_thread(self.getContents,(DOMAIN+chapter.get('href'),chapter.text,count))
            count+=1
            threadpool[id]=1
            self.lock.acquire()
            self.threadwork+=1
            self.lock.release()

    def makeBook(self,type):
        #make the content into a book

        if type ==EPUB:
            #make epub
            bk = makeEpub.epub(self.title)
            bk.close()
        else:
            #make txt
            if not os.path.exists(self.title): #如果文件夹不存在，则新建
                os.mkdir(self.title)
            os.chdir(self.title)
            #把东西写进去
            self.getIndex()
            while self.threadwork>0:
                #print(self.threadwork)
                pass
            print("爬完了,开始写")
            fd = open('./'+self.title+".txt",'a',encoding='utf-8')
            for dic in tqdm(lst):
                keylst=list(dic.keys())
                # print(keylst)
                for key in keylst:
                    fd.write(key)
                    fd.write('\n\n')
                    v = dic[key]
                    for texts in v:
                        for text in texts:
                            #print(text.text)
                            fd.write(text.text)
                            fd.write('\n')
                fd.flush()
            fd.close()
            print("小说下载完成")
        pass
def main():
    test = getInfo("https://m.yushubo.com/book_68688.html")
    test.makeBook(TEXT)
    #getContents('https://m.yushubo.com/read_93104_1.html',0)
    pass
if __name__ == '__main__':
    main()
