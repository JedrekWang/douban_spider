#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/3/27 0:38
# @Author  : Jedrek


import requests
from bs4 import BeautifulSoup
import json
import sys
import importlib
from collections import Counter
import jieba
from wordcloud import WordCloud
import matplotlib.pyplot as plt


def get_html_text(url):
    try:
        r = requests.get(url)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return " "


def is_chinese(s):
    rt = False
    if u"\u4e00" <= s <= u"\u9fa6":
        rt = True
    return rt


# 创建停用词list
def stop_words_list(filepath):
    stopwords = [line.strip() for line in open(filepath, 'r').readlines()]
    return stopwords


# 对句子进行分词
def seg_sentence(sentence):
    sentence_seged = jieba.cut(sentence.strip())
    stopwords = stop_words_list('stopwords.txt')  # 这里加载停用词的路径
    outstr = ''
    for word in sentence_seged:
        if word not in stopwords:
            if word != '\t':
                outstr += word
                outstr += " "
    return outstr


if __name__ == '__main__':
    subject = str(input('input subject:'))
    depth = int(input('input depth:'))
    start_url = 'https://movie.douban.com/subject/' + subject + '/comments'

    FONT_PATH = "D:\\user\\msyh_ttf\\MSYH.TTF"
    COMMENTS_PATH = "..\\file\\douban.txt"
    WORDS_PATH = "..\\file\\qingxijieguo.txt"
    WORDCOUNT_PATH = "..\\file\\wordcount.txt"
    # 将爬取的短评放入douban.txt
    with open(COMMENTS_PATH, 'wb+') as f:
        for i in range(depth):
            url = start_url + '?start=' + str(20 * i)
            html = get_html_text(url)
            soup = BeautifulSoup(html, "html.parser")
            for line in soup.find_all("p", class_=""):
                if line.string is not None:
                    line_string = line.string
                    line_string = line_string.strip()
                    line_string = line_string + "\n"
                    word = line_string[1]
                    s_unicode = is_chinese(word)
                    if s_unicode:
                        byte_string = line_string.encode(encoding="utf-8")
                        f.write(byte_string)

    # 将短评分词，并将结果放入qingxijieguo.txt
    with open(COMMENTS_PATH, 'rb+') as inputs, open(WORDS_PATH, 'wb+') as outputs:
        for line in inputs.readlines():
            line_string = bytes.decode(line, encoding="utf-8")
            line_seg = seg_sentence(line_string)  # 这里的返回值是字符串
            line_seg_byte = line_seg.encode(encoding="utf-8")
            outputs.write(line_seg_byte)
    # WordCount
    with open(WORDS_PATH, 'rb') as fr:  # 读入已经去除停用词的文件
        data = jieba.cut(bytes.decode(fr.read(), encoding='utf-8'))
    data = dict(Counter(data))
    with open(WORDCOUNT_PATH, 'wb') as fw:  # 读入存储wordcount的文件路径
        for k, v in data.items():
            string = '%s,%d\r\n' % (k, v)
            fw.write(string.encode(encoding='utf-8'))

    # 统计单词频率并生成云图
    max_arr = []
    with open(WORDS_PATH, 'rb+') as f:
        for line in f.readlines():
            line_string = bytes.decode(line, encoding='utf-8')
            arr = line_string.split(" ")
            max_arr += arr
    new_text = " ".join(max_arr)
    wordcloud = WordCloud(font_path=FONT_PATH,
                          background_color="black").generate(new_text)
    plt.imshow(wordcloud)
    plt.axis("off")
    # plt.show()
    wordcloud.to_file('..\\img\\%s.jpg' % subject)
