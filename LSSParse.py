from sys import exit, argv
from os.path import exists
from getopt import getopt, GetoptError


def main(argv):
    input_filename = ""
    output_filename = ""
    try:
        opts, args = getopt(argv, "hi:o:", ["ifile=", "ofile="])
    except GetoptError:
        print("lssRead.py -i <input_file> -o <output_file>")
        exit(2)

    for opt, arg in opts:
        if opt == "-h":
            print("lssRead.py -i <input_file> -o <output_file>")
            exit(1)
        elif opt in ("-i", "--ifile"):
            input_filename = arg.lstrip()
        elif opt in ("-o", "--ofile"):
            output_filename = arg.lstrip()

    if not exists(input_filename):
        print(f"ERROR: {input_filename} does not exists.")
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
                            if not name_completed:
                                # As of creation, no team name includes numbers beyond their first index
                                try:
                                    temp_float = float(str_split[x])
                                    name_completed = True
                                    output_file.write(f"{name_str},{temp_float}")

                                except ValueError:
                                    name_str = f"{name_str} {str_split[x]}"

                            else:
                                half_str = "½"  # need to catch ½ symbols and replace with a .5
                                if half_str in str_split[x]:
                                    temp_str = str_split[x].replace(half_str, ".5")
                                    output_file.write(f",{temp_str}")
                                else:
                                    output_file.write(f",{str_split[x]}")

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
                            if not name_completed:
                                # As of creation, no team name includes numbers beyond their first index
                                try:
                                    temp_int = int(str_split[x])
                                    name_completed = True
                                    output_file.write(f",{name_str},{temp_int}")

                                except ValueError:
                                    name_str = f"{name_str} {str_split[x]}"

                            elif str_split[x] == "<--->":  # the break between first and second team
                                name1 = name_str
                                name_completed = False
                                second_name_flag = True
                                name_str = ""
                                output_file.write(f",{str_split[x]}")

                            else:
                                output_file.write(f",{str_split[x]}")

                    print(f">Team Match-up: {name1} <---> {name_str}")

                    line = in_file.readline()

                elif team_roster_flag:
                    if str_split[1] == "-":  # this signifies current line is a team name, not a players details
                        name_str = ""

                        for x in range(len(str_split)):
                            if x == 0:  # first split is team number
                                output_file.write(str_split[x])

                            elif x == 1:  # second split is ignored
                                output_file.write(",")

                            elif x == 2:  # third split is start of team name
                                name_str = str_split[x]

                            else:
                                name_str = f"{name_str} {str_split[x]}"

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
                                    if not name_completed:
                                        try:
                                            if str_split[x].startswith("bk"):  # catches book avg vs established avg
                                                temp_var = str_split[x].replace("bk", "")
                                                temp_int = int(temp_var)
                                                output_file.write(f",{name_str},{temp_int}")
                                                name_completed = True

                                            else:  # normal average
                                                temp_int = int(str_split[x])
                                                output_file.write(f",{name_str},{temp_int}")
                                                name_completed = True

                                        except ValueError:
                                            name_str = f"{name_str} {str_split[x]}"

                                    else:
                                        output_file.write(f",{str_split[x]}")

                            print(f">#{str_split[0]}: {name_str}")

                        elif len(str_split) >= 11:  # bowler did not bowl on current week
                            for x in range(len(str_split)):
                                if x == 0:  # Bowler ID
                                    output_file.write(str_split[x])

                                elif x == 1:  # start of player name
                                    name_str = str_split[x]
                                    if name_str == "VACANT":  # this VACANT is always the same
                                        output_file.write(f",{name_str},120,124,0,0,,,120,120,120,360,672\n")
                                        break

                                else:
                                    if not name_completed:
                                        try:
                                            if str_split[x].startswith("bk"):  # catches book avg vs established avg
                                                temp_var = str_split[x].replace("bk", "")
                                                temp_int = int(temp_var)
                                                output_file.write(f",{name_str},{temp_int}")
                                                name_completed = True

                                            else:  # normal average
                                                temp_int = int(str_split[x])
                                                output_file.write(f",{name_str},{temp_int}")
                                                name_completed = True

                                        except ValueError:
                                            name_str = f"{name_str} {str_split[x]}"

                                    else:
                                        if str_split[x] == "0" and empty_games:
                                            for y in range(4):  # empty games
                                                output_file.write(",")

                                            output_file.write(str_split[x])
                                            empty_games = False

                                        else:
                                            output_file.write(f",{str_split[x]}")

                            print(f">#{str_split[0]}: {name_str}")

                        elif len(str_split) >= 9:  # usually an additional roster member that has no recorded games
                            output_file.write(str_split[0])
                            name_str = str_split[1]
                            loop_pos = 2

                            while not name_completed:
                                try:
                                    if str_split[loop_pos].startswith("bk"):
                                        temp_var = str_split[loop_pos].replace("bk", "")
                                        temp_int = int(temp_var)
                                        output_file.write(f",{name_str},{temp_int}")
                                        name_completed = True

                                    else:
                                        temp_int = int(str_split[loop_pos])
                                        output_file.write(f",{name_str}, {temp_int}")
                                        name_completed = True

                                except ValueError:
                                    name_str = f"{name_str} {str_split[loop_pos]}"
                                    loop_pos += 1

                            output_file.write(f",{str_split[loop_pos + 1]},0,0,,,,,,0,0\n")

                            print(f"#{str_split[0]}: {name_str}")

                        else:
                            print(f"> ERROR: Unknown number of parse elements on line: {str_split}")

                    line = in_file.readline()

                else:
                    print(f"> ERROR: Unknown category for line: {str_split}")

    output_file.close()
    print("\n\n>> LSSParse complete!")


if __name__ == "__main__":
    main(argv[1:])
