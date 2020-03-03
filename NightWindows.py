

import os
from subprocess import Popen, PIPE
import sys
import datetime as dt
import numpy as np
import pandas as pd
from timezonefinder import TimezoneFinder

class NightWindows(object):

    '''
    The purpose of this class is to find all of the possible viewing window times
    in a given period of time designated by the user.

    Initializing parameters
    -----------------------

    start (datetime): the first day of your sample window that you would like to calulate 

    end (datetime): the last day of your sample window that you would like to calculate

    coords (tuple OR string): tuple in format (lat, long) or 4-letter park code (ex: 'DENA')
    to select midpoint of selcted park

    hours (int): consecutive hours of observable time to determine a window (default=3)

    printout (bool): if True, will print times of every viewing window in console (default=False)

    '''

    def __init__(self, start, end, coords, hours, printout):
        self.start = start
        self.end = end
        self.coords = coords
        self.hours = hours
        self.printout = printout

    def GetWindows(self):
        return self.WindowFinder(
            self.start,
            self.end,
            self.coords,
            self.hours,
            self.printout)
        # prints out number of observable windows in range, writes to a file
        # specified by user

    # returns numbers of days in initialized range
    def DateRange(self):
        return self.end - self.start


    @staticmethod
    def WindowFinder(startdate, enddate, coords, hours=3, printout=False):
        
        # This points to directly above the folder that the file is in
        rootpath = (os.path.dirname(os.path.realpath(sys.argv[0])))
        
        def regions(condition):
            d = np.diff(condition)
            idx, = d.nonzero()
            idx += 1

            if condition[0]:
                idx = np.r_[0, idx]

            if condition[-1]:
                idx = np.r_[idx, condition.size]

            idx.shape = (-1, 2)

            return idx

        # Create a list of all dates in specified range
        listofdates = []
        currentdate = startdate
        while currentdate <= enddate:
            listofdates.append(currentdate)
            currentdate += dt.timedelta(days=1)

        # Create an empty numpy array SunMoonTimes to then populate with data
        SunMoonTimes = np.empty((len(listofdates), 6), dtype=object)

        # If coords is a string, open CentroidLatLongs, find park associated
        # with 4-letter code, and use this as coords tuple value
        if isinstance(coords, str):
            # Points to the folder containing text file
            df = pd.read_csv(rootpath + os.sep + "NightWindows\CentroidLatLongs.txt")
            df = df.sort_values("UNIT_NAME")
            df = df.drop_duplicates("UNIT_CODE")
            park = df.loc[df['UNIT_CODE'] == coords]
            long = park["POINT_X"].values.item()
            lat = park["POINT_Y"].values.item()
            coords = (lat, long)

        # Finds the time zone of the specified location to change from UTC to local 
        # time at the end of the function
        timezones = {"Pacific/Saipan" : 10,
             "Pacific/Honolulu" : -10,
             "America/Anchorage" : -9,
             "America/Los_Angeles" : -8,
             "America/Denver" : -7,
             "America/Phoenix": -7,
             "America/Chicago" : -6,
             "America/New_York" : -5,
             "America/St_Thomas" : -4}
        tf = TimezoneFinder()
        tz = tf.timezone_at(lng=coords[1], lat=coords[0])
        timediff = int(timezones[tz])

        # Run solunar script for every date in range and save times to
        # SunMoonTimes
        index = 0
        for i in listofdates:
            date_of_interest = i
            fmt_date = dt.datetime.strftime(date_of_interest, '%d/%m/%Y %H:%M')

            command = "solunar -f -l {0},{1} -d {2} --utc".format(
                coords[0], coords[1], fmt_date.lower())

            # Points to local copy of solunar
            os.chdir(rootpath + os.sep + "solunar_cmdline")

            process = Popen(command, stdout=PIPE, stderr=PIPE)
            stdout, stderr = process.communicate()
            values = stdout.decode().split("\n")

            # Find values for times in output "values", excepting cases where there is no moonrise, moonset,
            # or astronomical twilight -- these values are in HH:MM format

            # Some days have no moonrise or moonset - value starts at None, is
            # checked for below
            Moonrisetime = None
            try:
                Moonrisetime = dt.datetime.strptime(
                    [x for x in values if 'Moonrise' in x][0][-5:], '%H:%M')
            except IndexError:
                pass

            Moonsettime = None
            try:
                Moonsettime = dt.datetime.strptime(
                    [x for x in values if 'Moonset' in x][0][-5:], '%H:%M')
            except IndexError:
                pass

            # In Northern latitudes, some days have no astronomical twilight -
            # value is checked for below
            Astro1time = None     # Beginning of astronomical twilight, typically in morning
            try:
                Astro1time = dt.datetime.strptime(
                    [x for x in values if 'Astronomical twilight starts' in x][0][-5:], '%H:%M')
            except ValueError:
                pass

            Astro2time = None     # End of astronomical twilight, typically in evening
            try:
                Astro2time = dt.datetime.strptime(
                    [x for x in values if 'Astronomical twilight ends' in x][0][-5:], '%H:%M')
            except ValueError:
                pass
            # Sun always rises and sets in a day
            Sunrisetime = dt.datetime.strptime(
                [x for x in values if 'Sunrise' in x][0][-5:], '%H:%M')
            Sunsettime = dt.datetime.strptime(
                [x for x in values if 'Sunset' in x][0][-5:], '%H:%M')

            # Turn HH:MM format into datetime of current day for sun, moon, and
            # astronomical twilights
            Sunrise = i + \
                dt.timedelta(hours=Sunrisetime.hour, minutes=Sunrisetime.minute)
            Sunset = i + dt.timedelta(hours=Sunsettime.hour,
                                      minutes=Sunsettime.minute)

            try:
                Moonrise = i + \
                    dt.timedelta(hours=Moonrisetime.hour, minutes=Moonrisetime.minute)
            except AttributeError:
                Moonrise = None

            try:
                Moonset = i + \
                    dt.timedelta(hours=Moonsettime.hour, minutes=Moonsettime.minute)
            except AttributeError:
                Moonset = None

            if Astro1time is None:
                Astro1 = None
            else:
                Astro1 = i + \
                    dt.timedelta(hours=Astro1time.hour, minutes=Astro1time.minute)

            if Astro2time is None:
                Astro2 = None
            else:
                Astro2 = i + \
                    dt.timedelta(hours=Astro2time.hour, minutes=Astro2time.minute)

            # Save values to current day, proceed to next day
            SunMoonTimes[index] = [
                Sunrise, Sunset, Moonrise, Moonset, Astro1, Astro2]
            index += 1

        # Initalize lists and variables from input values
        first = startdate
        end = enddate
        Sunlist = []
        Moonlist = []
        Endlist = []
        dayindex = 0
        current = first
        nextday = first + dt.timedelta(days=1)
        timeslist = []

        # For every minute, check and write the value of if the sun, moon, and
        # both are in favorable positions
        while current < end:

            # When the time is equal to the next day, change index of
            # SunMoontimes to correct day
            if current == nextday:
                dayindex += 1
                nextday += dt.timedelta(days=1)

            usingday = SunMoonTimes[dayindex]

            # ASTRO TWILIGHT CALCULATIONS

            # Case 1: There is no Night on this day
            if usingday[4] is None or usingday[5] is None:
                Sunlist.append(0)

            # Case 2: Astronomical twilight begins in the morning and ends in
            # the evening (typical day)
            elif usingday[4] < usingday[5]:
                if current < usingday[4] or current > usingday[5]:
                    Sunlist.append(1)
                else:
                    Sunlist.append(0)

            # Case 3: Astronomical twilight from previous day ends in morning,
            # then begins for mornings AFTER
            elif usingday[4] > usingday[5]:
                if current > usingday[5] and current < usingday[4]:
                    Sunlist.append(1)
                else:
                    Sunlist.append(0)

            # MOON CALCULATIONS

            # Case 1: Moon starts set, rises, DOES NOT reset (usingday[3] =
            # None)
            if usingday[3] is None:
                if current < usingday[2]:
                    Moonlist.append(1)
                else:
                    Moonlist.append(0)

            # Case 2: Moon starts risen, sets, DOES NOT re-rise (usingday[2] =
            # None)
            elif usingday[2] is None:
                if current > usingday[3]:
                    Moonlist.append(1)
                else:
                    Moonlist.append(0)

            # Case 3: Moon starts set, then rises, then sets again
            elif usingday[2] < usingday[3]:
                if current < usingday[2] or current > usingday[3]:
                    Moonlist.append(1)
                else:
                    Moonlist.append(0)

            # Case 4: Moon starts risen, then sets, then rises again
            else:
                if current > usingday[3] and current < usingday[2]:
                    Moonlist.append(1)
                else:
                    Moonlist.append(0)

            # FINAL CALCULATIONS
            if Sunlist[-1] == 1 and Moonlist[-1] == 1:
                Endlist.append(1)
            else:
                Endlist.append(0)

            # Add time to timelist, then advance by one minute and repeat
            # process
            timeslist.append(current)
            current += dt.timedelta(minutes=1)

        # Once lists are formed, convert to numpy arrays
        timeslist = np.array(timeslist)
        # Account for time zone difference as calculated before
        timeslist += dt.timedelta(hours=timediff)
        Sunlist = np.array(Sunlist)
        Moonlist = np.array(Moonlist)
        Endlist = np.array(Endlist)

        # Use function regions to find start and end times of windows, then
        # subtract one from final value to avoid IndexError
        goodtimes = regions(Endlist)
        goodtimes[-1][1] = goodtimes[-1][1] - 1

        # Check if time between start and end is more than target hours, add to
        # list if True
        bestlist = []
        for i in goodtimes:
            if timeslist[i[1]] - timeslist[i[0]
                                           ] >= dt.timedelta(seconds=(3600 * hours)):
                bestlist.append(i)

        print("There are " + str(len(bestlist)) +
              " possible windows for the selected range\nProcessing Complete")

        # Check for value of printout in intiailization; if true, print times
        # in console
        if printout:
            for i in bestlist:
                print("A window opens at " +
                      str(timeslist[i[0]]) +
                      " and closes at " +
                      str(timeslist[i[1]]))

        # Write times into a text file, path and name should be changed for
        # each user
        calctime = dt.datetime.strftime(dt.datetime.now(), "%Y%m%d_%H%M%S")
        with open(rootpath + os.sep + "NightWindows\WindowTimes_" + calctime + ".txt", 'w+') as f:
            for i in bestlist:
                f.write(str(timeslist[i[0]]) + "\t" +
                        str(timeslist[i[1]]) + " \n")
