#!/usr/bin/env python3
"""Deliver the entry image to the grader's output folder.

Reads entry.png from this repository, checks it is a real PNG within the
competition's size caps, and copies it to $MAKEFUN_OUTPUT_DIR (or /output).
Standard library only: no network, no clock, no randomness, no image libs.
"""
import os
import shutil
import struct
import sys

REPO_DIR = os.path.dirname(os.path.abspath(__file__))
ENTRY_IMAGE = os.path.join(REPO_DIR, "entry.png")
SIDE_LIMIT = 1024
SIZE_LIMIT = 1024 * 1024
SIGNATURE = b"\x89PNG\r\n\x1a\n"


def abort(reason):
    sys.stderr.write("error: %s\n" % reason)
    sys.exit(1)


def inspect_png(path):
    """Return (width, height, byte_count) for a PNG, or abort if invalid."""
    try:
        with open(path, "rb") as handle:
            blob = handle.read()
    except OSError as exc:
        abort("cannot read %s: %s" % (path, exc))
    if len(blob) < 33:
        abort("entry.png is too short to be a PNG (%d bytes)" % len(blob))
    if blob[:8] != SIGNATURE:
        abort("entry.png does not start with the PNG signature")
    if blob[12:16] != b"IHDR":
        abort("entry.png is missing its IHDR chunk")
    width, height = struct.unpack(">II", blob[16:24])
    return width, height, len(blob)


def run():
    destination = os.environ.get("MAKEFUN_OUTPUT_DIR") or "/output"
    try:
        os.makedirs(destination, exist_ok=True)
    except OSError as exc:
        abort("cannot make output directory %s: %s" % (destination, exc))
    if not os.path.isfile(ENTRY_IMAGE):
        abort("entry image not found: %s" % ENTRY_IMAGE)
    width, height, size = inspect_png(ENTRY_IMAGE)
    if size > SIZE_LIMIT:
        abort("entry.png is %d bytes, over the %d byte limit" % (size, SIZE_LIMIT))
    if width > SIDE_LIMIT or height > SIDE_LIMIT:
        abort("entry.png is %dx%d, over the %d px limit" % (width, height, SIDE_LIMIT))
    target = os.path.join(destination, "entry.png")
    try:
        shutil.copyfile(ENTRY_IMAGE, target)
    except OSError as exc:
        abort("cannot write %s: %s" % (target, exc))
    print("entry.png %dx%d, %d bytes -> %s" % (width, height, size, target))


if __name__ == "__main__":
    run()
