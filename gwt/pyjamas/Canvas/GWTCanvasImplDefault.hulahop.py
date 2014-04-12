def cvt(s):
    if isinstance(s, str):
        return unicode(s)
    return s

class GWTCanvasImplDefault:

    def createElement(self):
        e = DOM.createElement("CANVAS")
        try:
            # This results occasionally in an error:
            # AttributeError: XPCOM component '<unknown>' has no attribute 'MozGetIPCContext'
            self.setCanvasContext(e.MozGetIPCContext(u'2d'))
        except AttributeError:
            # In which case this seems to work:
            self.setCanvasContext(e.getContext('2d'))
        return e


