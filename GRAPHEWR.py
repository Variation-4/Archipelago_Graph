import os
import matplotlib.pyplot as plt
import pandas as pd
import tkinter as tk
from tkinter import filedialog

#--CONSTANTS--##############################################
HELP_STRING = ("-- 'f' to open log file manager\n"
               "  - 'f add' to add a log file\n"
               "    - 'f add <path>' to add a log file manually\n"
               "  - 'f full' to see full file path\n"
               "-- '1' for quantity graph\n"
               "-- '2' for percentage graph\n"
               "-- 'e' to export data from the first log to .csv\n"
               "  - 'e [i]' to export data from log i to .csv\n"
               "  - 'e [i] <path>' to export data from log i to a specified location\n"
               "-- 'h' to print this message again\n"
               "-- 'q' to exit")
FILE_MENU_STRING = ("Files selected:\n"
                    "remove [i] | remove the file from consideration\n"
                    "add        | add a new file\n"
                    "add <path> | add the file at <path>\n"
                    "q          | close this menu\n")
############################################################

class Log:
    """
    Class to represent a log file
    """
    def __init__(self, players: dict[str, pd.Series], filepath: str, filename: str, timestamps: list[pd.Timestamp]):
        """
        Constructor for the Log class
        :param players: dictionary of players with their times in which they completed a check
        :param filepath: the filepath of the log
        :param filename: the name of the file
        :param timestamps: ordered list of all check timestamps in the log file
        """
        self.players = players
        self.players_relative = dict() #possibly somehow add documentation regarding this
        self.filepath = filepath
        self.filename = filename
        self.timestamps = timestamps

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

def format_check_timeline(log: list[list[str]], debug: bool = False) -> tuple[dict[str, pd.Series], list[pd.Timestamp]]:
    """
    Takes a list of lines (already split) from the log where someone is getting a check and formats them into a
    dictionary where the key is the player name and the value is a list of times when the player got a check. Also returns
    an ordered list of every timestamp that appears in the list.
    :param log: list of lines associated with an individual getting a check in a list
    :param debug: print debug messages (default False)
    :return: dictionary where keys are player names and values are the times when the player got a check and list of every timestamp
    """
    players = dict()
    timestamps = []
    for check in log:
        time = check[0][1:] + " " + check[1][:-2]
        player = check[4]
        if not (player in players):
            players[player] = []
        players[player].append(time)
        timestamps.append(pd.to_datetime(time, format="%Y-%m-%d %H:%M:%S,%f"))
        if debug:
            print(player + " got a check at " + time)
    
    for player in players:
            players[player] = pd.to_datetime(players[player], format="%Y-%m-%d %H:%M:%S,%f")

    return players, timestamps

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

def time_convert(arr: pd.Series, oldest: pd.Timestamp) -> list[float]:
    """
    Creates and returns a list of times that represent the delta between the given oldest time and each time in the
    given list.
    :param arr: the list containing times
    :param oldest: the oldest time to pivot the rest off of
    :return: a list of delta-times in minutes
    """
    new_arr = list()
    for i in range(len(arr)):
        new_arr.append((arr[i] - oldest).total_seconds()/60)
    return new_arr

def graph(logs: list[Log], y_label: str, y_constructor, debug: bool = False) -> None:
    """
    Create a line graph of some statistic against time, categorized by player (each key in the dictionary).
    Player will be prompted with which logs to graph out of the given. If one is selected, time will be formatted
    directly as it exists (when the player got the check), otherwise, time will be formatted relative to the oldest
    time-stamp (minutes since the start).
    :param logs: the list of logs to consider
    :param y_label: string to be shown on the y-axis
    :param y_constructor: function by which to plot the data on the y-axis using the DateTimeIndex as a parameter
    :param debug: print debug messages (default False)
    :return: None
    """
    if len(logs) == 0:
        print("Set a file to read from first")
        return

    if len(logs) == 1: # Skip selection if only one log is loaded
        selection = {0}
    else:
        console_clear()
        print("Select files to graph (e.g. '0 1 3') (c to cancel):")
        for i in range(len(logs)):
            print(i, "|", logs[i].filename)
        while True:
            invalid = False
            selection = input()
            if selection == "c":
                show_help()
                return
            selection = selection.split(" ")
            try:
                for i in range(len(selection)):
                    selection[i] = int(selection[i])
                for i in selection:
                    if i < 0 or i >= len(logs):
                        print("Invalid selection")
                        invalid = True
                if not invalid:
                    break
            except ValueError:
                print("Invalid selection")
        selection = set(selection)

    # If there is more than one selection, populate the players_relative entries for each log
    if len(selection) > 1:
        for i in selection:
            oldest = None
            players = logs[i].players
            for player in players:
                for time in players[player]:
                    if oldest is None or time < oldest:
                        oldest = time
            if debug:
                print("oldest time for", logs[i].filename +  ":", oldest)
            for player in players:
                logs[i].players_relative[player] = time_convert(players[player], oldest)

    plt.figure()

    for i in selection:
        log = logs[i]
        if debug:
            print("graphing", log.filename)
        players = log.players_relative if len(selection) > 1 else log.players
        for label, series in players.items():
            plt.plot(series, y_constructor(series), label=label + (" | " + log.filename if len(selection) > 1
                                                                   else ""), drawstyle='steps-post')
    plt.xlabel("Time")
    plt.ylabel(y_label)
    plt.legend()
    plt.xticks(rotation=45)

    plt.show()
    show_help()

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

