import random
import re
import sre_parse

ascii_lowercase = "abcdefghijklmnopqrstuvwxyz"
ascii_uppercase = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
ascii_letters = ascii_lowercase + ascii_uppercase
digits = "0123456789"
punctuation = " !\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~"
control = "\t\v\f\r"
newline = "\n"
printable = digits + ascii_letters + punctuation + control + newline
printableNotNL = digits + ascii_letters + punctuation + control

limit = 10


xeger_cache = {}


def xeger_cached(er: str):
    if er not in xeger_cache:
        xeger_cache[er] = Xeger(er)

    return xeger_cache[er].generate()


class Xeger:
    def __init__(self, regex: str) -> str:
        self.re = sre_parse.parse(regex)

    def generate(self):
        s = ""
        for x in self.re:
            s += self.generate_from_regexp(x)
            print(s)
        return s

    def generate_from_regexp(self, reg) -> str:
        match reg[0]:
            case sre_parse.LITERAL:
                return chr(reg[1])
            case sre_parse.MAX_REPEAT:
                rpt_sub = reg[1][2]
                rpt = reg[1][0]
                if reg[1][0] != reg[1][1]:
                    if reg[1][1] == re._constants.MAXREPEAT:
                        rpt = random.randint(1, limit)
                    else:
                        rpt = random.randint(reg[1][0], reg[1][1])
                    print("RE RPT ", rpt)
                return self.generate_from_subexp(rpt_sub, rpt)
            case sre_parse.IN:
                s = ""
                for r in reg[1]:
                    s += chr(random.randint(r[1][0], r[1][1]))
                return s
            case sre_parse.SUBPATTERN:
                ss = ""
                for x in reg[1][3]:
                    ss += self.generate_from_regexp(x)
                return ss
            case _:
                print("Skipped:", reg)
        return ""

    def generate_from_subexp(self, reg, count) -> str:
        s = ""
        for _ in range(0, count):
            for sub in reg:
                s += self.generate_from_regexp(sub)

        return s
