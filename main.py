#import area
from getInfo import getInfo
import config
def main():
    test = getInfo("https://www.aishuge.la/kan/10/10822/#:~:text=%5B%E7%BB%BC%5D%E5%BF%BD%E6%82%A0%E6%95%91%E4%B8%96%E4%B8%BB%E7%9A%84%E6%AD%A3%E7%A1%AE%E5%A7%BF%E5%8A%BF%E7%AB%A0%E8%8A%82%E5%88%97%E8%A1%A8%20%E7%AC%AC1%E7%AB%A0,%E5%AE%A1%E5%88%A4-%E6%AD%A3%E4%BD%8D%20%E7%AC%AC2%E7%AB%A0%20%E9%AB%98%E5%A1%94-%E9%80%86%E4%BD%8D")
    test.makeBook(config.TEXT)
    #getContents('https://m.yushubo.com/read_93104_1.html',0)
    pass
if __name__ == '__main__':
    main()
