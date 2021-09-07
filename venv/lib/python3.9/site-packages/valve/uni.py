
import unicodedata

ignored_characters = [
    "\n",
    "\t",
    " ",
    "\"",
]
# ignored_characters = [
#     "\n"
# ]
regions = []  # [start, stop], ...
region = [0, 0]

ignore = False
crange = 0x110000
# crange = 50
for point in range(crange):
    character = chr(point)
    character_ignored = character in ignored_characters

    if character_ignored:
        if not ignore:
            region[1] = point - 1
            ignore = True
    else:
        if ignore:
            ignore = False
            regions.append(region)
            region = [point, point]

    name = unicodedata.name(character, "<unknown>").ljust(50)
    point_hex = hex(point)[2:].upper().rjust(4, "0")
    # print(point_hex, '-' if character_ignored else ' ', name, repr(character))
region[1] = point
regions.append(region)


print()
print()
for index, (start, stop) in enumerate(regions):
    if index:
        print(" / ", end="")
    hex_start = "%x" + hex(start)[2:].upper().rjust(2, "0")
    hex_stop = "%x" + hex(stop)[2:].upper().rjust(2, "0")
    if hex_start == hex_stop:
        print(hex_start, end="")
    else:
        print(hex_start + "-" + hex_stop, end="")
print()
