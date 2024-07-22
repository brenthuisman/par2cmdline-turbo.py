import os
import stat
import platform
import sys
from pathlib import Path
from urllib.request import urlretrieve

from setuptools import Command, Extension, setup
from setuptools.command.bdist_wheel import bdist_wheel
from setuptools.command.build_ext import build_ext


TURBO_BASE_URL = "https://github.com/animetosho/par2cmdline-turbo/releases/tag/v1.1.1/"

# Possible platform tags for wheels
TURBO_PLATFORMTAGS = {
    "linux-amd64": "manylinux_2_17_x86_64",
    "linux-arm64": "manylinux_2_17_aarch64",
    "linux-armhf": "manylinux_2_17_armv7l",
    "macos-arm64": "macosx_11_0_arm64",
    "macos-x64": "macosx_10_9_x86_64",
    "win-arm64": "win_arm64",
    "win-x64": "win_amd64",
    "win-x86": "win32",
}


TURBO_PLATFORM = None
TURBO_PLATFORMTAG = None
TURBO_BINEXT = None

try:
    if os.environ.get("TURBO_PLATFORM") is None:
        THIS_OS = {
            "darwin": "macos",
            "linux": "linux",
            "win32": "win",
        }[sys.platform]
        THIS_ARCH = {
            "x86_64": "x64" if THIS_OS == "macos" else "amd64",
            "AMD64": "x64" if THIS_OS == "macos" else "amd64",
            "arm64": "arm64",
            "aarch64": "arm64",
            "x86": "x86",
            "armv7l": "armhf",
        }[platform.machine()]
        TURBO_PLATFORM = f"{THIS_OS}-{THIS_ARCH}"
    else:
        TURBO_PLATFORM = os.environ.get("TURBO_PLATFORM")
    TURBO_PLATFORMTAG = TURBO_PLATFORMTAGS[TURBO_PLATFORM]
    TURBO_BINEXT = ".exe" if "win" in TURBO_PLATFORM else ""
except KeyError:
    raise SystemExit(
        "The current or requested platform does not support par2cmdline-turbo. "
        + 'Please set "TURBO_PLATFORM" to one of '
        + ", ".join(list(TURBO_PLATFORMTAGS.keys()))
        + "."
    )


class TurboComposer(build_ext):
    """
    Custom extension command that fetches par2cmdline-turbo from upstream.
    """

    def initialize_options(self):
        super().initialize_options()

    def finalize_options(self):
        super().finalize_options()

    def run(self):
        """
        Download par2cmdline-turbo for the requested platform. Default to current platform.

        Requested a build for another platform by setting the TURBO_PLATFORM variable with the corresponding to one of the keys in TURBO_PLATTAGS.
        """
        print(f"Composing par2cmdline wheel for {TURBO_PLATFORM} ...")

        turbourl = f"https://github.com/animetosho/par2cmdline-turbo/releases/download/v1.1.1/par2cmdline-turbo-v1.1.1-{TURBO_PLATFORM}."
        turbourl += "7z" if "win" in TURBO_PLATFORM else "xz"

        destfile, _ = urlretrieve(turbourl)
        destfile = Path(destfile)

        binaries_dir = Path(__file__).parent / "par2" / "binaries"
        if not binaries_dir.exists():
            binaries_dir.mkdir()

        if turbourl.endswith("7z"):
            if sys.platform.startswith("win"):  # build plat may not be target plat
                os.system(f"7z.exe e {destfile} -o{binaries_dir}")
            else:
                os.system(f"7z e {destfile} -o{binaries_dir}")
        else:
            import lzma

            with open(binaries_dir / "par2", "wb") as fout, lzma.open(
                destfile, mode="rb"
            ) as fin:
                fout.write(fin.read())
            os.chmod(
                binaries_dir / "par2",
                os.stat(binaries_dir / "par2").st_mode | stat.S_IEXEC,
            )

        if "win" in TURBO_PLATFORM:
            new_binary_path = binaries_dir / "par2.exe"
            assert new_binary_path.exists()
        else:
            new_binary_path = binaries_dir / "par2"
            assert new_binary_path.exists()


# https://github.com/pypa/setuptools/issues/1347: setuptools does not support
# the clean command from distutils yet. so we need to use a workaround that gets
# called inside bdist_wheel invocation.
class TurboCleaner(Command):
    """
    Custom command that cleans the build directory of the package at the project root.
    """

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

    def run(self):
        """Clean build artifacts at runtime."""
        import shutil

        here = Path(__file__).parent.resolve()
        files_to_clean = "./build ./*.pyc ./*.egg-info ./*/__pycache__ ./__pycache__ ./*/binaries/*".split(
            " "
        )

        for path_spec in files_to_clean:
            # Make paths absolute and relative to this path
            abs_paths = here.glob(path_spec)
            for path in abs_paths:
                if not path.is_relative_to(here):
                    # raise error if path in files_to_clean is absolute + outside
                    # this directory
                    msg = f"{path} is not a path around {here}"
                    raise ValueError(msg)
                if path.is_file():
                    path.unlink()
                if path.is_dir():
                    shutil.rmtree(path)


# Mock setuptools into thinking that we are building a target binary on a host machine
# so that the wheel gets tagged correctly when building or cross-compiling.
class TurboWheel(bdist_wheel):
    """
    A customised wheel build command that sets the platform tags.
    """

    def initialize_options(self):
        super().initialize_options()

    def finalize_options(self):
        super().finalize_options()

    def get_tag(self):
        python_tag, abi_tag, platform_tag = bdist_wheel.get_tag(self)
        # Build for all Python 3 versions and set ABI tag to "none" because
        # the par2cmdline-turbo binary is not a CPython extension, it is a self-contained
        # non-Pythonic binary.
        return "py3", "none", TURBO_PLATFORMTAG

    def run(self):
        self.root_is_pure = False  # ensure that the wheel is tagged as a binary wheel

        self.run_command("clean")  # clean the build directory before building the wheel

        # ensure that the binary is copied into the binaries/ folder and then
        # into the wheel.
        par2_binary = (
            Path(__file__).parent / "par2" / "binaries" / "par2"
        ).with_suffix(TURBO_BINEXT)

        # if the binary does not exist, then we need to build it, so invoke
        # the build_ext command again and proceed to build the binary
        if not Path(par2_binary).exists():
            self.run_command("build_ext")

        # now that the binary exists, we have ensured its presence in the wheel
        super().run()


# https://setuptools.pypa.io/en/latest/userguide/ext_modules.html
setup(
    ext_modules=[
        Extension(
            name="par2.build",
            sources=[
                f"par2/binaries/par2{TURBO_BINEXT}",
            ],
        )
    ],
    cmdclass={
        "build_ext": TurboComposer,
        "clean": TurboCleaner,
        "bdist_wheel": TurboWheel,
    },
    package_data={
        "par2cmdline-turbo": [
            f"binaries/par2{TURBO_BINEXT}",
        ],
    },
)
