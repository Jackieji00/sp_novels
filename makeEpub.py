import zipfile
import os


# mimetype
# META-INF/
#    container.xml
# OEBPS/
#   content.opf
#   title.html    (可忽略)
#   content.html  (可忽略)
#   stylesheet.css
#   toc.ncx
#   images/       (可忽略)
#      cover.png
class epub:

    def __init__(self,title,author):
        self.title = title
        self.author = self.author
        if not os.path.exists(title): #如果文件夹不存在，则新建
            os.mkdir(title)
        os.chdir(title)
        self.epubFile = zipfile.ZipFile(title+".epub","w")
        #初始化根目录
        self.epubFile.writestr("mimetype",'application/epub+zip',compress_type = zipfile.ZIP_STORED)
        # read container_temp and write to the certain file
        con_temp = open('../temp/container_temp.xml','r')
        con_temp_text = con_temp.read()
        self.epubFile.writestr("META-INF/container.xml",con_temp_text,compress_type = zipfile.ZIP_STORED)
        con_temp.close()
        style_temp = open('../temp/stylesheet.css','r',encoding = "utf-8")
        style_temp_text = style_temp.read()
        self.epubFile.writestr("OEBPS/stylesheet.css",style_temp_text,compress_type = zipfile.ZIP_STORED)
        style_temp.close()
        con_head_temp = open('../temp/content_head.txt','r')
        self.content = con_head_temp.read()
        con_head_temp.close()
        addInfo()
    def addInfo(self):
        self.content += '<dc:title>'+self.title+'</dc:title>'
        self.content += '<dc:creator>'+self.author+'</dc:creator>'
    def addFile(self,id):
        pass
    def close(self):
        pass
