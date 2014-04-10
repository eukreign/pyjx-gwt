
class TreeItem(UIObject):

    def createImage(self):

        self.canvas = GWTCanvas(16,16,16,16)
        return self.canvas.getCanvasElement()

    def drawImage(self, mode):
        canvas = self.canvas
        canvas.resize(16, 16)
        canvas.saveContext()
        if mode == "white": return
        canvas.setLineWidth(1)
        canvas.setStrokeStyle(Color.Color("#aaa"))
        canvas.strokeRect(4,4,8,8)
        canvas.setStrokeStyle(Color.Color("#222"))
        canvas.setLineWidth(1)
        canvas.moveTo(5,8)
        canvas.lineTo(11,8)
        if mode == "closed":
            canvas.moveTo(8,5)
            canvas.lineTo(8,11)
        canvas.stroke()
        canvas.restoreContext()

