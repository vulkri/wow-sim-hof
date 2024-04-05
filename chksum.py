"""
    Adler-32 is a checksum algorithm which was invented by Mark Adler in 1995.
    Compared to a cyclic redundancy check of the same length, it trades reliability for
    speed (preferring the latter).
    Adler-32 is more reliable than Fletcher-16, and slightly less reliable than
    Fletcher-32.[2]

    source: https://en.wikipedia.org/wiki/Adler-32
"""
import zlib

def adler32(plain_text: str) -> int:
    """
    Function implements adler-32 hash.
    Iterates and evaluates a new value for each character

    >>> adler32('Algorithms')
    363791387

    >>> adler32('go adler em all')
    708642122
    """
    MOD_ADLER = 65521
    a = 1
    b = 0
    for plain_chr in plain_text:
#        a = (a + ord(plain_chr)) % MOD_ADLER
#        b = (b + a) % MOD_ADLER
        
        a = (a + ord(plain_chr))
        b = (b + a)

    a = a % MOD_ADLER
    b = b % MOD_ADLER

    return (b << 16) + a

s = ""
with open("teshar.txt.bak") as f:
    lines = f.readlines()
    checksum = lines[-1:]
    lines = lines[:-1]

    for line in lines:
        s = s + line
        
file_checksum = ((checksum[0])[12:])
calculated_checksum = hex(zlib.adler32(str.encode(s)))[2:]
if file_checksum != calculated_checksum:
    print("checksum invalid")
else:
    print("checksum valid")