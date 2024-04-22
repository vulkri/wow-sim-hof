import subprocess


simc = "./simc_bin"

# Quick sim - running simulationcraft
async def sim_it(name: str = None, simc_filename: str = None) -> int:
    # Provide name or simc file based on user input
    if name:
        args = " armory=eu,burning-legion," + name
    if simc_filename:
        args = " " + simc_filename

    # Run simc binary
    cmd = simc + args
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, shell=True)
    (output, err) = p.communicate()

    p_status = p.wait()
    if p_status != 0:
        return
    output_text = output.splitlines()
    # Get dps from Popen output
    dps_next = False
    for line in output_text:
        if dps_next:
            dps = line.split()[0].decode("utf-8")
            break
        if line.startswith(b"DPS Ranking:"):
            dps_next = True

    return int(dps)