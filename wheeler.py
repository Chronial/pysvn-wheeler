import argparse
import distutils.log
import distutils.version
import distutils.errors
import os
import re
import sys
import shutil
import subprocess
import tempfile
from pathlib import Path

import setuptools
import setuptools.command.build_ext as _build_ext

INNOUNP_EXE = Path(__file__).parent / 'tools/innounp.exe'


class InnoSetupExtension(setuptools.Extension):
    """Extension that consists of an Inno Setup file"""
    def __init__(self, name, sources, version=None, inno_setup=None, *args, **kw):
        """Initializes a new InnoSetupExtension object.

        :param version: version of setup file
        :param inno_setup: path to setup file
        """
        self.version = version
        self.inno_setup = inno_setup

        setuptools.Extension.__init__(self, name, sources, *args, **kw)


class build_ext(_build_ext.build_ext):
    """A specialization of the setuptools command 'build_ext' for processing
    Inno Setup files."""
    def build_extension(self, ext):
        """Builds an extension part of the python package."""
        if isinstance(ext, InnoSetupExtension):
            self.extract_inno_setup(ext)
        else:
            super(build_ext, self).build_extension(ext)

    def extract_inno_setup(self, ext):
        """Extracts app folder of Inno Setup file to corresponding package directory."""
        if not ext.inno_setup.is_file():
            raise distutils.errors.DistutilsFileError('Passed setup path isn\'t valid.')

        package_dir = Path(self.build_lib, ext.name)

        try:
            # extract setup file to package directory
            subprocess.check_output([str(INNOUNP_EXE), '-x', '-y', '-c{app}', '-d' +
                                     str(package_dir), str(ext.inno_setup)],
                                    stderr=subprocess.STDOUT, universal_newlines=True)
        except subprocess.CalledProcessError as e:
            raise distutils.errors.DistutilsExecError('Setup file couldn\'t be extracted.\n'
                                                      + str(e.stdout))


def main():
    p = argparse.ArgumentParser()
    p.add_argument('installer', type=Path,
                   help='pysvn installer to convert')
    p.add_argument('--pysvn-version',
                   help='version number of pysvn')
    args = p.parse_args()

    pysvn_exe = args.installer.absolute()
    if not pysvn_exe.is_file():
        print(f"{pysvn_exe} not found", file=sys.stderr)
        sys.exit(1)

    if args.pysvn_version:
        pysvn_version = args.pysvn_version
    else:
        match = re.search(r'py\d{2}-pysvn-svn\d{3,4}-((?:\d+.){2}\d+)-\d{4}.*.exe$',
                          pysvn_exe.name)
        if not match:
            print("Failed to extract version from pysvn installer name.", file=sys.stderr)
            print("Either give version via --pysvn-version or keep original installer name", file=sys.stderr)
            sys.exit(1)
        pysvn_version = match.group(1)

    # first match will be used
    pysvn_inno_setup = InnoSetupExtension(
        'pysvn', [], version=distutils.version.StrictVersion(pysvn_version),
        inno_setup=pysvn_exe)

    with tempfile.TemporaryDirectory() as temp_dir:
        temp_dir = Path(temp_dir)
        cwd = os.getcwd()
        os.chdir(temp_dir)
        try:
            setuptools.setup(
                script_name="setup.py",
                script_args=["bdist_wheel"],

                name='pysvn',
                version=str(pysvn_inno_setup.version),
                author="Barry Scott",
                author_email="barryscott@tigris.org",
                description="Subversion support for Python",
                long_description=(
                    "The pysvn module is a python interface to the Subversion version control "
                    "system. It depends on the native Apache Subversion client which is part "
                    "of this package. Additionally on Windows platform a VC++ Redistributable "
                    "suitable for your Python version have to be installed."),
                platforms=['win32'],
                url="http://pysvn.tigris.org",
                license="Apache Software License",
                keywords="subversion",
                zip_safe=False,
                cmdclass={'build_ext': build_ext},
                ext_modules=[pysvn_inno_setup],
                classifiers=[
                    'Development Status :: 5 - Production/Stable',
                    'Intended Audience :: Developers',
                    'License :: OSI Approved :: Apache Software License',
                    'Topic :: Software Development :: Version Control',
                    'Environment :: Win32 (MS Windows)',
                    'Operating System :: Microsoft :: Windows'
                ],
            )
        finally:
            os.chdir(cwd)

        unencrypted_wheel = list((temp_dir / "dist").glob("*.whl"))[0]
        shutil.copyfile(unencrypted_wheel, unencrypted_wheel.name)

    print("\nwheel written to:")
    print(unencrypted_wheel.name)


if __name__ == '__main__':
    main()
