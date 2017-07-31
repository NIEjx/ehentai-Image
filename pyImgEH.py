# for e-hentai.org
import os
from queue import Queue
import re
import time
import threading
import urllib.request
import urllib.error
import bs4
#replace url to start your own download
url = "https://e-hentai.org/g/1080929/7574e13d50/"

dirname = os.getcwd()
print_lock = threading.Lock()
data_q = Queue()

MaxThread = 40

def getImgAddr(numpages):
    print("Start to get imgURL")
    #img addr list
    list = []

    addrlist = []
    for iStr in range(1,numpages+1):
        tmpAddr = url+"?p="+str(iStr)
        addrlist.append(tmpAddr)
    for iAddr in addrlist:
        with urllib.request.urlopen(iAddr) as html:
            raw = html.read()
        soup = bs4.BeautifulSoup(raw, "html.parser")
        tmp_gdtm = soup.findAll('div', class_='gdtm')
        for iGdtm in tmp_gdtm:
            tmpUrl = iGdtm.find('a').get('href')
            list.append(tmpUrl)
    print("Get imgURL---------Done")
    return list

def mkdir(path):
    tmppath = os.getcwd()+"\\"+path
    try:
        os.makedirs(tmppath)
    except:
        print("DIR exist!")
        exit()
    return tmppath
def saveImg(imgUrl):
    time.sleep(0.1)
    with print_lock:
        imgName = imgUrl.split('-')[-1]
        with urllib.request.urlopen(imgUrl) as html:
            rawurl = html.read()
            soup = bs4.BeautifulSoup(rawurl,"html.parser")
            tmpimgurl = soup.find(id='i3').find('img').get('src')
            extension = "."+tmpimgurl.split('.')[-1]
            with urllib.request.urlopen(tmpimgurl) as imghtml:
                rawimg = imghtml.read()
                with open(imgName+extension,'wb') as file:
                    file.write(rawimg)
                print(imgName+extension,"------downloaded!")
            # try:
            #     raw = urllib.request.urlopen()
            #     img = raw.read()
            #     raw.close()
            #     with open(imgData.dir+"\\"+imgName,'wb') as file:
            #         file.write(img)
            # except:
            #     print("error:",imgName," not exist")
            #     pass
def worker():
    while True:
        tmpUrl = data_q.get()
        saveImg(tmpUrl)
        data_q.task_done()
#def imglist():

def main():
    #socket.setdefaulttimeout(10)

    for x in range(MaxThread):
        t = threading.Thread(target = worker)
        t.daemon = True
        t.start()
    start = time.time()
#----------------------------------
    raw = ""
    with urllib.request.urlopen(url) as html:
        raw = html.read()
    # with open("test2.html",'r+',encoding='utf-8') as file:
    #     raw = file.read()
    #     #print(raw)
#---------------------------------
    #图片文件信息在gm class的div里面
    soup = bs4.BeautifulSoup(raw,"html.parser")
    all_gm = soup.findAll('div',class_='gm')
    tmplist = []
    numpages = 0
    for i in all_gm:
        i.findAll('h1')
        if(len(i.findAll('h1')) != 0):
            tmplist.append(i)
    if(len(tmplist)!=1):
        print("Multipul error! Please mail the author")
        exit()
    else:
        infolist = tmplist[0]
#=================================  use url last split
        tmpStr = url.split('/')[-2]
        os.chdir(mkdir(tmpStr))
#=================================
        with open("info.html",'w',encoding='utf-8') as file:
            file.write("<html>\n<head><title>infomation</title>\n</head>")
            file.write("<body><p>download source:")
            file.write(url)
            file.write("</p>")
            filename = infolist.findAll('h1')
#=====================
            file.write("<p>file name</p>")
            for i in filename:
                stri = str(i).replace("<h1","<p")
                stri = stri.replace("/h1>","/p>")
                file.write(stri)
            fileinfo = infolist.find(id='gdd')
            file.write("<p>file info</p>")
            file.write(str(fileinfo))
            strinfo = str(fileinfo)
            # print(strinfo)
            # 暂时匹配的是整数 size的一般是浮点数 日期则有横杠
            pages = re.findall(r"gdt2\">(\d+) ",strinfo)
            print("图片数：",int(pages[0]))
            numpages = int(pages[0])

            taginfo = infolist.find(id='taglist')
            file.write("<p>tags</p>")
            file.write(str(taginfo))
            file.write("</body></html>")
#=====================
    #所有页 总页数/40
    tmp = numpages/40
    if(tmp>int(tmp)):
        tmp +=1
    all_imgs = getImgAddr(int(tmp))

    for iimg in all_imgs:
        data_q.put(iimg)
    all_imgs.clear()

    data_q.join()
    print("entire job took:", time.time()-start)

if __name__ == '__main__':
  main()

