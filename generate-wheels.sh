#!/usr/bin/env sh
TURBO_PLATFORM=linux-amd64 pip wheel .
TURBO_PLATFORM=linux-arm64 pip wheel .
TURBO_PLATFORM=linux-armhf pip wheel .
TURBO_PLATFORM=macos-arm64 pip wheel .
TURBO_PLATFORM=macos-amd64 pip wheel .
TURBO_PLATFORM=win-arm64 pip wheel .
TURBO_PLATFORM=win-x64 pip wheel .
