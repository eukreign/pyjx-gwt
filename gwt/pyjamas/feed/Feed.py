from pyjamas.Timer import Timer
from __pyjamas__ import doc, JS
from pyjamas import DOM

frameId = 0

class Feed:

    def __init__(self, url, callback):
        global frameId
        frame = DOM.createElement("iframe")
        frameid = "__pygwt_feedFrame%d" % frameId
        frameId += 1
        DOM.setAttribute(frame, "id", frameid)
        DOM.setAttribute(frame, "src", url)
        #DOM.setStyleAttribute(frame, 'width', '0')
        #DOM.setStyleAttribute(frame, 'height', '0')
        #DOM.setStyleAttribute(frame, 'border', '0')
        #DOM.setStyleAttribute(frame, 'position', 'absolute')
        self.frameId = frameId
        self.frame = frame
        self.timer = Timer(notify=self)
        doc().parent.body.appendChild(frame)
        self.callback = callback
        self.timer.scheduleRepeating(100)

    def getFrameTxt(self):
        return str(self.frame.contentWindow.document.body.innerHTML)

    def onTimer(self, *args):
        txt = self.getFrameTxt()
        if txt == '':
            return
        self.callback(self, txt)
        self.timer.cancel()
