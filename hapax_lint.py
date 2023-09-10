#
# WORK IN PROGRESS -- DO NOT USE
#

import sys

def lint_drumlanes(line):
    parts = split_line_to_parts(line)
    if len(parts) != 5:
        raise Exception("Syntax error: DRUMLANES must follow the format ROW:TRIG:CHAN:NOTENUMBER NAME")

    row = parts[0]
    if is_in_range(row, 1, 8) == False:
        raise Exception("ROW must be between 1 and 8")

    trig = parts[1]
    if is_null_or_in_range(trig, 0, 127) == False:
        raise Exception("TRIG must be between 0 and 127, or NULL")

    # TODO: CHAN check

    note_number = parts[3]
    if is_null_or_in_range(note_number, 0, 127) == False:
        raise Exception("NOTENUMBER must be between 0 and 127, or NULL")


def lint_PC(line):
    parts = split_line_to_parts(line)
    if len(parts) != 2 and len(parts) != 4:
        raise Exception("Syntax error: PC must follow format NUMBER NAME, OR NUMBER:MSB:LSB NAME")
    if is_in_range(parts[0], 1, 128) == False:
        raise Exception("PC must be a number between 1 and 128")
    if len(parts) > 2:
        if is_in_range(parts[1], 0, 127) == False:
            raise Exception("MSB must be a number between 0 and 127")
        if is_in_range(parts[2], 0, 127) == False:
            raise Exception("LSB must be a number between 0 and 127")

def lint_CC(line):
    return

def lint_NRPN(line):
    return

def lint_assign(line):
    return

def lint_automation(line):
    return

def lint_section_open(line):
    if line[0] != "[":
        raise Exception("Section definition must begin with '['")
    if line[1] == "/":
        raise Exception("Section definition text cannot begin with '/'")
    if line[-1] != "]":
        raise Exception("Section defintion must end with ']'")

def lint_section_close(line):
    if line[0] != "[":
        raise Exception("Section definition close must begin with '['")
    if line[1] != "/":
        raise Exception("Section definition close text must begin with '/'")
    if line[-1] != "]":
        raise Exception("Section defintion close must end with ']'")

def is_recognized_section(section):
    sections = ["ASSIGN","AUTOMATION","CC","COMMENT","DRUMLANES","NRPN","PC"]
    return section in sections


def is_null_or_in_range(part, start, end):
    if part != "NULL":
        try:
            # Casting throws ValueError if strig cannot convert to base 10
            if int(part) < start or int(part) > end:
                return False
        except:
            return False
    return True

def is_in_range(part, start, end):
    try:
        # Casting throws ValueError if cannot convert to base 10
        if int(part) < start or int(part) > end:
            return False
    except:
        return False
    return True

def split_line_to_parts(line):
    # TODO: Verify that Hapax parses lines properly when multiples spaces separate parts from NAME
    # TODO: Remove inline comments
    parts1 = line.split(":")
    #Split onces to allow names with spaces
    parts2 = parts1[-1].split(None, 1)
    parts = parts1[0:-1] + parts2
    return parts

with open(sys.argv[1]) as f:
    # TODO: check for accurate line_num
    # TODO: Ignore comment lines
    line_num = 0
    for line in f:
        line_num += 1
        #Skip if line begins with comment
        if line[0] == "#":
            continue
        if line[0] == "[":
            try:
                lint_section_open(line.strip())
            except Exception as e:
                msg = "Lint error found on line %s:" % line_num
                print(msg,e)
                exit(1)
            section = line.strip("[] \n")
            if is_recognized_section(section) == False:
                msg = "Lint error found on line %s:" % line_num
                print(msg, "Unrecognized section:", section)
                exit(1)
            for line in f:
                # We're now on the following line
                line_num += 1
                line = line.strip()
                if line[0] == "[":
                    if line.strip("[/]") != section:
                        msg = "Lint error found on line %s: " % line_num
                        msg += "Section close found for section that was not open. "
                        msg += "Expected %s " % section + "but found %s" % line.strip("[/]")
                        print(msg)
                        exit(1)
                    try:
                        lint_section_close(line)
                    except Exception as e:
                        msg = "Lint error found on line %s:" % line_num
                        print(msg,e)
                        exit(1)
                    break
                match section:
                    case "DRUMLANES":
                        lint_drumlanes(line)
                    case "PC":
                        lint_PC(line)
                    case "CC":
                        lint_CC(line)
                    case "NRPN":
                        lint_NRPN(line)
                    case "ASSIGN":
                        lint_assign(line)
                    case "AUTOMATION":
                        lint_automation(line)








