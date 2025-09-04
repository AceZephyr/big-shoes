# Big Shoes

Big Shoes is a standalone Final Fantasy 7 stepgraph viewer written in Python.

## Installation and Usage

You can now run this as a standalone application. Download the latest release, and run big_shoes.exe. Note that big_shoes.exe must be in this folder to work properly (it has to find some files), but you can make a shortcut to it.

To build as a standalone application, you will need `pyinstaller`. Simply run `pyinstaller main_window.spec` to build `big_shoes.exe` in the `dist` folder.

### Connecting to FF7

To connect to an emulator, go to Connect > Connect to Emulator.

Select the emulator process and process ID from the first two boxes. Click "Show This Window" to make sure the correct process is being referred to. Make sure to select the correct version on the rightmost box.

To connect to the PC version, go to Connect > Connect to PC. If FF7 PC is running, it will connect.

To disconnect from FF7, go to Connect > Disconnect

### Watches

View watches with Window > Watches

### Stepgraph

View the stepgraph with Window > Stepgraph

Use the mouse wheel to move left or right. Shift + scroll to scroll faster. Ctrl + scroll to change the y-axis danger scale. Alt + scroll to show more or less of the graph at a time.
### Formation Extrapolator

Window > Formation Extrapolator.

This window displays the next 10 battle formations on this field.

### Formation List

Window > List Formation Types.

This window lists the possible formations on this field.

## Compatability

Big Shoes is compatible with:

- FF7 PC Steam Version
- DuckStation (requires manual address search)
- BizHawk 2.3.2 to 2.7 and 2.9.1 (Octoshock core, not Nymashock)
- Retroarch
- PSXFin v1.13