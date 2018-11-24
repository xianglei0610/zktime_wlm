#coding=utf-8
# dump python dict to ini format file
# Author: limodou (limodou@gmail.com)
# Copyleft BSD
# you can see http://wiki.woodpecker.org.cn/moin/Dict4Ini for more details
# and the new source project is in http://code.google.com/p/dict4ini/
#
# Updates:
# 0.9.2-----------------------
#   2007/07/03
#     Add clear method
#     Added encryption code thanks to Mayowa Akinyemi
#     using the secretKey parameter will encrypt the values using
#     Paul Rubin's p3.py encryption module
#     using the hideData parameter will perform base64 enc/dec of the values
# 0.9.1-----------------------
#   2007/06/26
#     Fix float convert bug
# 0.9-------------------------
#   2007/06/13
#     Thanks for Victor Stinner giving a output format patch, so you can define your own
#     output format "%s = %s" to anything you want, for example "%s=%s" or "%s:%s". And 
#     Dict4Ini will auto remove '%s' from the fromat string, and the strip() the rest of 
#     the string, then use it to split the key and value in Ini file. For example, if you 
#     using "%s:%s", Dict4Ini will get "%s:%s".replace('%s', '').strip(), then use ':' to 
#     split the line.
# 0.8-------------------------
#   2007/04/20
#     Add exception process when parsing file
#     Add BOM detect
# 0.7-------------------------
#   2007/04/19
#     Fix '\' escape
# 0.6-------------------------
#   2006/01/18
#     Fix ordereditems bug.
# 0.5-------------------------
#   2006/01/04
#     Add ordereditems() method, so you can get the items according the ini file definition
#   2005/12/30
#     Support onelevel parameter, you can set it True, than only one level can be used, so that
#        the key can include section delimeter char in it.
#     Support sectiondelimeter parmeter, you can set the section delimeter to which you want
# 0.4-------------------------
#   2005/12/12
#     Fixed "\" bug in option's value
#   2005/12/09
#     Adding dict() method, then you can change the DictIni object to dict type
#   2005/10/16
#     Saving the order of the items
#     Adding float format
#

__version__ = '0.9'

import sys
import locale
import os.path
import re

section_delimeter = '/'

import base64
try:
    import p3 as crypt
except:
    crypt = None
    
class DictNode(object):
    def __init__(self, values, encoding=None, root=None, section=[], orders=[], sectiondelimeter=section_delimeter, onelevel=False, format="%s = %s"):
        self._items = values
        self._orders = orders
        self._encoding = encoding
        self._root = root
        self._section = section
        self._section_delimeter = sectiondelimeter
        self._onelevel = onelevel
        self._format = format

    def __getitem__(self, name):
        if self._items.has_key(name):
            value = self._items[name]
            if isinstance(value, dict):
                return DictNode(value, self._encoding, self._root, self._section + [name], sectiondelimeter=self._section_delimeter, onelevel=self._onelevel, format=self._format)
            else:
                return value
        else:
            self._items[name] = {}
            self._root.setorder(self.get_full_keyname(name))
            return DictNode(self._items[name], self._encoding, self._root, self._section + [name], sectiondelimeter=self._section_delimeter, onelevel=self._onelevel, format=self._format)

    def __setitem__(self, name, value):
        if self._section_delimeter and self._section_delimeter in name:
            if self._onelevel:
                sec = name.split(self._section_delimeter, 1)
            else:
                sec = name.split(self._section_delimeter)
            obj = self._items

            _s = self._section[:]
            for i in sec[:-1]:
                _s.append(i)
                if obj.has_key(i):
                    if isinstance(obj[i], dict):
                        obj = obj[i]
                    else:
                        obj[i] = {} #may lost some data
                        obj = obj[i]
                else:
                    obj[i] = {}
                    self._root.setorder(self._section_delimeter.join(_s))
                    obj = obj[i]
            obj[sec[-1]] = value
            self._root.setorder(self._section_delimeter.join(_s + [sec[-1]]))
        else:
            self._items[name] = value
            self._root.setorder(self.get_full_keyname(name))

    def __delitem__(self, name):
        if self._items.has_key(name):
            del self._items[name]

    def __repr__(self):
        return repr(self._items)

    def __getattr__(self, name):
        return self.__getitem__(name)

    def __setattr__(self, name, value):
        if name.startswith('_'):
            if name == '_comment':
                self._root._comments[self._section_delimeter.join(self._section)] = value
            else:
                self.__dict__[name] = value
        else:
            self.__setitem__(name, value)

    def comment(self, name, comment):
        if name:
            self._root._comments[self._section_delimeter.join(self._section + [name])] = comment
        else:
            self._root._comments[self._section_delimeter.join(self._section)] = comment

    def __delattr__(self, name):
        if self._items.has_key(name):
            del self._items[name]

    def __str__(self):
        return repr(self._items)

    def __len__(self):
        return len(self._items)

    def has_key(self, name):
        return self._items.has_key(name)

    def items(self):
        return self._items.items()

    def setdefault(self, name, value):
        return self._items.setdefault(name, value)

    def get(self, name, default=None):
        return self._items.get(name, default)

    def keys(self):
        return self._items.keys()

    def values(self):
        return self._items.values()

    def get_full_keyname(self, key):
        return self._section_delimeter.join(self._section + [key])

    def ordereditems(self, values, sec=[]):
        s = []
        for key, value in values.items():
            s.append((self._root._orders.get(self._section_delimeter.join(sec + [key]), 99999), key, value))
        s.sort()
        return [(x, y) for z, x, y in s]
    
    def clear(self):
        self._items = {}
        self._orders = []
        self._section = []

