# par2cmdline-turbo.py

This package provides [par2cmdline-turbo](https://github.com/animetosho/par2cmdline-turbo) as a Python package for MacOS, Linux, and Windows; for Python 3.8 and later. Any feedback is welcome!

> [!NOTE]
> This distribution of `par2cmdline-turbo` is currently not affiliated with the official `par2cmdline-turbo` project.

## Motivation

`pip` is a convenient way to install small utilities, even if they aren't pure Python. It also means you can declare them as dependencies and have `pip` or other Python package managers handle the dependency for you. This is may be convenient if you live exclusively in Python-land, but still want to use the very excellent `par2cmdline-turbo`.

## Install

    $ pip install par2cmdline-turbo

## Build

    $ git checkout https://github.com/brenthuisman/par2cmdline-turbo.py.git
    $ pip wheel ./par2cmdline-turbo.py

Optionally, you can "cross-compile" the wheel for other platforms. It actually just downloads the right binary from the `par2cmdline-turbo` releases page. Just set the `TURBO_PLATFORM` environment variable with a supported platform. For instance:

    $ TURBO_PLATFORM=linux-x64 pip wheel ./par2cmdline-turbo.py

Supported platforms: linux-amd64, linux-arm64, linux-armhf, macos-arm64, macos-amd64, win-arm64, win-amd64. You can use `generate-wheels.sh` to generate them all.

## Usage

After install, `par2` should be in your path and usable as upstream `par2cmdline`. See [their usage documentation](https://github.com/Parchive/par2cmdline?tab=readme-ov-file#using-par2cmdline).

## Credits

- Thanks to `@animetosho` for creating ParPar and taking the time to wrap it up as `par2cmdline-turbo`.
- Thanks to `@agriyakhetarpal` for giving me the idea and code with their [hugo-python-distributions](https://github.com/agriyakhetarpal/hugo-python-distributions).
