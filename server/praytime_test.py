from praytime import *
from datetime import date

praytime = PrayTime()
praytime.adjust({"maghrib":"5 min"})
print praytime.getTimes( date(2011, 4, 5), ( 30.3559683, -97.7428307), -6, 0, '12h' )