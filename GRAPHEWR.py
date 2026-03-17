import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog

def read_file(filename: str) -> list[list[str]]:
    """
    Reads the given file and puts all lines that are associated with an individual getting a check in a list, split by
    spaces.
    :param filename: name of the file to read
    :return: list of lines associated with an individual getting a check in a list
    """
    with open(filename, 'r') as f:
        lines = list()
        for line in f.readlines():
            # e.g. [time] (Team #1) player sent...
            line = line.split(" ")
            if len(line) >= 3 and line[2] == "(Team":
                lines.append(line)
    return lines

def format_check_timeline(log: list[list[str]], debug: bool = False) -> dict[str, list[str]]:
    """
    Takes a list of lines (already split) from the log where someone is getting a check and formats them into a
    dictionary where the key is the player name and the value is a list of times when the player got a check.
    :param log: list of lines associated with an individual getting a check in a list
    :param debug: pass true to print debug messages
    :return: dictionary where keys are player names and values are the times when the player got a check
    """
    players = dict()
    for check in log:
        time = check[0][1:] + " " + check[1][:-6]
        player = check[4]
        if not (player in players):
            players[player] = []
        players[player].append(time)
        if debug:
            print(player + " got a check at " + time)
    return players

def series_array(size: int) -> list[int]:
    """
    Creates a list of the given size containing values 1 to size.
    :param size: the size of the list
    :return: a list of values 1 to size, incrementing by 1
    """
    new_arr = list()
    for i in range(1, size + 1):
        new_arr.append(i)
    return new_arr

def percent_array(size: int) -> list[float]:
    """
    Creates a list of the given size containing percentages in proportion to the size (e.g. the first value would be
    (1/size) * 100).
    :param size: the size of the list
    :return: a list of percentages in proportion to the size relative to the index
    """
    new_arr = list()
    for i in range(1, size + 1):
        new_arr.append((i/size)*100)
    return new_arr

def graph(players: dict[str, pd.DatetimeIndex], y_label: str, y_constructor: function) -> None:
    """
    Create a line graph of some statistic against time, categorized by player (each key in the dictionary).
    :param players: the dictionary of player names and times
    :param y_label: string to be shown on the y-axis
    :param y_constructor: function by which to plot the data on the y axis
    :return: None
    """
    plt.figure()

    for label, series in players.items():
        plt.plot(series, y_constructor(series), label=label, drawstyle='steps-post')

    plt.xlabel("Time")
    plt.ylabel(y_label)
    plt.legend()
    plt.xticks(rotation=45)

    plt.show()

def select_file() -> str:
    """
    Opens a file dialog with Tkinter and returns the full path as a string.
    :return: The full path of the selected file as a string
    """
    root = tk.Tk()
    root.withdraw()

    path = filedialog.askopenfilename(
        title="Select a log file",
        initialdir=".",
        filetypes=(
            ("Text files", "*.txt"),
            ("All files", "*")
        )
    )

    root.destroy

    if path:
        return path
    else:
        return ""

def main():
    debug = False
    players = None
    help_string = "-- 'f' to set a file to read from\n-- '1' for quantity graph\n-- '2' for percentage graph\n-- 'h' to print this message again\n-- 'q' to exit"
    print(help_string)
    while True:
        choice = input()
        if choice == "debug":
            if debug:
                debug = False
                print("Debug is now false")
            else:
                debug = True
                print("Debug is now true")
        elif choice == "f": # Select file to read from
            try:
                checks = read_file(select_file())
                players = format_check_timeline(checks, debug)

                for player in players:
                    players[player] = pd.to_datetime(players[player])
                print("File set")
            except FileNotFoundError:
                print("File not found")
            except Exception as e:
                print("Unexpected Error: ", e)
        elif choice == "1": # Quantity graph
            if players is None:
                print("Set a file to read from first")
            else:
                graph(players, "Amount of Checks", lambda x: series_array(len(x)))
        elif choice == "2": # Percentage graph
            if players is None:
                print("Set a file to read from first")
            else:
                graph(players, "Percentage of Checks Completed", lambda x: percent_array(len(x)))
        elif choice == "h": # Print help message
            print(help_string)
        elif choice == "q": # Quit
            break
        else:
            print("Invalid input")

if __name__ == '__main__':
    main()
