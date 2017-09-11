import sys, codecs

MAX_MESSAGE_LENGTH = {0x00: 160, # GSM-7
                      0x04: 140, # 8-bit
                      0x08: 70}  # UCS2

MAX_INT = sys.maxsize
dictItemsIter = dict.items
xrange = range
unichr = chr
toByteArray = lambda x: bytearray(codecs.decode(x, 'hex_codec')) if type(x) == bytes else bytearray(codecs.decode(bytes(x, 'ascii'), 'hex_codec')) if type(x)  == str else x
rawStrToByteArray = lambda x: bytearray(bytes(x, 'latin-1'))

GSM7_BASIC = ('@£$¥èéùìòÇ\nØø\rÅåΔ_ΦΓΛΩΠΨΣΘΞ\x1bÆæßÉ !\"#¤%&\'()*+,-./0123456789:;<=>?¡ABCDEFGHIJKLMNOPQRSTUVWXYZÄÖÑÜ`¿abcdefghijklmnopqrstuvwxyzäöñüà')
GSM7_EXTENDED = {chr(0xFF): 0x0A,
                 #CR2: chr(0x0D),
                 '^':  chr(0x14),
                 #SS2: chr(0x1B),
                 '{':  chr(0x28),
                 '}':  chr(0x29),
                 '\\': chr(0x2F),
                 '[':  chr(0x3C),
                 '~':  chr(0x3D),
                 ']':  chr(0x3E),
                 '|':  chr(0x40),
                 '€':  chr(0x65)}

class Pdu(object):
    """ Encoded SMS PDU. Contains raw PDU data and related meta-information """
    
    def __init__(self, data, tpduLength):
        """ Constructor
        :param data: the raw PDU data (as bytes)
        :type data: bytearray
        :param tpduLength: Length (in bytes) of the TPDU
        :type tpduLength: int
        """
        self.data = data
        self.tpduLength = tpduLength
    
    def __str__(self):
        return str(codecs.encode(self.data, 'hex_codec'), 'ascii').upper()

def encodeSmsSubmitPdu(number, text, reference=0, validity=None, smsc=None, requestStatusReport=True, rejectDuplicates=False, sendFlash=False):
    """ Creates an SMS-SUBMIT PDU for sending a message with the specified text to the specified number
    
    :param number: the destination mobile number
    :type number: str
    :param text: the message text
    :type text: str
    :param reference: message reference number (see also: rejectDuplicates parameter)
    :type reference: int
    :param validity: message validity period (absolute or relative)
    :type validity: datetime.timedelta (relative) or datetime.datetime (absolute)
    :param smsc: SMSC number to use (leave None to use default)
    :type smsc: str
    :param rejectDuplicates: Flag that controls the TP-RD parameter (messages with same destination and reference may be rejected if True)
    :type rejectDuplicates: bool
            
    :return: A list of one or more tuples containing the SMS PDU (as a bytearray, and the length of the TPDU part
    :rtype: list of tuples
    """     
    tpduFirstOctet = 0x01 # SMS-SUBMIT PDU
    if validity != None:
        # Validity period format (TP-VPF) is stored in bits 4,3 of the first TPDU octet
        if type(validity) == timedelta:
            # Relative (TP-VP is integer)
            tpduFirstOctet |= 0x10 # bit4 == 1, bit3 == 0
            validityPeriod = [_encodeRelativeValidityPeriod(validity)]
        elif type(validity) == datetime:
            # Absolute (TP-VP is semi-octet encoded date)
            tpduFirstOctet |= 0x18 # bit4 == 1, bit3 == 1
            validityPeriod = _encodeTimestamp(validity) 
        else:
            raise TypeError('"validity" must be of type datetime.timedelta (for relative value) or datetime.datetime (for absolute value)')        
    else:
        validityPeriod = None
    if rejectDuplicates:
        tpduFirstOctet |= 0x04 # bit2 == 1
    if requestStatusReport:
        tpduFirstOctet |= 0x20 # bit5 == 1
    
    # Encode message text and set data coding scheme based on text contents
    try:
        encodedText = encodeGsm7(text)
    except ValueError:
        # Cannot encode text using GSM-7; use UCS2 instead
        alphabet = 0x08 # UCS2
    else:
        alphabet = 0x00 # GSM-7    
        
    # Check if message should be concatenated
    if len(text) > MAX_MESSAGE_LENGTH[alphabet]:
        # Text too long for single PDU - add "concatenation" User Data Header
        concatHeaderPrototype = Concatenation()
        concatHeaderPrototype.reference = reference
        pduCount = int(len(text) / MAX_MESSAGE_LENGTH[alphabet]) + 1
        concatHeaderPrototype.parts  = pduCount
        tpduFirstOctet |= 0x40
    else:
        concatHeaderPrototype = None
        pduCount = 1
    
    # Construct required PDU(s)
    pdus = []    
    for i in xrange(pduCount):
        pdu = bytearray()
        if smsc:
            pdu.extend(_encodeAddressField(smsc, smscField=True))
        else:
            pdu.append(0x00) # Don't supply an SMSC number - use the one configured in the device 
    
        udh = bytearray()
        if concatHeaderPrototype != None:
            concatHeader = copy(concatHeaderPrototype)
            concatHeader.number = i + 1
            if alphabet == 0x00:
                pduText = text[i*153:(i+1) * 153]
            elif alphabet == 0x08:
                pduText = text[i * 67 : (i + 1) * 67]
            udh.extend(concatHeader.encode())
        else:
            pduText = text
        
        udhLen = len(udh)        
        
        pdu.append(tpduFirstOctet)
        pdu.append(reference) # message reference
        # Add destination number    
        pdu.extend(_encodeAddressField(number))
        pdu.append(0x00) # Protocol identifier - no higher-level protocol
    
        pdu.append(alphabet if not sendFlash else (0x10 if alphabet == 0x00 else 0x18))
        if validityPeriod:
            pdu.extend(validityPeriod)
        
        if alphabet == 0x00: # GSM-7
            encodedText = encodeGsm7(pduText)
            userDataLength = len(encodedText) # Payload size in septets/characters
            if udhLen > 0:
                shift = ((udhLen + 1) * 8) % 7 # "fill bits" needed to make the UDH end on a septet boundary
                userData = packSeptets(encodedText, padBits=shift)
                if shift > 0:
                    userDataLength += 1 # take padding bits into account
            else:
                userData = packSeptets(encodedText)
        elif alphabet == 0x08: # UCS2
            userData = encodeUcs2(pduText)
            userDataLength = len(userData)
          
        if udhLen > 0:            
            userDataLength += udhLen + 1 # +1 for the UDH length indicator byte
            pdu.append(userDataLength)
            pdu.append(udhLen)
            pdu.extend(udh) # UDH
        else:
            pdu.append(userDataLength)
        pdu.extend(userData) # User Data (message payload)
        tpdu_length = len(pdu) - 1
        pdus = str(codecs.encode(pdu, 'hex_codec'), 'ascii').upper()
    return pdus

