
class Media(Widget):

    def setSrc(self, src):
        print "setSrc", src
        obj = self.getElement()
        DOM.setAttribute(obj, "URL", src)

    def setControls(self, controls):
        print "setControls", controls
        self.ctrlparam = DOM.createElement("PARAM")
        DOM.setAttribute(self.ctrlparam, "name", "ShowControls")
        DOM.setBooleanAttribute(self.ctrlparam, "VALUE",
            controls and "true" or "false")
        self.getElement().appendChild(self.ctrlparam)

#    def setStatusbar(self, statusbar):
#        print "setstatus", statusbar
#        self.statparam = DOM.createElement("PARAM")
#        DOM.setAttribute(self.statparam, "name", "ShowStatusBar")
#        DOM.setBooleanAttribute(self.statparam, "VALUE",
#            statusbar and "true" or "false")
#        self.getElement().appendChild(self.statparam)

    def setLoop(self, autorewind):
        print "autorewind", autorewind
        self.loopparam = DOM.createElement("PARAM")
        DOM.setAttribute(self.loopparam, "name", "autorewind")
        DOM.setBooleanAttribute(self.loopparam, "VALUE",
            autorewind and "true" or "false")
        self.getElement().appendChild(self.loopparam)

    def setAutoplay(self, autostart):
        print "autoplay", autostart
        self.playparam = DOM.createElement("PARAM")
        DOM.setAttribute(self.playparam, "name", "autostart")
        DOM.setBooleanAttribute(self.playparam, "VALUE",
            autostart and "true" or "false")
        self.getElement().appendChild(self.playparam)

