#import area
from getInfo import getInfo
import config
def main():
    test = getInfo("https://www.yinghuatxt.com/ydn296832/")
    test.makeBook(config.TEXT)
    #getContents('https://m.yushubo.com/read_93104_1.html',0)
    pass
if __name__ == '__main__':
    main()
