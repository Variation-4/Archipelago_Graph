# Archipelago Graph Utility

This is a utility script written in Python to graph completion rates of [ArchipelagoMW](https://github.com/ArchipelagoMW/Archipelago) games.

## Instructions

Open the application and select log files from an Archipelago game using `f` or `f add`. Subsequent commands will use data from this file.

### Quickstart

1. Run the program (either from the packaged `.exe` release or `GRAPHEWR.py`)
1. Open the file manager with `f`
1. Use `add` to choose a log file
1. Close the file manager with `q`
1. Use `1` to generate a quantity-based graph and `2` to generate a percentage-based graph

### Commands

|Command|Function|
|-|-|
|`f`|Opens the log file manager|
|`f full`|Opens the log file manager with full path names to each log file
|`f add`|Add a log file without opening the file manager<br>Identical to `add` in the file manager
|`f add <path>`|Adds the log file at the specified path without opening the file manager<br>Identical to `add <path>` in the file manager
|`1`|Creates a figure graphing the amount of checks each player collected over time|
|`2`|Creates a figure graphing the percentage of checks each player collected relative to their current number of checks collected over time|
|`e`|Exports data from the first log as a `.csv` file|
|`e [i]`|Exports data from log `i` as a `.csv` file|
|`e [i] <path>`|Exports data from log `i` to a specified location|
|`h`|Prints the list of commands|
|`q`|Exits the program|
|`debug`|Toggles debug mode|

### File Manager (`f`)
|Command|Function|
|-|-|
|`remove [i]`|Removes the log file, where `[i]` is the number corresponding to the file to be removed|
|`add`|Opens a file dialog to choose a log file to be added|
|`add <path>`|Adds the log file at the specified path|
|`q`|Quit the file manager and return to the main program|

## Current Limiations

- Percentage graph is based on the current number of checks collected instead of the actual amount in the player's game
- Cannot filter or modify in any way graph categories
