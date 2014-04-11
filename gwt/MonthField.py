from gwt.Calendar import DateField, Calendar
from gwt.Button import Button
from gwt.HorizontalPanel import HorizontalPanel
from gwt.Hyperlink import Hyperlink
from gwt.SimplePanel import SimplePanel

from pyjamas.locale import _

class NoDaysCalendar(Calendar):

    cancel = _("Cancel")
    monthsOfYear = [_('Jan'), _('Feb'), _('Mar'), _('Apr'), _('May'), _('Jun'),
                    _('Jul'), _('Aug'), _('Sep'), _('Oct'), _('Nov'), _('Dec')]



    def drawGrid(self,month,year):
        empty = SimplePanel()
        return empty

    def _gridShortcutsLinks(self):
        bh1 = Hyperlink(_("Current"))
        bh1.addClickListener(getattr(self, 'onToday'))

        b2 = Button(_("Choose"),self.onMonthSelected)

        bh3 = Hyperlink(self.cancel)
        bh3.addClickListener(getattr(self, 'onCancel'))


        b = HorizontalPanel()
        b.addStyleName("calendar-shortcuts")
        b.add(bh1)
        b.add(b2)
        b.add(bh3)

        self.vp.setHorizontalAlignment("center")
        b.setPadding(10)
        self.vp.add(b)

    def _gridCancelLink(self):pass


    def onMonthSelected(self,event):
        self.onDate(event,self.currentYear,self.currentMonth,1)

class MonthField(DateField):
    today_text = _("Current")

    def __init__(self):
        super(MonthField,self).__init__(format="%Y-%m")
        self.calendar = NoDaysCalendar()
        self.calendar.addSelectedDateListener(getattr(self,"onDateSelected"))

