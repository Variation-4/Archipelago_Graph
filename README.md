# Archipelago Graph Utility

This is a utility script written in Python to graph completion rates of [ArchipelagoMW](https://github.com/ArchipelagoMW/Archipelago) games.

## Instructions

Open the application and type `r` to select a log file from an Archipelago game. Subsequent commands will use data from this file.

### Commands
|Command|Function|
|-|-|
|`f`|Selects a log file to read data from|
|`1`|Creates a figure graphing the amount of checks each player collected over time|
|`2`|Creates a figure graphing the percentage of checks each player collected relative to their current number of checks collected over time|
|`h`|Prints the list of commands|
|`q`|Exits the program|

## Current Limiations

- Unable to combine multiple log files into one figure
- Percentage graph is based on the current number of checks collected instead of the actual amount in the player's game