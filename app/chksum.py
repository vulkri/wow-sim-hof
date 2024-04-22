"""
    Adler-32 is a checksum algorithm which was invented by Mark Adler in 1995.
    Compared to a cyclic redundancy check of the same length, it trades reliability for
    speed (preferring the latter).
    Adler-32 is more reliable than Fletcher-16, and slightly less reliable than
    Fletcher-32.[2]

    source: https://en.wikipedia.org/wiki/Adler-32
"""
import zlib

# Check simc string for validity and return character info
def parse_simc_string(simc_string: str = None, simc_filename: str = None) -> dict:
    s = ""
    parsed_data = {}

    # Might not use that block - check if okay to delete after 'vault helper' feature
    if simc_filename:
        with open(simc_filename) as f:
            lines = f.readlines()
            checksum = lines[-1:]
            lines = lines[:-1]
            for line in lines:
                s = s + line

    # Get content and checksum of simc string
    if simc_string:
        lines = simc_string.splitlines()
        checksum = lines[-1:]
        content = lines[:-1]
        for line in content:
                s = s + line + "\n"

    # Compare simc checksum with provided checksum
    checksum = checksum[0][12:]
    calculated_checksum = hex(zlib.adler32(str.encode(s)))[2:]
    if checksum != calculated_checksum:
        return False
    
    # Get character name from simc string
    character_name = lines[0].split(" ")[1]
    parsed_data["character_name"] = character_name

    return parsed_data