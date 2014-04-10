
class Timer:

    def __setTimeout(self, delayMillis):

        mf = get_main_frame()
        return mf.getDomWindow().setTimeout(self.__fire, delayMillis)

    def __clearTimeout(self,timer):
        mf = get_main_frame()
        return mf.getDomWindow().clearTimeout(timer)

    def __setInterval(self, periodMillis):
        mf = get_main_frame()
        return mf.getDomWindow().setInterval(self.__fire, periodMillis)

    __clearInterval = __clearTimeout

    # fire the timer
    def __fire(self):
        try:
            # if not repeating, remove it from the list of active timers
            if not self.__is_repeating:
                Timer.__timers.discard(self)
            self.__onTimer()
        except Exception, e:
            print_exc()

