import subprocess


def exec_command(command):
    proc = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    stdout = proc.stdout.decode('utf-8')
    stderr = proc.stderr.decode('utf-8')
    if proc.returncode != 0:
        return stdout, stderr, False
    return stdout, stderr, True
