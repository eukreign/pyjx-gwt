
class Video(Media):

    def __init__(self, src=None, **kwargs):
        obj = DOM.createElement("OBJECT")
        DOM.setAttribute(obj, "TYPE", "application/x-mplayer2")
        self.setElement(obj)

        if src:
            self.setSrc(src)

        Media.__init__(self, **kwargs)

        obj = self.getElement().object.ShowDisplay = False

    def setPoster(self, url):
        self.setStyleAttribute("background", "url(%s)" % url)