def add_file(path: str | None, logs: list[Log], debug: bool = False) -> None:
    """
    Opens a file dialog and adds selected log file to the specified Log list.
    :param path: path of file to be added to logs
    :param logs: the list of logs to add or remove Logs from
    :param debug: print debug messages (default False)
    :return: None
    """
    if not path:
        path = select_file()

    try:
        if debug:
            print("Reading file:", path)
            input("Press ENTER to continue")
        checks = read_file(path)
        players, timestamps = format_check_timeline(checks, debug)

        filename = path.split("/")[-1]
        log = Log(players, path, filename, timestamps)
        if debug:
            print("Created Log:", log.filename, "(", log, ")")
            input("Press ENTER to continue")
        logs.append(log)
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print("Unexpected Error: ", e)

def file_menu(logs: list[Log], full: bool, debug: bool = False) -> None:
    """
    Instantiates an interface with which to select files (add or remove for consideration).
    :param logs: the list of logs to add or remove Logs from
    :param full: if the full file path should be listed instead of the file name
    :param debug: print debug messages (default False)
    :return: None
    """

    def file_menu_message() -> None:
        """
        Prints the text interface for this menu
        :return: None
        """
        console_clear()
        print(FILE_MENU_STRING)
        for i in range(len(logs)):
            print(i, "|", logs[i].filename, ("(" + logs[i].filepath + ")") if full else "")


    file_menu_message()
    while True:
        choice = input().split(" ")
        if choice[0] == "remove":
            try:
                rm_log = logs.pop(int(choice[1]))
                if debug:
                    print("Removed log:", rm_log.filename, "(", rm_log, ")")
                    input("Press ENTER to continue")
                file_menu_message()
            except ValueError:
                print("Invalid selection - not a number")
            except IndexError:
                print("Invalid selection - invalid index")
            except Exception as e:
                print("Unexpected error:", e)
        elif choice[0] == "add":
            if len(choice) > 1:
                add_file(" ".join(choice[1:]), logs, debug)
            else:
                add_file(None, logs, debug)
            file_menu_message()
        elif choice[0] == "q":
            show_help()
            break
        else:
            print("Invalid input")

def export(log_i: int, path: str | None, logs: list[Log]) -> None:
    """
    Exports the data from a log into a .csv file. Only supports exploring a single log.
    :param log_i: Index of the log to export
    :param path: Path of the exported file. Set None to open a file dialog.
    :param logs: Master list of logs to reference from
    :return: None
    """

    if len(logs) == 0:
        print("Set a file to read from first")
        return
    
    if not path: # Opens file dialog if path not specified
        root = tk.Tk()
        root.attributes("-topmost", True)
        root.attributes("-alpha", 0)

        path = filedialog.asksaveasfilename(
            title="Export to...",
            initialdir=".",
            filetypes=(
                ("Comma Separated Values", "*.csv"),
                ("All files", "*")
            )
        )

        if path[-4:] != ".csv":
            path += ".csv"

        root.destroy()

    try:
        with open(path, "w") as file:
            content = "Timestamps, " # Content starts with the first column "Timestamps"

            # Exporting is limited to one log file at a time because of how timestamps are stored.
            # Multiple exports could be merged later in external software.
            log = logs[log_i]

            # Tracks location count for each player individually during content generation so players
            # can have data points even when they don't contribute
            current_checks = dict()

            for player, series in log.players.items():
                current_checks[player] = 0
                content += player + ", "

            content += "\n"

            for timestamp in log.timestamps: # Create a new line for each timestamp chronologically
                content += timestamp.strftime("%Y-%m-%d %X.%f") + ", " # Formats time for easy Excel importing; Different from log format
                for player, series in log.players.items():
                    # Checks if given timestamp is a timestamp where that player checked a location.
                    # Could cause issues if 2 players check a location on the same millisecond.
                    if timestamp in series:
                        current_checks[player] += 1
                    content += str(current_checks[player]) + ", "
                content += "\n"

            file.write(content)
            print(f"Successfully wrote from log {log.filepath} to {path}")
    except FileNotFoundError:
        print("File not found")
    except Exception as e:
        print("Unexpected Error: ", e)

def console_clear() -> None:
    """
    Clears the console window.
    :return: None
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def show_help() -> None:
    """
    Clears the console window and show the help string.
    :return: None
    """
    console_clear()
    print(HELP_STRING)

def main():
    debug = False
    logs = []
    show_help()
    while True:
        choice = input().split(" ")
        if choice[0] == "debug": # Toggle debug
            if debug:
                debug = False
                print("Debug is now false")
            else:
                debug = True
                print("Debug is now true")
        elif choice[0] == "f": # Select file to read from
            if len(choice) >= 2 and choice[1] == "add":
                if len(choice) >= 3:
                    add_file(" ".join(choice[2:]), logs, debug)
                else:
                    add_file(None, logs, debug)
            else:
                file_menu(logs, choice[1] == "full" if len(choice) > 1 else False, debug)
        elif choice[0] == "1": # Quantity graph
            graph(logs, "Amount of Checks", lambda x: array(len(x), lambda y: y), debug)
        elif choice[0] == "2": # Percentage graph
            graph(logs, "Percentage of Presently Completed Checks", lambda x: array(len(x),
                                                                                    lambda y: (y/len(x) * 100)), debug)
        elif choice[0] == "e":
            if len(choice) >= 2:
                if len(choice) >= 3:
                    export(int(choice[1]), " ".join(choice[2:]), logs)
                else:
                    export(int(choice[1]), None, logs)
            else:
                export(0, None, logs)
        elif choice[0] == "h": # Print help message
            show_help()
        elif choice[0] == "q": # Quit
            break
        else:
            print("Invalid input")

if __name__ == '__main__':
    main()