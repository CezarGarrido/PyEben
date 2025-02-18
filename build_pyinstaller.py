from argparse import ArgumentParser
from logging import getLogger, StreamHandler
from os.path import dirname, join, exists
from platform import python_compiler
from shlex import split
from shutil import rmtree
from subprocess import CalledProcessError, PIPE, Popen
from sys import exit, stdout, platform
from typing import Dict, Iterator
from venv import create

# Python executable path
if python_compiler()[:3] == "MSC":
    PYEXE = join("Scripts", "python")
else:
    PYEXE = join("bin", "python3")


def run_command(cmd: str, **kwargs: Dict[str, str]) -> Iterator[str]:
    """
    Generator function yielding command outputs
    
    :param cmd: Command
    :type cmd: str
    :param kwargs: Keyword arguments to pass to subprocess.Popen
    :type kwargs: Dict[str, str]
    :return: Output line
    :rtype: Iterator[str]
    """
    if python_compiler()[:3] == "MSC":
        command = cmd.split()
    else:
        command = split(cmd)
    process = Popen(command, stdout=PIPE, shell=False, text=True, **kwargs)
    for line in iter(process.stdout.readline, ""):
        yield line
    process.stdout.close()
    return_code = process.wait()
    if return_code:
        raise CalledProcessError(return_code, cmd)


logger = getLogger("Builder")
logger.setLevel("INFO")
hdlr = StreamHandler(stdout)
logger.addHandler(hdlr)

class Build:
    def __init__(self):
        parser = self._set_up_parser()
        self.args = parser.parse_args()
        self.logger = logger
        self.logger.setLevel(self.args.LOG)
        self.srcdir = dirname(__file__)

    def _set_up_parser(self) -> ArgumentParser:
        parser = ArgumentParser(prog="build.py", description="Builder")
        parser.add_argument("--log", action="store", help="Set the log level", dest="LOG",
                            choices=("DEBUG", "INFO", "WARNING", "ERROR"), default="INFO")
        parser.add_argument("--no-clean", action="store_true", help="Do not clean build artifacts", dest="NO_CLEAN",
                            default=False)
        parser.add_argument("-o", "--outdir", action="store", help="Path to output directory", dest="OUTDIR",
                            default="dist")
        return parser

    def _set_up_venv(self):
        venv = join(self.srcdir, "venv")
        self.logger.info(f"Setting up virtual environment: {venv}")
        create(venv, system_site_packages=True, clear=True, with_pip=True)
        
        self.py = join(venv, PYEXE)
        
        self.logger.info(f"Python executable: {self.py}")  # Adicione esta linha
            
        self._run_command(f"{self.py} -m pip install PyInstaller")
        
        # Verificar se o PyInstaller foi instalado corretamente
        try:
            self._run_command(f"{self.py} -m pyinstaller --version")
            self.logger.info("PyInstaller instalado corretamente.")
        except CalledProcessError:
            self.logger.error("Erro: PyInstaller não foi instalado corretamente. Abortando.")
            exit(1)

        requirements = join(self.srcdir, "requirements.txt")
        if exists(requirements):
            self._run_command(f"{self.py} -m pip install -r {requirements}")

    def _run_command(self, cmd: str):
        self.logger.debug(f"Command: {cmd}")
        for line in run_command(cmd):
            self.logger.info(line)

    def _build(self):
        build_spec = join(self.srcdir, "build.spec")
        if not exists(build_spec):
            self.logger.error("build.spec not found!")
            exit(1)
        self.logger.info("Running pyinstaller with build.spec")
        self._run_command(f"{self.py} -m pyinstaller {build_spec}")
        self.logger.info("Build completed")

    def _clean(self):
        self.logger.info("Removing venv")
        rmtree("venv")
        self.logger.info("Removed venv")

    def main(self):
        self._set_up_venv()
        self._build()
        if not self.args.NO_CLEAN:
            self._clean()
        self.logger.info("Builder completed successfully")
        return 0

if __name__ == "__main__":
    b = Build()
    exit(b.main())
