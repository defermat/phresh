#!/usr/bin/env python

import exifread
import hashlib
import os
import sys

def md5(fname):
    hash = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash.update(chunk)
    return hash.hexdigest()

def clean_photos(path):
    exts = [".jpg",".JPG",".jpeg",".JPEG",".TIFF",".tiff",".NEF",".nef"]
    hashes = []
    photos = {}
    num_photos = 0
    untouched_files = []
    no_date = 0
    for root, dirs, files in os.walk(path):
        path = root.split('/')
        for f in files:
            if f != ".DS_Store":
                flag = 0
                for ext in exts:
                    if f.endswith(ext):
                        flag = 1
                        fname = root+"/"+f
                        print fname
                        num_photos += 1
                        h = md5(fname)
                        if not h in hashes:
                            hashes.append(h)
                            with open(fname, 'rb') as fi:
                                tags = exifread.process_file(fi)
                                flag2 = 0
                                for key in tags:
                                    if "DateTime" in key:
                                        flag2 = 1
                                        print tags[key]
                                if not flag2:
                                    no_date += 1
                        print
                if not flag:
                    untouched_files.append(root+"/"+f)
    print hashes
    for f in untouched_files:
        print f
    print no_date
    print len(untouched_files)
    print num_photos
    print len(hashes)

if __name__ == "__main__":
    if len(sys.argv) == 2:
        path = sys.argv[1]
    else:
        path = u"."
    print path
    clean_photos(path)
