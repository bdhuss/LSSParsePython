LSSParse
(League Standing Sheet Parse)

Parses a flat text file, copy & pasted, version of my bowling leage standing sheets output from CDE's BLS software to a CSV.

Current usage:
LSSParse.py -i <input_file> -o <output_file>

Parse sections, in order:
- Team Standings
- Weekly Match-ups
- Team Rosters
- League Substitutes

Replaces 1/2 symbol with .5

Maintains precurses flags ["a", "i", "v"] to recorded games