class DictIni(DictNode):
    def __init__(self, inifile=None, values=None, encoding=None, commentdelimeter='#', sectiondelimeter=section_delimeter, onelevel=False, format="%s = %s", hideData=False, secretKey=None):
        self._items = {}
        self._inifile = inifile
        self._root = self
        self._section = []
        self._commentdelimeter = commentdelimeter
        self._comments = {}
        self._orders = {}
        self._ID = 1
        self._encoding = getdefaultencoding(encoding)
        self._section_delimeter = sectiondelimeter
        self._format = format
        self._secretKey = secretKey
        self._hideData = hideData
        assert not self
        if not self._section_delimeter:
            raise Exception, "section_delimeter cann't be empty!"
        self._onelevel = onelevel
        if values is not None:
            self._items = values

        if self._inifile and os.path.exists(self._inifile):
            self.read(self._inifile, self._encoding)

    def setfilename(self, filename):
        self._inifile = filename

    def getfilename(self):
        return self._inifile

    def save(self, inifile=None, encoding=None):
        if inifile is None:
            inifile = self._inifile

        if isinstance(inifile, (str, unicode)):
            f = file(inifile, 'w')
        elif isinstance(inifile, file):
            f = inifile
        else:
            f = inifile

        if not f:
            f = sys.stdout

        if encoding is None:
            encoding = self._encoding

        f.write(self._savedict([], self._items, encoding))
        if isinstance(inifile, (str, unicode)):
            f.close()

    def _savedict(self, section, values, encoding):
        if values:
            buf = []
            default = []
            for key, value in self.ordereditems(values, sec=section):
                if isinstance(value, dict):
                    sec = section[:]
                    sec.append(key)
                    buf.append(self._savedict(sec, value, encoding))
                else:
                    c = self._comments.get(self._section_delimeter.join(section + [key]), '')
                    if c:
                        lines = c.splitlines()
                        default.append('\n'.join(['%s %s' % (self._commentdelimeter, x) for x in lines]))

                    default.append(self._format % (key, self.uni_str(value, encoding)))
            if default:
                buf.insert(0, '\n'.join(default))
                buf.insert(0, '[%s]' % self._section_delimeter.join(section))
                c = self._comments.get(self._section_delimeter.join(section), '')
                if c:
                    lines = c.splitlines()
                    buf.insert(0, '\n'.join(['%s %s' % (self._commentdelimeter, x) for x in lines]))
            return '\n'.join(buf + [''])
        else:
            return ''

    def dict(self):
        return self._dict(self)

    def _dict(self, v):
        if isinstance(v, tuple):
            return tuple([self._dict(x) for x in v])
        elif isinstance(v, list):
            return [self._dict(x) for x in v]
        elif isinstance(v, (dict, DictNode)):
            d = {}
            for key, value in v.items():
                d[key] = self._dict(value)
            return d
        else:
            return v

    def read(self, inifile=None, encoding=None):
        if inifile is None:
            inifile = self._inifile

        if isinstance(inifile, (str, unicode)):
            try:
                f = file(inifile, 'r')
            except:
                return  #may raise Exception is better
        elif isinstance(inifile, file):
            f = inifile
        else:
            f = inifile

        if not f:
            f = sys.stdin

        if encoding is None:
            encoding = self._encoding

        comments = []
        section = ''
        for lineno, line in enumerate(f.readlines()):
            try:
                if lineno == 0:
                    if line.startswith('\xEF\xBB\xBF'):
                        line = line[3:]
                        encoding = 'utf-8'
                line =  line.strip()
                if not line: continue
                if line.startswith(self._commentdelimeter):
                    comments.append(line[1:].lstrip())
                    continue
                if line.startswith('['):    #section
                    section = line[1:-1]
                    #if comment then set it
                    if comments:
                        self.comment(section, '\n'.join(comments))
                        comments = []
                    continue
                key, value = line.split(self._format.replace('%s', '').strip(), 1)
                key = key.strip()
                value = self.process_value(value.strip(), encoding)
                if section:
                    self.__setitem__(section + self._section_delimeter + key, value)
                    #if comment then set it
                    if comments:
                        self.__getitem__(section).comment(key, '\n'.join(comments))
                        comments = []
                else:
                    self.__setitem__(key, value)
                    #if comment then set it
                    if comments:
                        self.comment(key, '\n'.join(comments))
                        comments = []
            except Exception, err:
                import traceback
                traceback.print_exc()
                print 'Error in [line %d]%s:' % (lineno, line)
                print line
        if isinstance(inifile, (str, unicode)):
            f.close()

    def setorder(self, key):
        if not self._orders.has_key(key):
            self._orders[key] = self._ID
            self._ID += 1
            
    def clear(self):
        self._items = {}
        self._section = []
        self._comments = {}
        self._orders = {}
        
    def process_value(self, value, encoding=None):
        value = self.protect_value(value, 1)
        
        length = len(value)
        t = value
        i = 0
        r = []
        buf = []
        listflag = False
        while i < length:
            if t[i] == '"': #string quote
                buf.append(t[i])
                i += 1
                while t[i] != '"' or (t[i] == '"' and t[i-1] == '\\'):
                    buf.append(t[i])
                    i += 1
                buf.append(t[i])
                i += 1
            elif t[i] == ',':
                r.append(''.join(buf).strip())
                buf = []
                i += 1
                listflag = True
            elif t[i] == 'u':
                buf.append(t[i])
                i += 1
            else:
                buf.append(t[i])
                i += 1
                while i < length and t[i] != ',':
                    buf.append(t[i])
                    i += 1
        if buf:
            r.append(''.join(buf).strip())
        result = []
        for i in r:
            if i.isdigit():
                result.append(int(i))
            elif i and i.startswith('u"'):
                result.append(unicode(unescstr(i[1:]), encoding))
            else:
                try:
                    b = float(i)
                    result.append(b)
                except:
                    result.append(unescstr(i))
    
        if listflag:
            return result
        elif result:
            return result[0]
        else:
            return ''
    
    def protect_value(self, value, mode=0):
        if mode == 0:
            # encrypt
            if crypt != None and self._secretKey != None :
                cipher = crypt.p3_encrypt(value, self._secretKey)
                return base64.b64encode(cipher)
            elif self._hideData is True:
                return base64.b64encode(value)
        else:
            # decrypt
            if crypt != None and self._secretKey != None :
                cipher = base64.b64decode(value)
                return crypt.p3_decrypt(cipher, self._secretKey)
            elif self._hideData is True:
                return base64.b64decode(value)

        return value
    
    def uni_str(self, a, encoding=None):
        return self.protect_value(uni_prt(a, encoding))
    
    
