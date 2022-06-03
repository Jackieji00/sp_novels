#import area
#third party
from bs4 import BeautifulSoup
from tqdm import tqdm
import requests
# python original
import _thread
import time
import os
#self written
import makeEpub
import config
####################################################
#global value
lst = []
threadpool={}
####################################################
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

    def getContents(self,target,chapter,count,indexPage):
        #to get content in website
        while 1:
            try:
                id=_thread.get_native_id()
                print("thread "+str(id)+" start getting chapter "+chapter+"\n")
                sess = requests.Session()
                sess.keep_alive = False # 关闭多余连
                req = requests.get(url=target, stream=True, timeout=(5,5))
                req.encoding = "utf-8"
                wholePage = req.text
                bs = BeautifulSoup(wholePage,'lxml')
                content = bs.find('content',id='readContent')
                texts = bs.find_all('p')
                # delete last tag
                l = len(texts)
                del texts[l-3:l]
                # save to global value
                self.lock_lst.acquire()
                d= lst[count]
                if not chapter in d:
                    d[chapter]=[]
                if texts not in d[chapter]:
                    d[chapter].append(texts)
                self.lock_lst.release()

                #针对1章分多页的情况
                nextPg = bs.find("a",string="下一页")
                req.close()
                if not nextPg==None: #如果没有下一页的link，就停止
                    # print(nextPg.get('href'))
                    link=config.DOMAIN+nextPg.get('href')
                    # print(link)
                    self.getContents(link,chapter,count,indexPage+1)
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

    def getIndex(self):
        # read index and get contents
        index_container = self.bs.find_all("li",id='chapter')
        count =0
        for i in range(len(index_container)):
            lst.append(dict())
        self.lock = _thread.allocate_lock()
        # for i in range(3):
        #     index = index_container[i]
        for index in tqdm(index_container):
            chapter = index.find('a')
            while self.threadwork>=config.THREADNUM:
                pass
            id = _thread.start_new_thread(self.getContents,(config.DOMAIN+chapter.get('href'),chapter.text,count,0))
            count+=1
            threadpool[id]=1
            self.lock.acquire()
            self.threadwork+=1
            self.lock.release()

    def makeBook(self,type):
        #make the content into a book
        if type ==config.EPUB:
            #make epub
            bk = makeEpub.epub(self.title)
            bk.close()
        elif type ==config.TEXT:
            #make txt
            if not os.path.exists(config.SAVE_ADDRESS): #如果文件夹不存在，则新建
                os.mkdir(config.SAVE_ADDRESS)
            if not os.path.exists(config.SAVE_ADDRESS+self.title): #如果文件夹不存在，则新建
                os.mkdir(config.SAVE_ADDRESS+self.title)
            os.chdir(config.SAVE_ADDRESS+self.title)
            #把东西写进去
            self.fdIndex = open('./'+self.title+"目录.txt",'a',encoding='utf-8')
            self.getIndex()
            while self.threadwork>0:
                #print(self.threadwork)
                pass
            print("爬完了,开始存入电脑")
            fd = open('./'+self.title+".txt",'a',encoding='utf-8')

            for dic in tqdm(lst):
                keylst=list(dic.keys())
                # print(keylst)
                for key in keylst:
                    fd.write(key)
                    fd.write('\n\n')
                    self.fdIndex.write(key)
                    v = dic[key]
                    for texts in v:
                        for text in texts:
                            #print(text.text)
                            fd.write(text.text)
                            fd.write('\n')
                fd.flush()
            fd.close()
            self.fdIndex.close()
            print(self.title+"下载完成")
        pass
