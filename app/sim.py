import subprocess


simc = "./simc_bin"


async def sim_it(name: str = None, profile_filename: str = None):
    if name:
        args = " armory=eu,burning-legion," + name
    if profile_filename:
        args = " " + profile_filename

    cmd = simc + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()

    p_status = p.wait()
    if p_status != 0:
        return
    output_text = output.splitlines()
    dps_next = False
    for line in output_text:
        if dps_next:
            dps = line.split()[0].decode("utf-8")
            break
        if line.startswith(b"DPS Ranking:"):
            dps_next = True

    return dps