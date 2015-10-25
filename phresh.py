#!/usr/bin/env python

import datetime
import exifread
import hashlib
import os
import shutil
import sys
import time
import uuid

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def clean_photos(path, output_dir):
    exts = [".jpg",".JPG",".jpeg",".JPEG",".TIFF",".tiff",".NEF",".nef"]
    hashes = []
    photos = {}
    num_photos = 0
    untouched_files = []
    no_date = 0
    for root, dirs, files in os.walk(path):
        path = root.split('/')
        for f in files:
            if f != ".DS_Store" and output_dir not in path:
                flag = 0
                for ext in exts:
                    if f.endswith(ext):
                        flag = 1
                        fname = root+"/"+f
                        num_photos += 1
                        rows,columns = os.popen('stty size', 'r').read().split()
                        rows = int(rows)
                        columns = int(columns)
                        sys.stdout.write('\r')
                        sys.stdout.write(' ' * columns)
                        sys.stdout.write('\r')
                        sys.stdout.write('processing {}'.format(fname[:columns-12]))
                        sys.stdout.flush()
                        h = md5(fname)
                        if not h in hashes:
                            hashes.append(h)
                            dt = None
                            dt2 = None
                            with open(fname, 'rb') as fi:
                                tags = exifread.process_file(fi)
                                flag2 = 0
                                for key in tags:
                                    if "DateTime" in key:
                                        flag2 = 1
                                        tdt = tags[key]
                                        try:
                                            dt = datetime.datetime.strptime(str(tdt), "%Y:%m:%d %H:%M:%S")
                                        except:
                                            dt = datetime.datetime.strptime("1970:01:01 00:00:00", "%Y:%m:%d %H:%M:%S")
                                if not flag2:
                                    try:
                                        dt2 = datetime.datetime.strptime(time.ctime(os.path.getctime(fname)), "%a %b %d %H:%M:%S %Y")
                                    except:
                                        dt2 = datetime.datetime.strptime("1970:01:01 00:00:00", "%Y:%m:%d %H:%M:%S")
                                    no_date += 1
                            if dt:
                                if not os.path.exists(output_dir+"/"+str(dt.year)):
                                    os.makedirs(output_dir+"/"+str(dt.year))
                                if not os.path.exists(output_dir+"/"+str(dt.year)+"/"+dt.strftime('%m')):
                                    os.makedirs(output_dir+"/"+str(dt.year)+"/"+dt.strftime('%m'))
                                if not os.path.exists(output_dir+"/"+str(dt.year)+"/"+dt.strftime('%m')+"/"+dt.strftime('%d')):
                                    os.makedirs(output_dir+"/"+str(dt.year)+"/"+dt.strftime('%m')+"/"+dt.strftime('%d'))
                                shutil.copy2(fname, output_dir+"/"+str(dt.year)+"/"+dt.strftime('%m')+"/"+dt.strftime('%d')+"/"+dt.strftime('%H')+dt.strftime('%M')+dt.strftime('%S')+"_"+str(uuid.uuid4().get_hex().upper()[0:6])+ext)
                            elif dt2:
                                if not os.path.exists(output_dir+"/no_exif"):
                                    os.makedirs(output_dir+"/no_exif")
                                if not os.path.exists(output_dir+"/no_exif/"+str(dt2.year)):
                                    os.makedirs(output_dir+"/no_exif/"+str(dt2.year))
                                if not os.path.exists(output_dir+"/no_exif/"+str(dt2.year)+"/"+dt2.strftime('%m')):
                                    os.makedirs(output_dir+"/no_exif/"+str(dt2.year)+"/"+dt2.strftime('%m'))
                                if not os.path.exists(output_dir+"/no_exif/"+str(dt2.year)+"/"+dt2.strftime('%m')+"/"+dt2.strftime('%d')):
                                    os.makedirs(output_dir+"/no_exif/"+str(dt2.year)+"/"+dt2.strftime('%m')+"/"+dt2.strftime('%d'))
                                shutil.copy2(fname, output_dir+"/no_exif/"+str(dt2.year)+"/"+dt2.strftime('%m')+"/"+dt2.strftime('%d')+"/"+dt2.strftime('%H')+dt2.strftime('%M')+dt2.strftime('%S')+"_"+str(uuid.uuid4().get_hex().upper()[0:6])+ext)
                if not flag:
                    untouched_files.append(root+"/"+f)
    with open(output_dir+"/ignored.txt", 'w') as f:
        for uf in untouched_files:
            f.write(uf+"\n")
    print
    print
    print "copied", no_date, "with no exif data"
    print "ignored", len(untouched_files), "non-photo files"
    print "found", num_photos, "photos"
    print "only", len(hashes), "photos were unique"
    print num_photos-len(hashes), "duplicates were not copied"
    print

if __name__ == "__main__":
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = u"."
    output_dir = "phresh_output"
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    else:
        print "output directory '"+output_dir+"' already exists!"
        sys.exit()
    clean_photos(path, output_dir)
