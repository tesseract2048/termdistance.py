#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
 @author:   hty0807@gmail.com
"""
import struct
import sys
import os
import math
import tornado.web
import json
import urllib
from array import array
from time import clock

BLACK, RED, GREEN, YELLOW, BLUE, MAGENTA, CYAN, WHITE = range(8)

vec = {}
vecsize = 0

class DistanceHandler(tornado.web.RequestHandler):
    # i am doing this here for faster startup (1400% faster actually), 
    # but this may lose performance during calculation
    def __preprocess(self, vectuple):
        veclist = []
        len = float(0)
        for a in range(0, vecsize):
            len += vectuple[a] * vectuple[a]
        len = math.sqrt(len)
        for a in range(0, vecsize):
            veclist.append(vectuple[a] / len)
        return veclist

    def __calc_distance(self):
        word1 = self.get_argument('word1').encode('utf-8')
        word2 = self.get_argument('word2').encode('utf-8')
        if word1 not in vec:
            raise tornado.web.HTTPError(404)
        if word2 not in vec:
            raise tornado.web.HTTPError(404)
        m1 = self.__preprocess(vec[word1])
        m2 = self.__preprocess(vec[word2])
        len = float(0)
        dist = float(0)
        for a in range(0, vecsize):
            len += m1[a] * m1[a]
            dist += m1[a] * m2[a]
        len = math.sqrt(len)
        dist /= len
        self.write(json.dumps({'word1': word1, 'word2': word2, 'cosineDistance': dist}))
        println('word1: %s, word2: %s, cosineDistance: %f' % (word1, word2, dist), YELLOW)
    def post(self):
        self.__calc_distance()
    def get(self):
        self.__calc_distance()

def readvec(filename):
    global vecsize, vec
    println('reading vectors, this may take a few minutes...', WHITE)
    t1 = clock()
    f = open(filename, 'rb')
    meta = f.readline().split(' ')
    words = long(meta[0])
    vecsize = long(meta[1])
    println('words: %s, vecsize: %s' % (words, vecsize), WHITE)
    fmt = ''
    for i in range(0, vecsize):
        fmt += 'f'
    for i in range(0, words):
        word = ''
        while True:
            ch = f.read(1)
            if ch == ' ':
                break
            word += ch
        word = word.strip()
        vec[word] = struct.unpack_from(fmt, f.read(struct.calcsize(fmt)))
        if i % 10000 == 0:
            println('%d / %d' % (i, words), CYAN)
    f.close()
    t2 = clock()
    println('finished reading vectors, %f seconds used' % (t2 - t1), GREEN)

def startserver(port):
    println('starting http server...', WHITE)
    application = tornado.web.Application([
            (r"/distance", DistanceHandler),
            ])
    application.listen(port, "0.0.0.0")
    println('entering server loop', GREEN)
    tornado.ioloop.IOLoop.instance().start()

def println(msg, color):
    print '\x1b[1;3%sm%s\x1b[0m' % (color, msg)

if __name__ == "__main__":
    argc = len(sys.argv)
    if argc < 3:
        println('Usage: wd.py <vectors> <port>', RED)
        exit(1)
    readvec(sys.argv[1])
    startserver(sys.argv[2])
