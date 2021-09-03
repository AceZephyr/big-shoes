# Big Shoes

Big Shoes is a standalone Final Fantasy 7 stepgraph viewer written in Python.

## Installation

Download or pull this repository.

If you don't have Python installed, the easiest way to get it is from the [Microsoft Store](https://www.microsoft.com/en-us/p/python-39/9p7qfqmjrfp7).

Double click _setup_python.bat to install necessary packages.

## Usage

Double click _run_big_shoes.bat to run Big Shoes.

### Connecting to FF7

To connect to an emulator, go to Connect > Connect to Emulator.

Select the emulator process and process ID from the first two boxes. Click "Show This Window" to make sure the correct process is being referred to. Make sure to select the correct version on the rightmost box.

To connect to the PC version, go to Connect > Connect to PC. If FF7 PC is running, it will connect.

To disconnect from FF7, go to Connect > Disconnect

### Stepgraph

View the stepgraph with Window > Toggle Stepgraph

Use the mouse wheel to move left or right. Shift + scroll to scroll faster. Ctrl + scroll to change the y-axis danger scale.

Keys:
- P: Toggle preemptive stepids
- Ctrl+P: Toggle preemptive battle checks
- X: Toggle extrapolation lines
- M: Toggle encounter marks
- R: Reset Step Position
- D: Reset Danger Scaling

### Formation Extrapolator

Window > Formation Extrapolator.

This window displays the next 10 battle formations on this field.

### Formation List

Window > List Formation Types.

This window lists the possible formations on this field.

## Compatability

Big Shoes is compatible with:

- FF7 PC Steam Version
- BizHawk 2.3.2 to 2.6.2
- Retroarch
- PSXFin v1.13

## To Do

Considering Linux support.

Settings window.