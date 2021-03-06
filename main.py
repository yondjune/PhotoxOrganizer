# -*- encoding: utf-8 -*-
# heading statement
'''
文件说明：根据图片拍摄日期建立(-年/-月/-日)三级目录(备份资料库)，将文件相应
拷贝至相应日期目录中，并将图片文件名改为拍摄日期(20151210)+原图片名
作者信息：penguinjing & lixiguangzhou
版本自述: 0.5
'''
# 全局引用
import os
import exifread
import shutil
import sys
import hashlib

reload(sys)
sys.setdefaultencoding('utf-8')

# 全局变量
#PATH = "/path/2/work dir"
MONTH_NAMES = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec']


# 函式撰写区
def print_prompt():
    print "  ____   _             _                                     "
    print " |  _ \ | |__    ___  | |_  ___                              "
    print " | |_) || '_ \  / _ \ | __|/ _ \                             "
    print " |  __/ | | | || (_) || |_| (_) |                            "
    print " |_|    |_|_|_| \___/  \__|\___/           _                 "
    print "  __  __  / _ \  _ __  __ _   __ _  _ __  (_) ____ ___  _ __ "
    print "  \ \/ / | | | || '__|/ _` | / _` || '_ \ | ||_  // _ \| '__|"
    print "   >  <  | |_| || |  | (_| || (_| || | | || | / /|  __/| |   "
    print "  /_/\_\  \___/ |_|   \__, | \__,_||_| |_||_|/___|\___||_|   "
    print "                      |___/                                  "
    print '\nAutomatic sort photos by shotting date and backup it.\n'
    print "usage: python main.py <original dir> <target dir>"

def get_all_jpg(path):
    alljpgfilelist = []
    for folderName, subfolders, filenames in os.walk(path):
        for filename in filenames:
            if filename[-4:].lower() == '.jpg':
                jpgfilename = os.path.join(folderName, filename)
                alljpgfilelist.append(jpgfilename)
    return alljpgfilelist

def get_exif_date(FileName):
    tags = {}
    with open(FileName, 'rb') as f:
        tags = exifread.process_file(f, details=False)  #  Return Exif tags as a dictionary
    if 'EXIF DateTimeOriginal' in tags:
        shotDateTime = tags.get('EXIF DateTimeOriginal').values
        shotDate = shotDateTime[:10].split(':')
    else:
        shotDate = 'unknown'
    return shotDate

def create_target_dir(TargetDir, ShotDate):
    if ShotDate == 'unknown':
        targetDirJoin = os.path.join(TargetDir, ShotDate)
    else:    
        year, month, day = ShotDate
        LF_year = ''.join(['Year', year]).encode('ascii','ignore')
        LF_month = ''.join([month, '-', MONTH_NAMES[int(month)-1]]).encode('ascii','ignore')
        LF_day = ''.join(['Day-', day]).encode('ascii','ignore')
        targetDirJoin = os.path.join(TargetDir, LF_year, LF_month, LF_day)
    if os.path.exists(targetDirJoin):
        return
    else:
        os.makedirs(targetDirJoin)

def hash_file(file):
    BLOCKSIZE = 65536
    hasher = hashlib.md5()
    with open(file, 'rb') as f:
        buf = f.read(BLOCKSIZE)
        while len(buf) > 0:
            hasher.update(buf)
            buf = f.read(BLOCKSIZE)
    return hasher.digest()

def copy_image_file(FullFileName, TargetDir, ShotDate):
    if ShotDate == 'unknown':
        newBasename = os.path.basename(FullFileName)
        targetFullFileName = os.path.join(TargetDir, ShotDate, newBasename)
    else: 
        year, month, day = ShotDate
        LF_year = ''.join(['Year', year])
        LF_month = ''.join([month, '-', MONTH_NAMES[int(month)-1]])
        LF_day = ''.join(['Day-', day])
        newBasename = ''.join([year, month, day, '_', os.path.basename(FullFileName)])
        targetFullFileName = os.path.join(TargetDir, LF_year, LF_month, LF_day, newBasename)

    if os.path.isfile(targetFullFileName):
        if hash_file(FullFileName) != hash_file(targetFullFileName):
            oldfilename, extname = os.path.splitext(targetFullFileName)
            for n in range(1, 100):
                targetFullFileName = ''.join([oldfilename, '_', str(n), extname])
                if not os.path.isfile(targetFullFileName):
                    print "\na new file <{}> will be created.".format(os.path.basename(targetFullFileName)) ,
                    break
        else: 
            print "\ntarget file: <{}> existed & passed.".format(os.path.basename(targetFullFileName)) ,
            return
    shutil.copy2(FullFileName, targetFullFileName)

# 自检区
if __name__ == '__main__':
    if len(sys.argv) in [1, 2] or len(sys.argv) > 3:
        print_prompt()
    elif len(sys.argv) == 3:
        selfname, sourcedir, targetdir = sys.argv
        if os.path.isdir(sourcedir) and os.path.isdir(targetdir):
            for jpgfile in get_all_jpg(sourcedir):
                print 'processing files', jpgfile,  
                image_date = get_exif_date(jpgfile)
                create_target_dir(targetdir, ShotDate = image_date)
                copy_image_file(jpgfile, targetdir, ShotDate = image_date)
                print '-> Done'
        else:
            print_prompt()