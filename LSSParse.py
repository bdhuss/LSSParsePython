from sys import exit, argv
from os.path import exists
from getopt import getopt, GetoptError


def main(argv):
    input_filename = ""
    output_filename = ""
    try:
        opts, args = getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except GetoptError:
        print("LSSParse.py -i <input_file> -o <output_file>")
        exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("LSSParse.py -i <input_file> -o <output_file>")
            exit(1)
        elif opt in ("-i", "--ifile"):
            input_filename = arg.lstrip()
        elif opt in ("-o", "--ofile"):
            output_filename = arg.lstrip()

    if not exists(input_filename):
        print(f"ERROR: Incorrect command syntax, or in file does not exist.")
        print("SYNTAX: LSSParse.py -i <input_file> -o <output_file>")
        exit(1)

    if exists(output_filename):
        overwrite_confirm = input(f"{output_filename} already exists. Do you want to overwrite it? (Y/N): ")
        if overwrite_confirm.upper() == "N":
            print("User chose not to overwrite existing file.")
            exit(1)

    print(f">Starting processing of {input_filename}...")

    with open(input_filename) as in_file:
        line = in_file.readline()
        output_file = open(output_filename, "w")
        team_standings_flag = False
        recap_flag = False
        team_roster_flag = False

        while line:
            if line.startswith("#Team Standings"):
                team_standings_flag = True
                output_file.write(
                    "Place,#,Team Name,%Won,Points Won,Points Lost,Y-T-D % Won,Y-T-D Won,Y-T-D Lost,Games Won,Scratch Pins,Pins +HDCP\n")
                print(f">> HEADER LINE --> Team Standings")
                line = in_file.readline()

            elif line.startswith("#Recap"):
                team_standings_flag = False
                recap_flag = True
                output_file.write(
                    "Lanes,Team Name,HDCP 1,HDCP 2,HDCP 3,HDCP Total,Points Won,,Team Name,HDCP 1,HDCP 2,HDCP 3,HDCP Total,Points Won\n")
                print(f">> HEADER LINE --> Recap")
                line = in_file.readline()

            elif line.startswith("#Team Rosters"):
                team_roster_flag = True
                recap_flag = False
                print(f">> HEADER LINE --> Team Rosters")
                line = in_file.readline()

            else:
                str_split = line.split(" ")

                if team_standings_flag:
                    name_str = ""
                    name_completed = False

                    for x in range(len(str_split)):
                        if x < 2:  # first two indexes will be placement & team number
                            output_file.write(f"{str_split[x]},")

                        elif x == 2:  # third index will be the start of the team name
                            name_str = str_split[x]

                        else:
                            if name_completed:
                                if "??" in str_split[x]:  # we don't want "??" symbols
                                    temp_str = str_split[x].replace("??", ".5")
                                    output_file.write(f",{temp_str}")
                                else:
                                    output_file.write(f",{str_split[x]}")

                            else:
                                name_completed, name_str = parse_name(name_str, str_split[x])

                                if name_completed:
                                    output_file.write(f"{name_str},{str_split[x]}")

                    print(f">Team Standings: {name_str}")
                    line = in_file.readline()

                elif recap_flag:
                    second_name_flag = False
                    name1 = ""

                    for x in range(len(str_split)):
                        if x == 0:  # first split will be lane assignments
                            output_file.write(f"{str_split[x]}")
                            name_completed = False
                            name_str = ""

                        elif x == 1:  # second split is the start of team #1's name
                            name_str = str_split[x]

                        elif second_name_flag:  # start of second teams name
                            name_str = str_split[x]
                            second_name_flag = False

                        else:
                            if str_split[x] == "<--->":  # the string BLS uses "vs"
                                name1 = name_str
                                name_completed = False
                                second_name_flag = True
                                name_str = ""
                                output_file.write(f",{str_split[x]}")

                            elif name_completed:
                                output_file.write(f",{str_split[x]}")

                            else:
                                name_completed, name_str = parse_name(name_str, str_split[x])

                                if name_completed:
                                    output_file.write(f",{name_str},{str_split[x]}")

                    print(f">Team Match-up: {name1} <---> {name_str}")
                    line = in_file.readline()

                elif team_roster_flag:
                    if str_split[1] == "-":  # this signifies current line is a team name, not a players details
                        name_str = ""

                        for x in range(len(str_split)):
                            # This line should always be in the same order
                            # Example: <TEAM_#> - <NAME_OF_TEAM>
                            match x:
                                case 0: output_file.write(str_split[x])
                                case 1: output_file.write(",")
                                case 2: name_str = str_split[x]
                                case _: name_str = f"{name_str} {str_split[x]}"

                        output_file.write(name_str)
                        print(f">Team Roster: {name_str}")

                    else:
                        name_str = ""
                        name_completed = False
                        empty_games = True

                        if len(str_split) >= 14:  # typical case
                            for x in range(len(str_split)):
                                if x == 0:  # Bowler ID
                                    output_file.write(str_split[x])

                                elif x == 1:  # start of player name
                                    name_str = str_split[x]

                                else:
                                    if name_completed:
                                        output_file.write(f",{str_split[x]}")

                                    else:
                                        name_completed, name_str = parse_name(name_str, str_split[x])

                                        if name_completed:
                                            output_file.write(f",{name_str},{str_split[x]}")

                            print(f">#{str_split[0]}: {name_str}")

                        elif len(str_split) >= 11:  # bowler did not bowl on current week
                            for x in range(len(str_split)):
                                if x == 0:  # Bowler ID
                                    output_file.write(str_split[x])

                                elif x == 1:  # start of player name
                                    name_str = str_split[x]
                                    if name_str == "VACANT":  # this VACANT is always the same
                                        output_file.write(f",{name_str},120,124,0,0,,,v120,v120,v120,360,672\n")
                                        break

                                else:
                                    if name_completed:
                                        if str_split[x] == "0" and empty_games:
                                            for y in range(4):  # empty games
                                                output_file.write(",")

                                            output_file.write(str_split[x])
                                            empty_games = False

                                        else:
                                            output_file.write(f",{str_split[x]}")

                                    else:
                                        name_completed, name_str = parse_name(name_str, str_split[x])

                                        if name_completed:
                                            output_file.write(f",{name_str},{str_split[x]}")

                            print(f">#{str_split[0]}: {name_str}")

                        elif len(str_split) >= 9:  # usually an additional roster member that has no recorded games
                            output_file.write(str_split[0])
                            name_str = str_split[1]
                            loop_pos = 2

                            while not name_completed:
                                name_completed, name_str = parse_name(name_str, str_split[loop_pos])
                                loop_pos += 1

                            output_file.write(f",{name_str},{str_split[loop_pos-1]},{str_split[loop_pos]},0,0,,,,,,0,0\n")
                            print(f"#{str_split[0]}: {name_str}")

                        else:
                            print(f"> ERROR: Unknown number of parse elements on line: {str_split}")

                    line = in_file.readline()

                else:
                    print(f"> ERROR: Unknown category for line: {str_split}")

    output_file.close()
    print("\n>> LSSParse complete!")


def parse_name(name_str, split_str):
    try:
        if split_str.startswith("bk"):
            split_str = split_str.replace("bk", "")  # remove preceding "bk" from averages

        float(split_str)  # if it's not a float, the name has yet to be completed
        return True, name_str

    except ValueError:  # if parse attempt fails, assume name is not yet complete
        temp_str = f"{name_str} {split_str}"
        return False, temp_str


if __name__ == "__main__":
    main(argv[1:])
