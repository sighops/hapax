# DRUMLANE Errors
DRUM = "Syntax error: DRUMLANES must follow the format ROW:TRIG:CHAN:NOTENUMBER NAME"
DRUM_ROW = "ROW must be between 1 and 8"
DRUM_TRIG = "TRIG must be between 0 and 127, or NULL"
DRUM_CHAN = "CHAN must be between 1 and 16, or NULL"
DRUM_CHAN_G = "CHAN Gx, x must be between 1 and 4, or NULL"
DRUM_CHAN_CV = "CHAN CVx, x must be between 1 and 4, or NULL"
DRUM_CHAN_CVG = "CHAN CVGx, x must be between 1 and 4, or NULL"
DRUM_NOTE = "NOTENUMBER must be between 0 and 127, or NULL"

# PC Errors
PC = "Syntax error: PC must follow format NUMBER NAME, OR NUMBER:MSB:LSB NAME"
PC_RANGE = "PC must be a number between 1 and 128"
PC_MSB = "MSB must be a number between 0 and 127"
PC_LSB = "LSB must be a number between 0 and 127"

# CC Errors
CC = "Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME"
CC_RANGE = "CC must be a number between 0 and 127"
CC_FMT = "Syntax error: CC must follow format NUMBER NAME, OR NUMBER:DEFAULT=xx NAME"
CC_DEFAULT = "DEFAULT value must be a number between 0 and 127"

# CC_PAIR Errors
CC_PAIR = "Syntax error: CC_PAIR must follow format NUMBER:NUMBER NAME"
CC_PAIR_1 = "CC1 must be a number between 0 and 127"
CC_PAIR_2 = "CC2 must be a number between 0 and 127"

# NRPN Errors
NRPN = "Syntax error: NRPN must follow format MSB:LSB:DEPTH NAME or MSB:LSB:DEPTH:DEFAULT=xx NAME"
NRPN_MSB = "MSB must be a number between 0 and 127"
NRPN_LSB = "LSB must be a number between 0 and 127"
NRPN_DEPTH = "DEPTH must be a either 7 or 14"
NRPN_VALUE = "VALUE must be between 0 and 16383"

# ASSIGN Errors
ASSN = "Syntax error: Assign must follow format POT_NUMBER(1-8) TYPE:VALUE or POT_NUMBER(1-8) TYPE:VALUE DEFAULT=DEFAULT_VALUE"
ASSN_CC = "CC must be a number between 0 and 119"
ASSN_CC_DEFAULT = "CC DEFAULT value must be a number between 0 and 127"
ASSN_CV = "CV must be a number between 1 and 4"
ASSN_CV_DEFAULT_V = "CV DEFAULT Voltage must be a number between -5 and 5"
ASSN_CV_DEFAULT_VAL = "CV DEFAULT value must be a number between 0 and 65535"
ASSN_MSB = "MSB must be a number between 0 and 127"
ASSN_LSB = "LSB must be a number between 0 and 127"
ASSN_DEPTH = "DEPTH must be 7 or 14"
ASSN_NRPN = "NRPN DEFAULT value must be a number between 0 and 65535"

# AUTOMATION Errors
AUTO = "Syntax error: AUTOMATION must follow format TYPE:VALUE.  Ensure value is the correct format."
AUTO_CC = "CC must be a number between 0 and 127"
AUTO_CV = "CV must be a number between 1 and 4"
AUTO_MSB = "MSB must be a number between 0 and 127"
AUTO_LSB = "LSB must be a number between 0 and 127"
AUTO_DEPTH = "DEPTH must be a 7 or 14"

# Context/Section Errors
CTX_OPEN = "Section definition open must begin with '['"
CTX_OPEN_FMT = "Section definition open text cannot begin with '[/'"
CTX_OPEN_CLOSE = "Section defintion open must end with ']'"
CTX_CLOSE = "Section definition close must begin with '['"
CTX_CLOSE_FMT = "Section definition close text must begin with '/'"
CTX_CLOSE_CLOSE = "Section defintion close must end with ']'"

# General Config Errors
TRACKNAME = "Syntax error: TRACKNAME must be in format: 'TRACKNAME NAME', NAME must be alphanumeric ASCII or one of ' ', '_', '-', '+'"
TYPE = "Syntax error: TYPE must be in format: 'TYPE DEF_TYPE', DEF_TYPE must be one of POLY, DRUM, MPE, or NULL"
OUTPORT = "Syntax error: OUTPORT must be in format: 'OUTPORT PORT', PORT must be one of A, B, C, D, USBD, USBH, CVGx, CVx, Gx, or NULL(x between 1&4)"
OUTCHAN = "Syntax error: OUTCHAN must be in format: 'OUTCHAN CHAN', CHAN must be between 1 and 16 or NULL"
INPORT = "Syntax error: TYPE must be in format: 'INPORT PORT', PORT must be one of NONE, ALLACTIVE, A, B, USBH, USBD, CVG, or NULL"
INCHAN = "Syntax error: INCHAN must be in format: 'INCHAN CHAN', CHAN must be between 1 and 16, ALL, or NULL"
MAXRATE = "Syntax error: MAXRATE must be in format: 'MAXRATE RATE', RATE must be be one of NULL, 192, 96, 64, 48, 32, 24, 16, 12, 8, 6, 4, 3, 2, 1"