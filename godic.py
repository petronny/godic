#!/bin/python3
import sys
import urllib.request
from urllib.parse import quote
import re

class Colorizing(object):
    colors = {
            'none': '',
            'default': '\033[0m',
            'bold': '\033[1m',
            'underline': '\033[4m',
            'blink': '\033[5m',
            'reverse': '\033[7m',
            'concealed': '\033[8m',

            'black': '\033[30m',
            'red': '\033[31m',
            'green': '\033[32m',
            'yellow': '\033[33m',
            'blue': '\033[34m',
            'magenta': '\033[35m',
            'cyan': '\033[36m',
            'white': '\033[37m',

            'on_black': '\033[40m',
            'on_red': '\033[41m',
            'on_green': '\033[42m',
            'on_yellow': '\033[43m',
            'on_blue': '\033[44m',
            'on_magenta': '\033[45m',
            'on_cyan': '\033[46m',
            'on_white': '\033[47m',

            'beep': '\007',
            }

    @classmethod
    def colorize(cls, s, colors=None):
        if type(colors)==str:
            colors=[colors]
        for color in colors:
            if color in cls.colors:
                s='{0}{1}{2}'.format(cls.colors[color], s, cls.colors['default'])
        return s

query=sys.argv[1]
url='http://www.godic.net/dicts/de/'+quote(query)
_c=Colorizing.colorize

html=urllib.request.urlopen(url).read().decode('utf-8')
#html=re.sub(r'<img[^>]*>','',html)
html=html.replace('\r','')

word=re.search(r'<span class="word">([^<]*)</span>', html)
if word:
    word=word.group(1)
    word=word.replace('&#228;','ä')
    word=word.replace('&#252;','ö')
    word=word.replace('&#252;','ü')
    word=word.replace('&#223;','ß')
    word=word.replace('&#196;','Ä')
    word=word.replace('&#214;','Ö')
    word=word.replace('&#220;','Ü')
    print(_c(word, 'bold'), end=' ')

phonitic_sep=re.search(r'<span class="Phonitic-Sep">(.*?)</span>', html)
if phonitic_sep:
    phonitic_sep=phonitic_sep.group(1)
    while len(phonitic_sep)>0:
        u=re.search(r'^<u>([^<]*)</u>', phonitic_sep)
        b=re.search(r'^<b>([^<]*)</b>', phonitic_sep)
        other=re.search(r'^([^<]*)<', phonitic_sep)
        if u:
            print(_c(u.group(1),['underline', 'green']), end='')
            phonitic_sep=phonitic_sep[len(u.group()):]
            continue
        if b:
            print(_c(b.group(1),['bold', 'green']), end='')
            phonitic_sep=phonitic_sep[len(b.group()):]
            continue
        if other:
            print(_c(other.group(1),'green'), end='')
            phonitic_sep=phonitic_sep[len(other.group(1)):]
            continue
        if not u and not b:
            break
    print(' ', end='')

phonitic=re.search(r'<span class="Phonitic">([^<]*)</span>', html)
if phonitic:
    print(phonitic.group(1))
else:
    print()

html=html[html.find('<div id="translate">'):]
html=html[:html.find('<p class="explain-word-info">')]

while True:
    cara=re.search(r'<span class="?cara"?>([^<]*)</span>', html)
    expHead=re.search(r'<div class="expHead">(.*?)</div>', html, re.S)
    exp=re.search(r'<span class="?exp"?>(.*?)</span>', html)
    exp2=re.search(r'<p class="exp">(.*?)</p>', html)
    line=re.search(r'<p class="line">(.*?)</p>', html)
    eg=re.search(r'<span class=eg>(.*?)(</span>|<!--eg-->)', html)
    phrase=re.search(r'<span id="phrase">(.*?)</span>', html)
    greytxt=re.search(r'<span class="greytxt">(.*?)</span>', html)
    br=re.search(r'(<BR>|</span>|</div>|<span>)(.*?)(<BR>|</div>|<span|</span>)', html)
    a=re.search(r'<a href="/dicts/de/[^"]*">([^<]*)</a>', html)
    matches=[cara, expHead, exp, exp2, line, eg, phrase, greytxt, br, a]
    first=len(html)
    match=None
    for i in matches:
        if not i:
            continue
        if i==br:
            if first > i.regs[0][1]-1:
                first=i.regs[0][1]-1
                match=i
        else:
            if first > i.regs[0][0]:
                first=i.regs[0][0]
                match=i
    if not match:
        break
    if match==cara:
        print(_c(cara.group(1), ['bold', 'cyan']))
    elif match==expHead:
        expHead=re.sub(r'<[^>]*>','',re.sub(r'[\r\n]','',expHead.group(1)))
        if expHead=='德语例句库':
            break
        print()
        print(_c(expHead,['bold', 'magenta']))
    elif match==exp or match==exp2:
        print('  '+re.sub(r'<span class="key">([^<]*)</span>',_c('\\1', ['bold', 'red']), match.group(1)))
    elif match==eg:
        print('    '+_c(re.sub(r'</?i>', '', eg.group(1)).replace('<br>', '\n    '),['green']))
    elif match==phrase:
        print('    '+_c(re.sub(r'</?i>', '', phrase.group(1)).replace('<br>', '\n    '),['bold', 'green']))
    elif match==line:
        print('  '+re.sub(r'<span class="key">([^<]*)</span>',_c('\\1', ['bold', 'red']), match.group(1)))
    elif match==br:
        br=br.group(2)
        if len(br)>0 and br.find('<div')<0 and br.find('</p>')<0 and br.find('<!--')<0 and br.find('</a>')<0:
            print(br)
    elif match==a:
        print(a.group(1), end=',')
    else:
        print(match.group(1))
    if match==br:
        html=html[match.regs[2][1]:]
    else:
        html=html[match.regs[1][1]:]