def _encodeAddressField(address, smscField=False):
    """ Encodes the address into an address field
    
    :param address: The address to encode (phone number or alphanumeric)
    :type byteIter: str
    
    :return: Encoded SMS PDU address field
    :rtype: bytearray
    """
    # First, see if this is a number or an alphanumeric string
    toa = 0x80 | 0x00 | 0x01 # Type-of-address start | Unknown type-of-number | ISDN/tel numbering plan
    alphaNumeric = False    
    if address.isalnum():
        # Might just be a local number
        if address.isdigit():
            # Local number
            toa |= 0x20
        else:
            # Alphanumeric address
            toa |= 0x50
            toa &= 0xFE # switch to "unknown" numbering plan
            alphaNumeric = True
    else:
        if address[0] == '+' and address[1:].isdigit():
            # International number
            toa |= 0x10
            # Remove the '+' prefix
            address = address[1:]
        else:
            # Alphanumeric address
            toa |= 0x50
            toa &= 0xFE # switch to "unknown" numbering plan
            alphaNumeric = True
    if  alphaNumeric:
        addressValue = packSeptets(encodeGsm7(address, False))
        addressLen = len(addressValue) * 2        
    else:
        addressValue = encodeSemiOctets(address)
        if smscField:            
            addressLen = len(addressValue) + 1
        else:
            addressLen = len(address)
    result = bytearray()
    result.append(addressLen)
    result.append(toa)
    result.extend(addressValue)
    return result

def packSeptets(octets, padBits=0):
    """ Packs the specified octets into septets
    
    Typically the output of encodeGsm7 would be used as input to this function. The resulting
    bytearray contains the original GSM-7 characters packed into septets ready for transmission.
    
    :rtype: bytearray
    """
    result = bytearray()    
    if type(octets) == str:
        octets = iter(rawStrToByteArray(octets))
    elif type(octets) == bytearray:
        octets = iter(octets)
    shift = padBits
    if padBits == 0:
        prevSeptet = next(octets)
    else:
        prevSeptet = 0x00
    for octet in octets:
        septet = octet & 0x7f;
        if shift == 7:
            # prevSeptet has already been fully added to result
            shift = 0        
            prevSeptet = septet
            continue            
        b = ((septet << (7 - shift)) & 0xFF) | (prevSeptet >> shift)
        prevSeptet = septet
        shift += 1
        result.append(b)    
    if shift != 7:
        # There is a bit "left over" from prevSeptet
        result.append(prevSeptet >> shift)
    return result

def encodeSemiOctets(number):
    """ Semi-octet encoding algorithm (e.g. for phone numbers)
        
    :return: bytearray containing the encoded octets
    :rtype: bytearray
    """
    if len(number) % 2 == 1:
        number = number + 'F' # append the "end" indicator
    octets = [int(number[i+1] + number[i], 16) for i in xrange(0, len(number), 2)]
    return bytearray(octets)

def encodeGsm7(plaintext, discardInvalid=False):
    """ GSM-7 text encoding algorithm
    
    Encodes the specified text string into GSM-7 octets (characters). This method does not pack
    the characters into septets.
    
    :param text: the text string to encode
    :param discardInvalid: if True, characters that cannot be encoded will be silently discarded 
    
    :raise ValueError: if the text string cannot be encoded using GSM-7 encoding (unless discardInvalid == True)
    
    :return: A bytearray containing the string encoded in GSM-7 encoding
    :rtype: bytearray
    """
    result = bytearray()
    plaintext = str(plaintext)
    for char in plaintext:
        idx = GSM7_BASIC.find(char)
        if idx != -1:
            result.append(idx)
        elif char in GSM7_EXTENDED:
            result.append(0x1B) # ESC - switch to extended table
            result.append(ord(GSM7_EXTENDED[char]))
        elif not discardInvalid:
            raise ValueError('Cannot encode char "{0}" using GSM-7 encoding'.format(char))
    return result

def encodeUcs2(text):
    """ UCS2 text encoding algorithm
    
    Encodes the specified text string into UCS2-encoded bytes.
    
    :param text: the text string to encode
    
    :return: A bytearray containing the string encoded in UCS2 encoding
    :rtype: bytearray
    """
    result = bytearray()
    for b in map(ord, text):
        result.append(b >> 8)
        result.append(b & 0xFF)
    return result
