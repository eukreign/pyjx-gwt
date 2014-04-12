# Copyright (C) 2012 Kees Bos <cornelis.bos@gmail.com>
# LISENCE : Apache 2.0 or WTFPL, choose what suits your needs
#

from gettext import NullTranslations
import re
from JSONService import loads
from HTTPRequest import HTTPRequest

try:
    from gettext import c2py
except ImportError:
    from __pyjamas__ import JS
    def c2py(plural):
        f = None
        JS('''eval("@{{f}}=function(n){return " + @{{plural}} + ";}")''')
        return f


class JSONTranslations(NullTranslations):
    re_nplurals = re.compile('nplurals *= *(\d+)')
    re_plural = re.compile('plural *= *([^;]+)')
    base_url = None
    domain = None

    def __init__(self, *args, **kwargs):
        NullTranslations.__init__(self, *args, **kwargs)
        self.new_catalog()

    def new_catalog(self, base_url=None, domain=None, lang=None):
        self._catalog = {}
        self.lang = lang
        self.plural = lambda n: int(n != 1) # germanic plural by default

    def load(self, base_url=None, domain=None, lang=None, onCompletion=None, onError=None):
        if base_url is None:
            base_url = self.base_url
        if domain is None:
            domain = self.domain
        url = base_url
        if domain is not None and lang is not None:
            url = "%s/%s_%s.json" % (url, domain, lang)
        self.new_catalog(base_url, domain, lang)
        self._onCompletion = onCompletion
        self._onError = onError
        HTTPRequest().asyncGet(url, self)

    def onCompletion(self, text):
        self.parse_json(text)
        if self._onCompletion is not None:
            self._onCompletion(text)

    def onError(self, text, code):
        if self._onError is not None:
            self._onError(text, code)
        raise RuntimeError(code)

    def onTimeout(self, text):
        pass

    def onProgress(self, event):
        pass

    def parse_json(self, text):
        json = loads(text)
        self._catalog.update(json)
        for k, v in self._catalog[""].iteritems():
            k = k.lower()
            if k == 'plural-forms':
                self.nplurals = int(self.re_nplurals.search(v).group(1))
                self.plural = c2py(self.re_plural.search(v).group(1))

    def _parse(self, url):
        self.load(url)

    def gettext(self, message):
        tmsg = self._catalog.get(message)
        if tmsg is None:
            if self._fallback:
                return self._fallback.gettext(message)
            return message
        return tmsg[0]

    def ngettext(self, msgid1, msgid2, n):
        tmsg = self._catalog.get(msgid1)
        if tmsg is None:
            if self._fallback:
                return self._fallback.ngettext(msgid1, msgid2, n)
            if self.plural(n):
                return msgid2
            return msgid1
        else:
            return tmsg[self.plural(n)]

    lgettext = gettext
    lngettext = ngettext
    ugettext = gettext
    ungettext = ngettext
