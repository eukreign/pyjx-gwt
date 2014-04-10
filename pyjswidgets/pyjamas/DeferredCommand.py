from pyjamas.Timer import Timer

deferredCommands = []
timerIsActive = False


def add(cmd):
    deferredCommands.append(cmd)
    maybeSetDeferredCommandTimer()


def flushDeferredCommands():
    for i in range(len(deferredCommands)):
        current = deferredCommands[0]
        del deferredCommands[0]
        if current:
            if hasattr(current, "execute"):
                current.execute()
            else:
                current()


def maybeSetDeferredCommandTimer():
    global timerIsActive

    if (not timerIsActive) and (not len(deferredCommands) == 0):
        Timer(1, onTimer)
        timerIsActive = True


def onTimer(t):
    global timerIsActive

    flushDeferredCommands()
    timerIsActive = False
    maybeSetDeferredCommandTimer()


