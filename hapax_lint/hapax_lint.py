# version 0.6
#
# Linter for Squarp Hapax instrument definition files.
#

import sys
import re
import os

class HapaxLintException(Exception):
    pass

class HapaxLinter():
    def __init__(self, filename):
        self.filename = filename
        return
    def lint_drumlanes(self, line):
        dl = re.match(r'(\d+):(\d+|NULL):((\d+)|G(\d)|CV(\d)|CVG(\d)|NULL):(\d+|NULL)\s(.+)', line)
        if dl == None:
            raise HapaxLintException("Syntax error: DRUMLANES must follow the format ROW:TRIG:CHAN:NOTENUMBER NAME")
        parts = dl.groups()
        if self.is_in_range(parts[0], 1, 8) == False:
            raise HapaxLintException("ROW must be between 1 and 8")
        if self.is_null_or_in_range(parts[1], 0, 127) == False:
            raise HapaxLintException("TRIG must be between 0 and 127, or NULL")
        if parts[3] != None:
            if self.is_null_or_in_range(parts[3], 1, 16) == False:
                raise HapaxLintException("CHAN must be between 1 and 16, or NULL")
        if parts[4] != None:
            if self.is_null_or_in_range(parts[4], 1, 4) == False:
                print(parts[4])
                raise HapaxLintException("CHAN Gx, x must be between 1 and 4, or NULL")
        if parts[5] != None:
            if self.is_null_or_in_range(parts[5], 1, 4) == False:
                raise HapaxLintException("CHAN CVx, x must be between 1 and 4, or NULL")
        if parts[6] != None:
            if self.is_null_or_in_range(parts[6], 1, 4) == False:
                raise HapaxLintException("CHAN CVGx, x must be between 1 and 4, or NULL")
        if self.is_null_or_in_range(parts[7], 0, 127) == False:
            raise HapaxLintException("NOTENUMBER must be between 0 and 127, or NULL")
        return True


    def lint_PC(self, line):
        pc = re.match(r'(\d+)(:(\d+|NULL):(\d+|NULL))?\s(.+)', line)
        if pc == None:
            raise HapaxLintException("Syntax error: PC must follow format NUMBER NAME, OR NUMBER:MSB:LSB NAME")
        parts = pc.groups()
        if self.is_in_range(parts[0], 1, 128) == False:
            raise HapaxLintException("PC must be a number between 1 and 128")
        if parts[2] != None:
            if self.is_null_or_in_range(parts[2], 0, 127) == False:
                raise HapaxLintException("MSB must be a number between 0 and 127")
            if self.is_null_or_in_range(parts[3], 0, 127) == False:
                raise HapaxLintException("LSB must be a number between 0 and 127")
        return True

    def lint_CC(self, line):
        cc = re.match(r'(\d+)(:DEFAULT=)?(\d+)?\s(.+)', line)
        if cc == None:
            raise HapaxLintException("Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME")
        parts = cc.groups()
        if self.is_in_range(parts[0], 0, 127) == False:
            raise HapaxLintException("CC must be a number between 0 and 127")
        # Line uses the NUMBER:DEFAULT=xx NAME format
        if parts[2] != None:
            if parts[1] == None:
                raise HapaxLintException("Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME")
            if self.is_in_range(parts[2], 0, 127) == False:
                raise HapaxLintException("DEFAULT value must be a number between 0 and 127")
        return True

    def lint_CC_Pair(self, line):
        cc_pair = re.match(r'(\d+):(\d+)\s(.+)', line)
        if cc_pair == None:
            raise HapaxLintException("Syntax error: CC_PAIR must follow format NUMBER:NUMBER NAME")
        parts = cc_pair.groups()
        if self.is_in_range(parts[0], 0, 127) == False:
            raise HapaxLintException("CC1 must be a number between 0 and 127")
        if self.is_in_range(parts[1], 0, 127) == False:
            raise HapaxLintException("CC2 must be a number between 0 and 127")
        return True

    def lint_NRPN(self, line):
        nrpn = re.match(r'([0-9]+):([0-9]+):([0-9]+)(:DEFAULT=)?(\d+)?\s(.+)$', line)
        if nrpn == None:
            raise HapaxLintException("Syntax error: NRPN must follow format MSB:LSB:DEPTH NAME or MSB:LSB:DEPTH:DEFAULT=xx NAME")
        parts = nrpn.groups()
        if self.is_in_range(parts[0], 0, 127) == False:
            raise HapaxLintException("MSB must be a number between 0 and 127")
        if self.is_in_range(parts[1], 0, 127) == False:
            raise HapaxLintException("LSB must be a number between 0 and 127")
        if self.depth_is_valid(parts[2]) == False:
            raise HapaxLintException("DEPTH must be a either 7 or 14")
        if parts[4] != None:
            if self.is_in_range(parts[4], 0, 16383) == False:
                raise HapaxLintException("VALUE must be between 0 and 16383")
        return True

    def lint_assign(self, line):
        assign = re.match(r'([1-8])\s(CC|CV|PB|NRPN):(\d+)(?::(\d+):(\d+))?\s?(?:DEFAULT=(\d+))?', line)
        if assign == None:
            assign = re.match(r'([1-8])\s(PB|AT|NULL)$', line)
            if assign:
                return True
        if assign == None:
            raise HapaxLintException("Syntax error: Assign must follow format POT_NUMBER(1-8) TYPE:VALUE or POT_NUMBER(1-8) TYPE:VALUE DEFAULT=DEFAULT_VALUE")
        parts = assign.groups()
        match parts[1]:
            case "CC":
                if self.is_in_range(parts[2], 0, 119) == False:
                    raise HapaxLintException("CC must be a number between 0 and 119")
                if parts[5] != None:
                    if self.is_in_range(parts[2], 0, 127) == False:
                        raise HapaxLintException("CC DEFAULT value must be a number between 0 and 127")
            #TODO: Also need to lint CV voltage
            case "CV":
                if self.is_in_range(parts[2], 1, 4) == False:
                    raise HapaxLintException("CV must be a number between 1 and 4")
                if parts[5] != None:
                    if self.is_in_range(parts[5], 0, 65535) == False:
                        raise HapaxLintException("CC DEFAULT value must be a number between 0 and 65535")
            case "NRPN":
                if self.is_in_range(parts[2], 0, 127) == False:
                    raise HapaxLintException("MSB must be a number between 0 and 127")
                if self.is_in_range(parts[3], 0, 127) == False:
                    raise HapaxLintException("LSB must be a number between 0 and 127")
                if self.depth_is_valid(parts[4]) == False:
                    raise HapaxLintException("DEPTH must be 7 or 14")
                if parts[5] != None:
                    if self.is_in_range(parts[5], 0, 65535) == False:
                        raise HapaxLintException("NRPN DEFAULT value must be a number between 0 and 65535")
            #TODO: Implement this?  Docs say everything after PB type is ignored but also says you can define a
            # default value.  WHICH IS IT?
            case "PB":
                pass
        return True

    def lint_automation(self, line):
        auto = re.match(r'(CC|AT|PB|CV|NRPN)(?::(\d+):?(\d+)?:?(\d+)?)?', line)
        if auto == None:
            raise HapaxLintException("Syntax error: AUTOMATION must follow format TYPE:VALUE.  Ensure value is the correct format.")
        parts = auto.groups()
        match parts[0]:
            case "CC":
                if self.is_in_range(parts[1], 0, 127) == False:
                    raise HapaxLintException("CC must be a number between 0 and 127")
            case "AT":
                pass
            case "PB":
                pass
            case "CV":
                if self.is_in_range(parts[1], 1, 4) == False:
                    raise HapaxLintException("CV must be a number between 1 and 4")
            case "NRPN":
                if self.is_in_range(parts[1], 0, 127) == False:
                    raise HapaxLintException("MSB must be a number between 0 and 127")
                if self.is_in_range(parts[2], 0, 127) == False:
                    raise HapaxLintException("LSB must be a number between 0 and 127")
                if self.depth_is_valid(parts[3]) == False:
                    raise HapaxLintException("DEPTH must be a 7 or 14")
        return True

    def lint_line_for_section(self, section, line):
        match section:
            case "DRUMLANES":
                self.lint_drumlanes(line)
            case "PC":
                self.lint_PC(line)
            case "CC":
                self.lint_CC(line)
            case "NRPN":
                self.lint_NRPN(line)
            case "ASSIGN":
                self.lint_assign(line)
            case "AUTOMATION":
                self.lint_automation(line)
            case "CC_PAIR":
                self.lint_CC_Pair(line)

    def lint_section_open(self, line):
        if line[0] != "[":
            raise HapaxLintException("Section definition open must begin with '['")
        if line[1] == "/":
            raise HapaxLintException("Section definition open text cannot begin with '[/'")
        if line[-1] != "]":
            raise HapaxLintException("Section defintion must end with ']'")
        section = re.match(r'\[(.*)\]', line).groups()[0]
        if self.is_recognized_section(section) == False:
            raise HapaxLintException("Section '%s' is not a valid section" % section)


    def lint_section_close(self, line):
        if line[0] != "[":
            raise HapaxLintException("Section definition close must begin with '['")
        if line[1] != "/":
            raise HapaxLintException("Section definition close text must begin with '/'")
        if line[-1] != "]":
            raise HapaxLintException("Section defintion close must end with ']'")

    def is_recognized_section(self, section):
        sections = ["ASSIGN","AUTOMATION","CC","COMMENT","DRUMLANES","NRPN","PC","CC_PAIR"]
        return section in sections


    def is_null_or_in_range(self, part, start, end):
        if part != "NULL":
            try:
                # Casting throws ValueError if string cannot convert to base 10
                if int(part) < start or int(part) > end:
                    return False
            except:
                #TODO: Should probably raise exception here since string expected but no valid string
                return False
        return True

    def is_in_range(self, part, start, end):
        try:
            # Casting throws ValueError if cannot convert to base 10
            if int(part) < start or int(part) > end:
                return False
        except:
            return False
        return True

    def depth_is_valid(self, depth):
        return int(depth) == 7 or int(depth) == 14

    def lint(self):
        with open(self.filename) as f:
            line_num = 0
            for line in f:
                line_num += 1
                #Skip if line begins with comment
                if line[0] == "#":
                    continue
                if line[0] == "[":
                    try:
                        self.lint_section_open(line.strip())
                    except HapaxLintException as e:
                        msg = "Lint error found on line %s:" % line_num
                        print(msg,e)
                        exit(1)
                    section = re.match(r'\[(.*)\]', line).groups()[0]
                    for line in f:
                        # We're now on the following line
                        line_num += 1
                        line = line.strip()
                        # Skip blank line
                        if len(line) == 0:
                            continue
                        # Skip comment
                        if line[0] == "#":
                            continue
                        # Removes inline comments
                        line = line.split("#")[0]
                        if line[0] == "[":
                            if line[1] != "/" and line.strip("[]") != section:
                                msg = "Lint error found on line %s: " % line_num
                                msg += "New section %s opened before closing open section %s" % (line.strip("[/]"), section)
                                print(msg)
                                exit(1)
                            if line.strip("[/]") != section:
                                msg = "Lint error found on line %s: " % line_num
                                msg += "Section close found for section that was not open. "
                                msg += "Expected %s but found %s" % (section, line.strip("[/]"))
                                print(msg)
                                exit(1)
                            try:
                                self.lint_section_close(line)
                            except HapaxLintException as e:
                                msg = "Lint error found on line %s:" % line_num
                                print(msg,e)
                                exit(1)
                            break
                        try:
                            self.lint_line_for_section(section, line)
                        except HapaxLintException as e:
                            lint_err = str(e)
                            msg = "Lint error found on line %s:" % line_num
                            print(msg, lint_err)
                            exit(1)

            print("Finished linting file: %s\nNo lint errors found" % fname)


if __name__ == "__main__":
    fname = sys.argv[1]
    linter = HapaxLinter(fname)
    linter.lint()