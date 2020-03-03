# NightWindows

## Purpose

The Natural Sounds and Night Skies division of the National Park Service uses scientific equipment to measure the amount of anthropogenic light cast into the night sky in parks across the country. To do this, the sun must be more than 18° below the horizon, and the moon must be set. This is most common on or around the new moon, but there are other periods of several hours of observable time outside of this. This program solves this problem by giving all available observation windows of a specified time in the desired location.

## Downloading NightWindows
To use the NightWindows class, you must first clone the [solunar](https://github.com/kevinboone/solunar_cmdline) repository and compile it via directions listed in the associated readme file. 
After cloning the NightWindows repository, it is important that *both NightWindows and solunar are in the same folder.* This way when linking a root folder, the program knows where to find all useful information.

## Using the NightWindows Class

Objects created with the NightWindows class are initialized with five objects:

- The first day of your desired window
- the final day of your desired window
- the coordinates of your location as a tuple, **OR** the 4-letter NPS code
- minimum number of hours a window must be
- a boolean on if you would like a printout of the windows in your console

Examples:

```
Denali = NightWindows(dt.datetime(2019, 9, 1), dt.datetime(2020, 4, 1), "DENA", 3, True)
Shenandoah = NightWindows(dt.datetime(2020, 1, 1), dt.datetime(2021, 1, 1), (38.53, -118.68), 4, False)
```

*Note: if entering a 4-letter NPS code, this will use the **centerpoint** of this park. If more specificity is needed, please use the coordinates as a tuple*

Once initialized, using the method GetWindows will run computations and save data to a text file, naming it according to the time it was created

```
>>>Shenandoah.GetWindows()
There are 178 possible windows for the selected range
Processing Complete
```
You can also use method DateRange to receive the number of days your window encapsulates

```
>>>Shenandoah.DateRange()
datetime.timedelta(days=366)
```

## Public Domain

This project is in the worldwide public domain.

> This projet is in the public domain within the United States,
> and copyright adn related rights in the world worlwide are waived through the 
> [CC0 1.0 Universal public domain dedication](https://creativecommons.org/publicdomain/zero/1.0/).
>
> All contributions to this project will be released under the CC0 dedication.
> By submitting a pull request, you are agreeing to comply with this waiver of copyright interest.
