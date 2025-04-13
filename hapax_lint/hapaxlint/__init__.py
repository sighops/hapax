# version 0.9
#
# Linter for Squarp Hapax instrument definition files.
#

import re
import sys
from hapaxlint import errors
from hapaxlint import warnings

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
            raise HapaxLintException(errors.DRUM)
        parts = dl.groups()
        if self._is_in_range(parts[0], 1, 8) is False:
            raise HapaxLintException(errors.DRUM_ROW)
        if self._is_null_or_in_range(parts[1], 0, 127) is False:
            raise HapaxLintException(errors.DRUM_TRIG)
        if parts[3] is not None:
            if self._is_null_or_in_range(parts[3], 1, 16) is False:
                raise HapaxLintException(errors.DRUM_CHAN)
        if parts[4] is not None:
            if self._is_null_or_in_range(parts[4], 1, 4) is False:
                raise HapaxLintException(errors.DRUM_CHAN_G)
        if parts[5] is not None:
            if self._is_null_or_in_range(parts[5], 1, 4) is False:
                raise HapaxLintException(errors.DRUM_CHAN_CV)
        if parts[6] is not None:
            if self._is_null_or_in_range(parts[6], 1, 4) is False:
                raise HapaxLintException(errors.DRUM_CHAN_CVG)
        if self._is_null_or_in_range(parts[7], 0, 127) is False:
            raise HapaxLintException(errors.DRUM_NOTE)
        return True


    def lint_pc(self, line):
        pc = re.match(r'(\d+)(:(\d+|NULL):(\d+|NULL))?\s(.+)', line)
        if pc is None:
            raise HapaxLintException(errors.PC)
        parts = pc.groups()
        if self._is_in_range(parts[0], 1, 128) is False:
            raise HapaxLintException(errors.PC_RANGE)
        if parts[2] is not None:
            if self._is_null_or_in_range(parts[2], 0, 127) is False:
                raise HapaxLintException(errors.PC_MSB)
            if self._is_null_or_in_range(parts[3], 0, 127) is False:
                raise HapaxLintException(errors.PC_LSB)
        return True

    def lint_cc(self, line):
        cc = re.match(r'(\d+)(:DEFAULT=)?(\d+)?\s(.+)', line)
        if cc is None:
            cc = re.match(r'(\d+):(\d+)\s(.+)', line)
            if cc is not None:
                raise HapaxLintWarning(warnings.CC_DEFAULT)
            raise HapaxLintException(errors.CC)
        parts = cc.groups()
        if self._is_in_range(parts[0], 0, 127) is False:
            raise HapaxLintException(errors.CC_RANGE)
        # Line uses the NUMBER:DEFAULT=xx NAME format
        if parts[2] is not None:
            if parts[1] is None:
                raise HapaxLintException(errors.CC_FMT)
            if self._is_in_range(parts[2], 0, 127) is False:
                raise HapaxLintException(errors.CC_DEFAULT)
        return True

    def lint_cc_pair(self, line):
        cc_pair = re.match(r'(\d+):(\d+)\s(.+)', line)
        if cc_pair is None:
            raise HapaxLintException(errors.CC_PAIR)
        parts = cc_pair.groups()
        if self._is_in_range(parts[0], 0, 127) is False:
            raise HapaxLintException(errors.CC_PAIR_1)
        if self._is_in_range(parts[1], 0, 127) is False:
            raise HapaxLintException(errors.CC_PAIR_2)
        return True

    def lint_nrpn(self, line):
        nrpn = re.match(r'(\d+):(\d+):(\d+)(:DEFAULT=)?(\d+)?\s(.+)$', line)
        if nrpn is None:
            nrpn = re.match(r'(\d+):(\d+):(\d+):(\d+)?\s(.+)$', line)
            if nrpn is not None:
                raise HapaxLintWarning(warnings.NRPN_DEFAULT)
            raise HapaxLintException(errors.NRPN)
        parts = nrpn.groups()
        if self._is_in_range(parts[0], 0, 127) is False:
            raise HapaxLintException(errors.NRPN_MSB)
        if self._is_in_range(parts[1], 0, 127) is False:
            raise HapaxLintException(errors.NRPN_LSB)
        if self._depth_is_valid(parts[2]) is False:
            raise HapaxLintException(errors.NRPN_DEPTH)
        if parts[4] is not None:
            if self._is_in_range(parts[4], 0, 16383) is False:
                raise HapaxLintException(errors.NRPN_VALUE)
        return True

    def _lint_assign(self, line):
        assign = re.match(r'([1-8])\s(CC|CV|PB|NRPN):(\d+)(?::(\d+):(\d+))?\s?(?:DEFAULT=(\d+|[\-0-9.]+V))?', line)
        if assign is None:
            assign = re.match(r'([1-8])\s(PB|AT|NULL)$', line)
            if assign:
                return True
        if assign is None:
            raise HapaxLintException(errors.ASSN)
        parts = assign.groups()
        match parts[1]:
            case "CC":
                if self._is_in_range(parts[2], 0, 119) is False:
                    raise HapaxLintException(errors.ASSN_CC)
                if parts[5] is not None:
                    if self._is_in_range(parts[5], 0, 127) is False:
                        raise HapaxLintException(errors.ASSN_CC_DEFAULT)
            case "CV":
                if self._is_in_range(parts[2], 1, 4) is False:
                    raise HapaxLintException(errors.ASSN_CV)
                if parts[5] is not None:
                    if "V" in parts[5]:
                        if self._is_valid_voltage(parts[5].strip("V")) is False:
                            raise HapaxLintException(errors.ASSN_CV_DEFAULT_V)
                    elif self._is_in_range(parts[5], 0, 65535) is False:
                        raise HapaxLintException(errors.ASSN_CV_DEFAULT_VAL)
            case "NRPN":
                if self._is_in_range(parts[2], 0, 127) is False:
                    raise HapaxLintException(errors.ASSN_MSB)
                if self._is_in_range(parts[3], 0, 127) is False:
                    raise HapaxLintException(errors.ASSN_LSB)
                if self._depth_is_valid(parts[4]) is False:
                    raise HapaxLintException(errors.ASSN_DEPTH)
                if parts[5] is not None:
                    if self._is_in_range(parts[5], 0, 65535) is False:
                        raise HapaxLintException(errors.ASSN_NRPN)
            # Should this be implemented?  Docs say everything after PB type is ignored but also says you can define a
            # default value.  WHICH IS IT?
            case "PB":
                pass
        return True

    def lint_automation(self, line):
        auto = re.match(r'(CC|AT|PB|CV|NRPN)(?::(\d+):?(\d+)?:?(\d+)?)?', line)
        if auto is None:
            raise HapaxLintException(errors.AUTO)
        parts = auto.groups()
        match parts[0]:
            case "CC":
                if self._is_in_range(parts[1], 0, 127) is False:
                    raise HapaxLintException(errors.AUTO_CC)
            case "AT":
                pass
            case "PB":
                pass
            case "CV":
                if self._is_in_range(parts[1], 1, 4) is False:
                    raise HapaxLintException(errors.AUTO_CV)
            case "NRPN":
                if self._is_in_range(parts[1], 0, 127) is False:
                    raise HapaxLintException(errors.AUTO_MSB)
                if self._is_in_range(parts[2], 0, 127) is False:
                    raise HapaxLintException(errors.AUTO_LSB)
                if self._depth_is_valid(parts[3]) is False:
                    raise HapaxLintException(errors.AUTO_DEPTH)
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
            raise HapaxLintException(errors.CTX_OPEN)
        if line[1] == "/":
            raise HapaxLintException(errors.CTX_OPEN_FMT)
        if line[-1] != "]":
            raise HapaxLintException(errors.CTX_OPEN_CLOSE)
        section = re.match(r'\[(.*)\]', line).groups()[0]
        if self._is_recognized_section(section) is False:
            raise HapaxLintException(f"Section '{section}' is not a valid section")


    def _lint_section_close(self, line):
        if line[0] != "[":
            raise HapaxLintException(errors.CTX_CLOSE)
        if line[1] != "/":
            raise HapaxLintException(errors.CTX_CLOSE_FMT)
        if line[-1] != "]":
            raise HapaxLintException(errors.CTX_CLOSE_CLOSE)

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
            raise HapaxLintException(errors.TRACKNAME)
        return True

    def _lint_type(self, line):
        def_type = re.match(r'TYPE (POLY|DRUM|MPE|NULL)$', line)
        if def_type is None:
            raise HapaxLintException(errors.TYPE)
        return True

    def _lint_outport(self, line):
        def_type = re.match(r'OUTPORT (A|B|C|D|USBD|USBH|CVG[1-4]|CVX[1-4]|G[1-4]|NULL)$', line)
        if def_type is None:
            raise HapaxLintException(errors.OUTPORT)
        return True

    def _lint_outchan(self, line):
        def_type = re.match(r'OUTCHAN ([1-9]|1[0-6]|NULL)$', line)
        if def_type is None:
            raise HapaxLintException(errors.OUTCHAN)
        return True

    def _lint_inport(self, line):
        def_type = re.match(r'INPORT (NONE|ALLACTIVE|A|B|USBD|USBH|CVG|NULL)$', line)
        if def_type is None:
            raise HapaxLintException(errors.INPORT)
        return True

    def _lint_inchan(self, line):
        def_type = re.match(r'INCHAN ([1-9]|1[0-6]|ALL|NULL)$', line)
        if def_type is None:
            raise HapaxLintException(errors.INCHAN)
        return True

    def _lint_maxrate(self, line):
        maxrate = re.match(r'MAXRATE (NULL|192|96|64|48|32|24|16|12|8|6|4|3|2|1)$', line)
        if maxrate is None:
            raise HapaxLintException(errors.MAXRATE)

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