unescapechars = {'"':'"', 't':'\t', 'r':'\r', 'n':'\n', '\\':'\\', 'a':'\a', 'f':'\f', 
    "'":"'", 'b':'\b', 'v':'\v'}
def unescstr(value):
    if value.startswith('"') and value.endswith('"') or value.startswith("'") and value.endswith("'"):
        s = []
        i = 1
        end = len(value) - 1
        while i < end:
            if value[i] == '\\' and unescapechars.has_key(value[i+1]):
                s.append(unescapechars[value[i+1]])
                i += 2
            else:
                s.append(value[i])
                i += 1
        value = ''.join(s)
    return value

def escstr(value):
    s = []
    for c in value:
        if c == "'":
            s.append(c)
            continue
        v = repr(c).replace('"', r'\"')
        if '\\' in v and ord(c)<128:
            if isinstance(c, str):
                s.append(v[1:-1])
            else:
                s.append(v[2:-1])
        else:
            s.append(c)
    return ''.join(s)

def uni_prt(a, encoding=None):
    s = []
    if isinstance(a, (list, tuple)):
        for i, k in enumerate(a):
            s.append(uni_prt(k, encoding))
            s.append(',')
    elif isinstance(a, str):
        t = escstr(a)
        if (' ' in t) or (',' in t) or ('"' in t) or t.isdigit() or ('\\' in t):
            s.append('"%s"' % t)
        else:
            s.append("%s" % t)
    elif isinstance(a, unicode):
        t = escstr(a)
        s.append('u"%s"' % t.encode(encoding))
    else:
        s.append(str(a))

    return ''.join(s)

def getdefaultencoding(encoding):
    if not encoding:
        encoding = locale.getdefaultlocale()[1]
    if not encoding:
        encoding = sys.getfilesystemencoding()
    if not encoding:
        encoding = 'utf-8'
    return encoding

if __name__ == '__main__':
    d = DictIni('t.ini', format="%s:%s", secretKey='mayowa')
    print d
    d._comment = 'Test\nTest2'
    d.a = 'b'
    d.b = 1
    d['b'] = 3
    d.c.d = (1,2,'b asf "aaa')
    d['s']['t'] = u'中国'
    d['s'].a = 1
    d['m/m'] = 'testing'
    d['p'] = r'\?'
    d.t.m.p = '3'
    print d
    d.save()

    d = DictIni('t.ini', format="%s:%s", secretKey='mayowa')
    print d.p

    d = DictIni('t2.ini', format="%s:%s", hideData=True)
    d.p.a = '1'
    d.p.b = '2'
    d.save()

    d = DictIni('t2.ini', format="%s:%s", hideData=True)
    print d.p.a
    print d.p.b

