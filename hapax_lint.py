

def lint_drumlanes(line):
    parts1 = line.split(":")
    if len(parts1) != 4:
        raise Exception("ROW, TRIG, CHAN, and NOTENUMBER must exist and be separated by ':'")
    parts2 = parts[3].split()
    if len(parts2) != 2:
        raise Exception("NOTENUMBER and NAME must be separated by a space")
    parts = parts1 + parts2
    row = int(parts[0])
    if row < 1 or row > 8:
        raise Exception("ROW must be between 1 and 8")
    trig = parts[1]
    if trig != "NULL":
        try:
            if int(trig) < 0 or int(trig) > 127:
                raise Exception
        except:
            raise Exception("TRIG must be between 0 and 127, or NULL")
    #TODO: CHAN check
    note_number = int(parts[3])
    if note_number < 0 or note_number > 127:
        raise Exception

def lint_PC():
    return

def lint_CC():
    return

def lint_NRPN():
    return

def lint_assign():
    return

def lint_automation():
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


with open("./roland_jx08.txt") as f:
    line_num = 1
    for line in f:
        if line[0] == "[":
            try:
                lint_section_open(line.strip())
            except Exception as e:
                msg = "Lint error found on line %s:" % line_num
                print(msg,e)
                exit(1)
            section = line.strip("[] \n")
            for line in f:
                line_num += 1
                if line[0] == "[":
                    try:
                        lint_section_close(line.strip())
                    except Exception as e:
                        msg = "Lint error found on line %s:" % line_num
                        print(msg,e)
                        exit(1)
                    break
            print(section)
            exit()
        line_num += 1
