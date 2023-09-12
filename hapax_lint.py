#
# WORK IN PROGRESS -- DO NOT USE
#

import sys
import re

class HapaxLintException(Exception):
    pass

def lint_drumlanes(line):
    parts = split_line_to_parts(line)
    if len(parts) != 5:
        raise HapaxLintException("Syntax error: DRUMLANES must follow the format ROW:TRIG:CHAN:NOTENUMBER NAME")

    row = parts[0]
    if is_in_range(row, 1, 8) == False:
        raise HapaxLintException("ROW must be between 1 and 8")

    trig = parts[1]
    if is_null_or_in_range(trig, 0, 127) == False:
        raise HapaxLintException("TRIG must be between 0 and 127, or NULL")

    # TODO: CHAN check

    note_number = parts[3]
    if is_null_or_in_range(note_number, 0, 127) == False:
        raise HapaxLintException("NOTENUMBER must be between 0 and 127, or NULL")


def lint_PC(line):
    parts = split_line_to_parts(line)
    if len(parts) != 2 and len(parts) != 4:
        raise HapaxLintException("Syntax error: PC must follow format NUMBER NAME, OR NUMBER:MSB:LSB NAME")
    if is_in_range(parts[0], 1, 128) == False:
        raise HapaxLintException("PC must be a number between 1 and 128")
    if len(parts) > 2:
        if is_in_range(parts[1], 0, 127) == False:
            raise HapaxLintException("MSB must be a number between 0 and 127")
        if is_in_range(parts[2], 0, 127) == False:
            raise HapaxLintException("LSB must be a number between 0 and 127")

def lint_CC(line):
    parts = split_line_to_parts(line)
    if len(parts) != 2 and len(parts) != 3:
        raise HapaxLintException("Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME")
    if is_in_range(parts[0], 0, 127) == False:
        raise HapaxLintException("CC must be a number between 0 and 127")
    # Line uses the NUMBER:DEFAULT=xx NAME format
    if len(parts) == 3:
        default, value = parts[1].split("=")
        if default != "DEFAULT":
            raise HapaxLintException("Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME")
        if is_in_range(value, 0, 127) == False:
            raise HapaxLintException("DEFAULT value must be a number between 0 and 127")

def lint_NRPN(line):
    parts = split_line_to_parts(line)
    length = len(parts)
    if length != 4 and length != 5:
        raise HapaxLintException("Syntax error: NRPN must follow format MSB:LSB:DEPTH NAME or MSB:LSB:DEPTH:DEFAULT=xx NAME")
    if is_in_range(parts[0], 0, 127) == False:
        raise HapaxLintException("MSB must be a number between 0 and 127")
    if is_in_range(parts[1], 0, 127) == False:
        raise HapaxLintException("LSB must be a number between 0 and 127")
    if depth_is_valid(parts[2]) == False:
        raise HapaxLintException("DEPTH must be a either 7 or 14")
    if length == 5:
        if is_in_range(parts[3], 0, 16383) == False:
            raise HapaxLintException("DEPTH must be a either 7 or 14")

def lint_assign(line):
    parts = split_assign_line_to_parts(line)
    print(parts)
    return

def lint_automation(line):
    parts = split_line_to_parts(line)

def lint_line_for_section(section, line):
    try:
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
    except HapaxLintException as e:
        return str(e)

def lint_section_open(line):
    if line[0] != "[":
        raise HapaxLintException("Section definition must begin with '['")
    if line[1] == "/":
        raise HapaxLintException("Section definition text cannot begin with '/'")
    if line[-1] != "]":
        raise HapaxLintException("Section defintion must end with ']'")

def lint_section_close(line):
    if line[0] != "[":
        raise HapaxLintException("Section definition close must begin with '['")
    if line[1] != "/":
        raise HapaxLintException("Section definition close text must begin with '/'")
    if line[-1] != "]":
        raise HapaxLintException("Section defintion close must end with ']'")

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

def depth_is_valid(depth):
    return depth == 7 or depth == 14

def split_line_to_parts(line):
    # TODO: Remove inline comments?
    parts1 = line.split(":")
    #Split onces to allow names with spaces
    parts2 = parts1[-1].split(None, 1)
    parts = parts1[0:-1] + parts2
    return parts

# Because assigns couldn't just follow the same formatting...
def split_assign_line_to_parts(line):
    # TODO: Remove inline comments?
    parts1 = line.split(" ", 1)
    parts2 = parts1[-1].split(":")
    if re.search("DEFAULT_VALUE=", parts2[-1]):
        splits = 2
    else:
        splits = 1
    parts3 = parts2[-1].split(" ", splits)
    #Split onces to allow names with spaces
    parts = [parts1[0]] + [parts2[0]] + parts3
    return parts

fname = sys.argv[1]
with open(fname) as f:
    # TODO: check for accurate line_num
    line_num = 0
    for line in f:
        line_num += 1
        #Skip if line begins with comment
        if line[0] == "#":
            continue
        if line[0] == "[":
            try:
                lint_section_open(line.strip())
            except HapaxLintException as e:
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
                    except HapaxLintException as e:
                        msg = "Lint error found on line %s:" % line_num
                        print(msg,e)
                        exit(1)
                    break
                lint_err = lint_line_for_section(section, line)
                if lint_err != None:
                    msg = "Lint error found on line %s:" % line_num
                    print(msg, lint_err)
                    exit(1)
                
    print("Finished linting file: %s\nNo lint errors found" % fname)
