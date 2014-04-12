class Audio(Media):

    def __init__(self, src=None, **kwargs):
        print "create object"
        obj = DOM.createElement("OBJECT")
        DOM.setAttribute(obj, "TYPE", "application/x-mplayer2")
        DOM.setAttribute(obj, "classid",
                                "CLSID:6BF52A52-394A-11d3-B153-00C04F79FAA6")
        print "set element"
        self.setElement(obj)

        print "widget init"
        Media.__init__(self, **kwargs)

        print "setSrc"
        if src:
            self.setSrc(src)

        self.dispparam = DOM.createElement("PARAM")
        DOM.setAttribute(self.dispparam, "name", "ShowDisplay")
        DOM.setBooleanAttribute(self.dispparam, "VALUE", "false")
        self.getElement().appendChild(self.dispparam)


