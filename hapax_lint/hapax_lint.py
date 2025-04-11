# version 0.9
#
# Linter for Squarp Hapax instrument definition files.
#

import sys
import re

class HapaxLintException(Exception):
    pass

class HapaxLintWarning(Exception):
    pass

class HapaxInstrumentLinter():
    def __init__(self, filename=None, strict=False):
        self.filename = filename
        self.strict = strict
        self.has_warnings = False

    def lint_drumlanes(self, line):
        dl = re.match(r'(\d+):(\d+|NULL):((\d+)|G(\d)|CV(\d)|CVG(\d)|NULL):(\d+|NULL)\s(.+)', line)
        if dl is None:
            raise HapaxLintException("Syntax error: DRUMLANES must follow the format ROW:TRIG:CHAN:NOTENUMBER NAME")
        parts = dl.groups()
        if self._is_in_range(parts[0], 1, 8) is False:
            raise HapaxLintException("ROW must be between 1 and 8")
        if self._is_null_or_in_range(parts[1], 0, 127) is False:
            raise HapaxLintException("TRIG must be between 0 and 127, or NULL")
        if parts[3] is not None:
            if self._is_null_or_in_range(parts[3], 1, 16) is False:
                raise HapaxLintException("CHAN must be between 1 and 16, or NULL")
        if parts[4] is not None:
            if self._is_null_or_in_range(parts[4], 1, 4) is False:
                raise HapaxLintException("CHAN Gx, x must be between 1 and 4, or NULL")
        if parts[5] is not None:
            if self._is_null_or_in_range(parts[5], 1, 4) is False:
                raise HapaxLintException("CHAN CVx, x must be between 1 and 4, or NULL")
        if parts[6] is not None:
            if self._is_null_or_in_range(parts[6], 1, 4) is False:
                raise HapaxLintException("CHAN CVGx, x must be between 1 and 4, or NULL")
        if self._is_null_or_in_range(parts[7], 0, 127) is False:
            raise HapaxLintException("NOTENUMBER must be between 0 and 127, or NULL")
        return True


    def lint_pc(self, line):
        pc = re.match(r'(\d+)(:(\d+|NULL):(\d+|NULL))?\s(.+)', line)
        if pc is None:
            raise HapaxLintException("Syntax error: PC must follow format NUMBER NAME, OR NUMBER:MSB:LSB NAME")
        parts = pc.groups()
        if self._is_in_range(parts[0], 1, 128) is False:
            raise HapaxLintException("PC must be a number between 1 and 128")
        if parts[2] is not None:
            if self._is_null_or_in_range(parts[2], 0, 127) is False:
                raise HapaxLintException("MSB must be a number between 0 and 127")
            if self._is_null_or_in_range(parts[3], 0, 127) is False:
                raise HapaxLintException("LSB must be a number between 0 and 127")
        return True

    def lint_cc(self, line):
        cc = re.match(r'(\d+)(:DEFAULT=)?(\d+)?\s(.+)', line)
        if cc is None:
            cc = re.match(r'(\d+):(\d+)\s(.+)', line)
            if cc is not None:
                raise HapaxLintWarning("Undocumented syntax used for CC definition.  Expected NUMBER:DEFAULT=xx, but got NUMBER:xx")
            raise HapaxLintException("Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME")
        parts = cc.groups()
        if self._is_in_range(parts[0], 0, 127) is False:
            raise HapaxLintException("CC must be a number between 0 and 127")
        # Line uses the NUMBER:DEFAULT=xx NAME format
        if parts[2] is not None:
            if parts[1] is None:
                raise HapaxLintException("Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME")
            if self._is_in_range(parts[2], 0, 127) is False:
                raise HapaxLintException("DEFAULT value must be a number between 0 and 127")
        return True

    def lint_cc_pair(self, line):
        cc_pair = re.match(r'(\d+):(\d+)\s(.+)', line)
        if cc_pair is None:
            raise HapaxLintException("Syntax error: CC_PAIR must follow format NUMBER:NUMBER NAME")
        parts = cc_pair.groups()
        if self._is_in_range(parts[0], 0, 127) is False:
            raise HapaxLintException("CC1 must be a number between 0 and 127")
        if self._is_in_range(parts[1], 0, 127) is False:
            raise HapaxLintException("CC2 must be a number between 0 and 127")
        return True

    def lint_nrpn(self, line):
        nrpn = re.match(r'(\d+):(\d+):(\d+)(:DEFAULT=)?(\d+)?\s(.+)$', line)
        if nrpn is None:
            nrpn = re.match(r'(\d+):(\d+):(\d+):(\d+)?\s(.+)$', line)
            if nrpn is not None:
                raise HapaxLintWarning("Undocumented syntax used for NRPN definition.  Expected MSB:LSB:DEPTH:DEFAULT=xx, but got MSB:LSB:DEPTH:xx")
            raise HapaxLintException("Syntax error: NRPN must follow format MSB:LSB:DEPTH NAME or MSB:LSB:DEPTH:DEFAULT=xx NAME")
        parts = nrpn.groups()
        if self._is_in_range(parts[0], 0, 127) is False:
            raise HapaxLintException("MSB must be a number between 0 and 127")
        if self._is_in_range(parts[1], 0, 127) is False:
            raise HapaxLintException("LSB must be a number between 0 and 127")
        if self._depth_is_valid(parts[2]) is False:
            raise HapaxLintException("DEPTH must be a either 7 or 14")
        if parts[4] is not None:
            if self._is_in_range(parts[4], 0, 16383) is False:
                raise HapaxLintException("VALUE must be between 0 and 16383")
        return True

    def _lint_assign(self, line):
        assign = re.match(r'([1-8])\s(CC|CV|PB|NRPN):(\d+)(?::(\d+):(\d+))?\s?(?:DEFAULT=(\d+|[\-0-9.]+V))?', line)
        if assign is None:
            assign = re.match(r'([1-8])\s(PB|AT|NULL)$', line)
            if assign:
                return True
        if assign is None:
            raise HapaxLintException("Syntax error: Assign must follow format POT_NUMBER(1-8) TYPE:VALUE or POT_NUMBER(1-8) TYPE:VALUE DEFAULT=DEFAULT_VALUE")
        parts = assign.groups()
        match parts[1]:
            case "CC":
                if self._is_in_range(parts[2], 0, 119) is False:
                    raise HapaxLintException("CC must be a number between 0 and 119")
                if parts[5] is not None:
                    if self._is_in_range(parts[5], 0, 127) is False:
                        raise HapaxLintException("CC DEFAULT value must be a number between 0 and 127")
            case "CV":
                if self._is_in_range(parts[2], 1, 4) is False:
                    raise HapaxLintException("CV must be a number between 1 and 4")
                if parts[5] is not None:
                    if "V" in parts[5]:
                        if self._is_valid_voltage(parts[5].strip("V")) is False:
                            raise HapaxLintException("CV DEFAULT Voltage must be a number between -5 and 5")
                    elif self._is_in_range(parts[5], 0, 65535) is False:
                        raise HapaxLintException("CV DEFAULT value must be a number between 0 and 65535")
            case "NRPN":
                if self._is_in_range(parts[2], 0, 127) is False:
                    raise HapaxLintException("MSB must be a number between 0 and 127")
                if self._is_in_range(parts[3], 0, 127) is False:
                    raise HapaxLintException("LSB must be a number between 0 and 127")
                if self._depth_is_valid(parts[4]) is False:
                    raise HapaxLintException("DEPTH must be 7 or 14")
                if parts[5] is not None:
                    if self._is_in_range(parts[5], 0, 65535) is False:
                        raise HapaxLintException("NRPN DEFAULT value must be a number between 0 and 65535")
            # Should this be implemented?  Docs say everything after PB type is ignored but also says you can define a
            # default value.  WHICH IS IT?
            case "PB":
                pass
        return True

    def lint_automation(self, line):
        auto = re.match(r'(CC|AT|PB|CV|NRPN)(?::(\d+):?(\d+)?:?(\d+)?)?', line)
        if auto is None:
            raise HapaxLintException("Syntax error: AUTOMATION must follow format TYPE:VALUE.  Ensure value is the correct format.")
        parts = auto.groups()
        match parts[0]:
            case "CC":
                if self._is_in_range(parts[1], 0, 127) is False:
                    raise HapaxLintException("CC must be a number between 0 and 127")
            case "AT":
                pass
            case "PB":
                pass
            case "CV":
                if self._is_in_range(parts[1], 1, 4) is False:
                    raise HapaxLintException("CV must be a number between 1 and 4")
            case "NRPN":
                if self._is_in_range(parts[1], 0, 127) is False:
                    raise HapaxLintException("MSB must be a number between 0 and 127")
                if self._is_in_range(parts[2], 0, 127) is False:
                    raise HapaxLintException("LSB must be a number between 0 and 127")
                if self._depth_is_valid(parts[3]) is False:
                    raise HapaxLintException("DEPTH must be a 7 or 14")
        return True

    def _lint_line_for_section(self, section, line):
        match section:
            case "DRUMLANES":
                self.lint_drumlanes(line)
            case "PC":
                self.lint_pc(line)
            case "CC":
                self.lint_cc(line)
            case "NRPN":
                self.lint_nrpn(line)
            case "ASSIGN":
                self._lint_assign(line)
            case "AUTOMATION":
                self.lint_automation(line)
            case "CC_PAIR":
                self.lint_cc_pair(line)

    def _lint_section_open(self, line):
        if line[0] != "[":
            raise HapaxLintException("Section definition open must begin with '['")
        if line[1] == "/":
            raise HapaxLintException("Section definition open text cannot begin with '[/'")
        if line[-1] != "]":
            raise HapaxLintException("Section defintion must end with ']'")
        section = re.match(r'\[(.*)\]', line).groups()[0]
        if self._is_recognized_section(section) is False:
            raise HapaxLintException(f"Section '{section}' is not a valid section")


    def _lint_section_close(self, line):
        if line[0] != "[":
            raise HapaxLintException("Section definition close must begin with '['")
        if line[1] != "/":
            raise HapaxLintException("Section definition close text must begin with '/'")
        if line[-1] != "]":
            raise HapaxLintException("Section defintion close must end with ']'")

    def _is_recognized_section(self, section):
        sections = ["ASSIGN","AUTOMATION","CC","COMMENT","DRUMLANES","NRPN","PC","CC_PAIR"]
        return section in sections


    def _is_null_or_in_range(self, part, start, end):
        if part != "NULL":
            try:
                # Casting throws ValueError if string cannot convert to base 10
                if int(part) < start or int(part) > end:
                    return False
            except ValueError:
                #TODO: Should probably raise exception here since string expected but no valid string
                return False
        return True

    def _is_in_range(self, part, start, end):
        try:
            # Casting throws ValueError if cannot convert to base 10
            if int(part) < start or int(part) > end:
                return False
        except ValueError:
            return False
        return True

    def _depth_is_valid(self, depth):
        return int(depth) == 7 or int(depth) == 14

    def _is_valid_voltage(self, voltage):
        try:
            if float(voltage) < -5 or float(voltage) > 5:
                return False
        except ValueError:
            return False
        return True

    def _lint_trackname(self, line):
        trackname = re.match(r'TRACKNAME [A-z0-9 _\-\+]+$', line)
        if trackname is None:
            raise HapaxLintException("Syntax error: TRACKNAME must be in format: 'TRACKNAME NAME', NAME must be alphanumeric ASCII or one of ' ', '_', '-', '+'")
        return True

    def _lint_type(self, line):
        def_type = re.match(r'TYPE (POLY|DRUM|MPE|NULL)$', line)
        if def_type is None:
            raise HapaxLintException("Syntax error: TYPE must be in format: 'TYPE DEF_TYPE', DEF_TYPE must be one of POLY, DRUM, MPE, or NULL")
        return True

    def _lint_outport(self, line):
        def_type = re.match(r'OUTPORT (A|B|C|D|USBD|USBH|CVG[1-4]|CVX[1-4]|G[1-4]|NULL)$', line)
        if def_type is None:
            raise HapaxLintException("Syntax error: OUTPORT must be in format: 'OUTPORT PORT', PORT must be one of A, B, C, D, USBD, USBH, CVGx, CVx, Gx, or NULL(x between 1&4)")
        return True

    def _lint_outchan(self, line):
        def_type = re.match(r'OUTCHAN ([1-9]|1[0-6]|NULL)$', line)
        if def_type is None:
            raise HapaxLintException("Syntax error: OUTCHAN must be in format: 'OUTCHAN CHAN', CHAN must be between 1 and 16 or NULL")
        return True

    def _lint_inport(self, line):
        def_type = re.match(r'INPORT (NONE|ALLACTIVE|A|B|USBD|USBH|CVG|NULL)$', line)
        if def_type is None:
            raise HapaxLintException("Syntax error: TYPE must be in format: 'INPORT PORT', PORT must be one of NONE, ALLACTIVE, A, B, USBH, USBD, CVG, or NULL")
        return True

    def _lint_inchan(self, line):
        def_type = re.match(r'INCHAN ([1-9]|1[0-6]|ALL|NULL)$', line)
        if def_type is None:
            raise HapaxLintException("Syntax error: INCHAN must be in format: 'INCHAN CHAN', CHAN must be between 1 and 16, ALL, or NULL")
        return True

    def _lint_maxrate(self, line):
        maxrate = re.match(r'MAXRATE (NULL|192|96|64|48|32|24|16|12|8|6|4|3|2|1)$', line)
        if maxrate is None:
            raise HapaxLintException("Syntax error: MAXRATE must be in format: 'MAXRATE RATE', RATE must be be one of NULL, 192, 96, 64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1")

    def lint_setup(self, setup, line):
        match setup:
            case "TRACKNAME":
                self._lint_trackname(line)
            case "TYPE":
                self._lint_type(line)
            case "OUTPORT":
                self._lint_outport(line)
            case "OUTCHAN":
                self._lint_outchan(line)
            case "INPORT":
                self._lint_inport(line)
            case "INCHAN":
                self._lint_inchan(line)
            case "MAXRATE":
                self._lint_maxrate(line)
            case "VERSION":
                pass
            case _:
                raise HapaxLintException(f"Syntax error: {setup} is not a valid setup value.")

    def lint(self):
        with open(self.filename) as f:
            try:
                line_num = 0
                for line in f:
                    line_num += 1
                    #Skip if line begins with comment
                    if line[0] == "#":
                        continue
                    if line[0] == "[":
                        self._lint_section_open(line.strip())
                        section = re.match(r'\[(.*)\]', line).groups()[0]
                        for line in f:
                            # We're now on the following line
                            line_num += 1
                            line = line.strip()
                            # Skip blank line
                            if len(line) == 0:
                                continue
                            # Skip comment lines
                            if line[0] == "#":
                                continue
                            # Removes inline comments
                            line = line.split("#")[0]
                            if line[0] == "[":
                                if line[1] != "/":
                                    raise HapaxLintException(f'New {line.strip("[/]")} section opened before closing open {section} section')
                                if line.strip("[/]") != section:
                                    raise HapaxLintException(f'Section close found for section that was not open. Expected {section} but found {line.strip("[/]")}')
                                self._lint_section_close(line)
                                break
                            self._lint_line_for_section(section, line)

                    setup = re.match(r'^(\w+)\s', line)
                    if setup is not None:
                        setup = setup.groups()[0]
                        self.lint_setup(setup, line.strip())
            except HapaxLintWarning as e:
                if self.strict is True:
                    self.has_warnings = True
                    warning = str(e)
                    msg = f"WARNING on line {line_num}:"
                    print(msg, warning)
            except HapaxLintException as e:
                lint_err = str(e)
                msg = f"Error found on line {line_num}:"
                print(msg, lint_err, f"\nLine {line_num}: {line}")
                sys.exit(1)
            if self.has_warnings:
                print(f"Finished linting file: {self.filename}\nFinished with warnings, but no errors found.")
                print("Lines with warnings may work but don't follow documented standards and may break in future firmware versions.")
            else:
                print(f"Finished linting file: {self.filename}\nNo lint errors found")


if __name__ == "__main__":
    if not sys.version_info >= (3, 10):
        print("FAIL: Python version 3.10 or greater is required.")
    fname = sys.argv[1]
    linter = HapaxInstrumentLinter(fname)
    linter.lint()
