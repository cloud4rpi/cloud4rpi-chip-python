# -*- coding: utf-8 -*-

import subprocess


def cpu_temp():
    command = "echo $(sudo i2cget -y -f 0 0x34 0x5e)" + \
              " $(sudo i2cget -y -f 0 0x34 0x5f)"
    msb, lsb = subprocess.check_output(command, shell=True).split()
    return round((int(msb, 0) << 4 | int(lsb, 0) & 15) / 10 - 144.7, 2)


def ip_address():
    try:
        output = subprocess.check_output(['hostname', '-I']).decode().strip()
    except Exception:
        output = 'error'
    return output
