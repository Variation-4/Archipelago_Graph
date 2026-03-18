import os
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog

#--CONSTANTS--##############################################
HELP_STRING = ("-- 'f' to set a file to read from\n"
               "  -'f full' to see full file path\n"
               "-- '1' for quantity graph\n"
               "-- '2' for percentage graph\n"
               "-- 'h' to print this message again\n"
               "-- 'q' to exit")
############################################################

#TODO Add documentation
class Log:
    def __init__(self, players, filepath, filename):
        self.players = players
        self.filepath = filepath
        self.filename = filename

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

def array(size: int, f) -> list[int | float]:
    """
    Creates a list of the given size containing values dependent on a given function (f(index)).
    :param size: the size of the list
    :param f: function by which to create the contents of the generated list
    :return: a list of values
    """
    new_arr = list()
    for i in range(1, size + 1):
        new_arr.append(f(i))
    return new_arr

#TODO Update documentation
def graph(logs: list[Log], y_label: str, y_constructor) -> None:
    """
    Create a line graph of some statistic against time, categorized by player (each key in the dictionary).
    :param logs:
    :param selection:
    :param y_label: string to be shown on the y-axis
    :param y_constructor: function by which to plot the data on the y-axis using the DateTimeIndex as a parameter
    :return: None
    """
    console_clear()
    print("Select files to graph (e.g. '0 1 3'):")
    for i in range(len(logs)):
        print(i, "|", logs[i].filename)
    selection = input()
    selection = selection.split(" ")

    plt.figure()

    #TODO If there are multiple logs, use relative time instead of fixed
    for i in selection:
        log = logs[int(i)]
        players = log.players
        for label, series in players.items():
            plt.plot(series, y_constructor(series), label=label + (" | " + log.filename if len(selection) > 1
                                                                   else ""), drawstyle='steps-post')
    plt.xlabel("Time")
    plt.ylabel(y_label)
    plt.legend()
    plt.xticks(rotation=45)

    plt.show()
    console_clear()
    print(HELP_STRING)

def select_file() -> str:
    """
    Opens a file dialog with Tkinter and returns the full path as a string.
    :return: The full path of the selected file as a string
    """
    root = tk.Tk()
    root.attributes("-topmost", True)
    root.attributes("-alpha", 0)

    path = filedialog.askopenfilename(
        title="Select a log file",
        initialdir=".",
        filetypes=(
            ("Text files", "*.txt"),
            ("All files", "*")
        )
    )

    root.destroy()

    if path:
        return path
    else:
        return ""

#TODO Add documentation
def file_menu(logs, full, debug: bool = False):
    while True:
        console_clear()
        print("Files selected:\n"
              "remove [i] | remove the file from consideration\n"
              "add        | add a new file\n"
              "q          | close this menu\n")
        for i in range(len(logs)):
            print(i, "|", logs[i].filename, ("(" + logs[i].filepath + ")") if full else "")
        choiceF = input()
        if choiceF[:6] == "remove":
            try:
                logs.pop(int(choiceF[7:]))
            except ValueError:
                print("Invalid selection - not a number")
            except IndexError:
                print("Invalid selection - invalid index")
            except Exception as e:
                print("Unexpected error:", e)
        elif choiceF == "add":
            try:
                file = select_file()
                print(file)
                checks = read_file(file)
                players = format_check_timeline(checks, debug)

                for player in players:
                    players[player] = pd.to_datetime(players[player])

                filename = file.split("/")[-1]
                logs.append(Log(players, file, filename))
                print("File set")
            except FileNotFoundError:
                print("File not found")
            except Exception as e:
                print("Unexpected Error: ", e)
        elif choiceF == "q":
            console_clear()
            print(HELP_STRING)
            break
        else:
            print("Invalid input")

def console_clear() -> None:
    """
    Clears the console window
    :return: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')

#TODO Add more debug stuff
def main():
    debug = False
    logs = []
    print(HELP_STRING)
    while True:
        choice = input()
        if choice == "debug": # Toggle debug
            if debug:
                debug = False
                print("Debug is now false")
            else:
                debug = True
                print("Debug is now true")
        elif choice[0] == "f": # Select file to read from
            file_menu(logs, choice[2:] == "full", debug)
        elif choice == "1": # Quantity graph
            if len(logs) == 0:
                print("Set a file to read from first")
            else:
                graph(logs, "Amount of Checks", lambda x: array(len(x), lambda y: y))
        elif choice == "2": # Percentage graph
            if len(logs) == 0:
                print("Set a file to read from first")
            else:
                graph(logs, "Percentage of Presently Completed Checks", lambda x: array(len(x),
                                                                                           lambda y: (y/len(x) * 100)))
        elif choice == "h": # Print help message
            print(HELP_STRING)
        elif choice == "q": # Quit
            break
        else:
            print("Invalid input")

if __name__ == '__main__':
    console_clear()
    main()