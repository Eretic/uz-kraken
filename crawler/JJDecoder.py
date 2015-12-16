import re
import unittest


OUTPUT = ''


def out(s):
    global OUTPUT
    OUTPUT += s


def lotu(gv, data):
    # lotu
    str_l = "(![]+\"\")[" + gv + "._$_]+"
    str_o = gv + "._$+"
    str_t = gv + ".__+"
    str_u = gv + "._+"

    if data.find(str_l) == 0:
        data = data[len(str_l):]
        return data, 'l'
    elif data.find(str_o) == 0:
        data = data[len(str_o):]
        return data, 'o'
    elif data.find(str_t) == 0:
        data = data[len(str_t):]
        return data, 't'
    elif data.find(str_u) == 0:
        data = data[len(str_u):]
        return data, 'u'
    return data, ''


def decode(text):
    global OUTPUT
    OUTPUT = ''
    text = re.sub(r'/^\s+|\s+$/g', '', text)

    if text.find("\"\'\\\"+\'+\",") == 0:
        # locate jjcode
        start_pos = text.find('$$+"\\""+') + 8;
        end_pos = text.find('"\\"")())()');
        # get gv
        gv = text[text.find('"\'\\"+\'+",') + 9:text.find("=~[]")]
        gvl = len(gv)
    else:
        # get gv
        gv = text[:text.find('=')]
        gvl = len(gv)

        # locate jjcode
        start_pos = text.find('"\\""+') + 5
        end_pos = text.find('"\\"")())()')

    if start_pos == end_pos:
        print('No data')
        return ''

    data = text[start_pos:end_pos]
    # hex decode string
    b = ["___+", "__$+", "_$_+", "_$$+",
         "$__+", "$_$+", "$$_+", "$$$+",
         "$___+", "$__$+", "$_$_+", "$_$$+",
         "$$__+", "$$_$+", "$$$_+", "$$$$+"]

    # # lotu
    # str_l = "(![]+\"\")[" + gv + "._$_]+"
    # str_o = gv + "._$+"
    # str_t = gv + ".__+"
    # str_u = gv + "._+"

    # 0123456789abcdef
    str_hex = gv + "."

    # s
    str_s = '"'
    gvsig = gv + "."

    str_quote = '\\\\\\"'
    str_slash = '\\\\\\\\'

    str_lower = "\\\\\"+"
    str_upper = "\\\\\"+" + gv + "._+"

    str_end = '"+'  # end of s loop

    while data:
        # lotu
        data, lc = lotu(gv, data)
        if lc:
            out(lc)
            continue

        # 0123456789abcdef
        if data.find(str_hex) == 0:
            data = data[len(str_hex):]
            # check every element of hex decode string for a match
            for i in range(len(b)):
                if data.find(b[i]) == 0:
                    data = data[len(b[i]):]
                    out('%x' % i)
                    break
            continue

        # start of s block
        if data.startswith(str_s):
            data = data[len(str_s):]
            # check if "R
            if data.startswith(str_upper):  # r4 n >= 128
                data = data[len(str_upper):]  # skip sig
                ch_str = []
                for j in range(2):  # shouldn't be more than 2 hex chars
                    # gv + "."+b[ c ]
                    if data.startswith(gvsig):
                        data = data[len(gvsig):]  # skip gvsig
                        for k in range(len(b)):  # for every entry in b
                            if data.startswith(b[k]):
                                data = data[len(b[k])]
                                ch_str.append(k)
                                break
                    else:
                        break  # done
                out(''.join([chr(x) for x in ch_str]))
                continue
            elif data.startswith(str_lower):
                data = data[len(str_lower):]  # skip sig
                ch_str = ""
                ch_lotux = ""
                temp = ""
                b_checkR1 = 0

                for j in range(3):  # shouldn't be more than 3 octal chars
                    if j > 1:  # lotu check
                        data, ch_lotux = lotu(gv, data)
                        if ch_lotux:
                            break

                    # gv + "."+b[ c ]
                    if data.startswith(gvsig):
                        temp = data[len(gvsig):]
                        for k in range(8):  # for every entry in b octal
                            if temp.startswith(b[k]):
                                if int(ch_str + str(k), 8) > 128:
                                    b_checkR1 = 1
                                    break
                                ch_str += str(k)
                                data = data[len(gvsig):]  # skip gvsig
                                data = data[len(b[k]):]
                                break

                        if b_checkR1 == 1:
                            if data.startswith(str_hex):
                                data = data[len(str_hex):]
                                # check every element of hex decode string for a match
                                for i in range(len(b)):
                                    if data.find(b[i]) == 0:
                                        data = data[len(b[i]):]
                                        ch_lotux = hex(i)
                                        break
                                break
                    else:
                        break
                out(chr(int(ch_str, 8)) + ch_lotux)
                continue  # step out of the while loop
            else:  # "S ----> "SR or "S+
                # if there is, loop s until R 0r +
                # if there is no matching s block, throw error

                match = 0
                n = 0
                # searching for mathcing pure s block
                while True:
                    n = ord(data[0])
                    if data.startswith(str_quote):
                        data = data[len(str_quote):]
                        out('"')
                        match += 1
                        continue
                    elif data.startswith(str_slash):
                        data = data[len(str_slash):]
                        out('\\')
                        match += 1
                        continue
                    elif data.startswith(str_end):
                        if match == 0:
                            print('+ no match S block: ' + data)
                            return
                        data = data[len(str_end):]
                        break  # step out of the while loop
                    elif data.startswith(str_upper):
                        if match == 0:
                            print('no match S block n>128: ' + data)
                            return
                        data = data[len(str_upper):]
                        ch_str = []
                        for j in range(10):
                            if j > 1:
                                data, ch_lotux = lotu(gv, data)
                                if ch_lotux:
                                    break
                            # gv + "."+b[ c ]
                            if data.startswith(gvsig):
                                data = data[len(gvsig):]
                                for k in range(len(b)):
                                    if data.startswith(b[k]):
                                        data = data[len(b[k]):]
                                        ch_str.append(k)
                                        break
                            else:
                                break  # done
                        out(''.join([chr(x) for x in ch_str]))
                        break  # step out of the while loop
                    elif data.startswith(str_lower):
                        if match == 0:
                            print('no match S block n<128: ' + data)
                            return
                        data = data[len(str_lower):]
                        ch_str = ''
                        b_checkR1 = 0
                        for j in range(3):
                            if j > 1:
                                data, ch_lotux = lotu(gv, data)
                                if ch_lotux:
                                    break
                            # gv + "."+b[ c ]
                            if data.startswith(gvsig):
                                temp = data[len(gvsig):]
                                for k in range(8):
                                    if temp.startswith(b[k]):
                                        if int(ch_str + str(k), 8) > 128:
                                            b_checkR1 = 1
                                            break
                                        ch_str += str(k);
                                        data = data[len(gvsig):]  # skip gvsig
                                        data = data[len(b[k]):];
                                        break
                                if b_checkR1 == 1:
                                    if data.startswith(str_hex):
                                        data = data[len(str_hex):]
                                        for i in range(len(b)):
                                            if data.startswith(b[i]):
                                                data = data[len(b[i]):]
                                                ch_lotux = hex(i)
                                                break
                            else:
                                break  # done
                        out(chr(int(ch_str, 8)) + ch_lotux)
                        break  # step out of the while loop
                    elif (0x21 <= n <= 0x2f) or (0x3A <= n <= 0x40) or (0x5b <= n <= 0x60) or (0x7b <= n <= 0x7f):
                        out(data[0])
                        data = data[1:]
                        match += 1
                continue
        print('No match: ' + data)
        break

    return OUTPUT


class JJDecoderTest(unittest.TestCase):
    def test(self):
        with open('jjdecoder_tests.txt', 'r') as tests:
            while True:
                req = tests.readline()
                if not req:
                    break
                exp = tests.readline().strip()
                result = decode(req)
                self.assertEqual(exp, result)


if __name__ == '__main__':
    unittest.main()
