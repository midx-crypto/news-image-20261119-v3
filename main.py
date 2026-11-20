#!/usr/bin/env python3
"""news-image-20261119 entrypoint (Python 3.13, standard library only).

Copies the pre-rendered entry.png beside this file to
$MAKEFUN_OUTPUT_DIR/entry.png (or /output/entry.png in the grader).
No network, no rendering at run time: the same bytes every run.
"""
import hashlib
import os
import shutil
import struct
import sys
import zlib
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = Path(os.environ.get("MAKEFUN_OUTPUT_DIR", "/output"))
MAX_BYTES = 1048576
MAX_DIM = 1024


def png_dimensions(data):
    """Return (width, height) of a PNG from its IHDR chunk, else None."""
    if len(data) < 33 or data[:8] != b"\x89PNG\r\n\x1a\n":
        return None
    if data[12:16] != b"IHDR":
        return None
    w, h = struct.unpack(">II", data[16:24])
    return w, h


def png_wellformed(data):
    """Check the PNG chunk chain: every chunk's CRC matches, ends at IEND."""
    pos = 8
    seen_iend = False
    while pos + 8 <= len(data):
        length = struct.unpack(">I", data[pos:pos + 4])[0]
        ctype = data[pos + 4:pos + 8]
        end = pos + 8 + length + 4
        if end > len(data):
            return False
        crc_stored = struct.unpack(">I", data[end - 4:end])[0]
        crc_calc = zlib.crc32(ctype + data[pos + 8:pos + 8 + length]) & 0xFFFFFFFF
        if crc_stored != crc_calc:
            return False
        pos = end
        if ctype == b"IEND":
            seen_iend = True
            break
    return seen_iend and pos == len(data)


def main():
    src = HERE / "entry.png"
    data = src.read_bytes()
    if len(data) > MAX_BYTES:
        sys.exit(f"entry.png too large: {len(data)} bytes > {MAX_BYTES}")
    dims = png_dimensions(data)
    if dims is None:
        sys.exit("entry.png is not a PNG")
    if dims[0] > MAX_DIM or dims[1] > MAX_DIM:
        sys.exit(f"entry.png too large: {dims[0]}x{dims[1]} > {MAX_DIM}x{MAX_DIM}")
    if not png_wellformed(data):
        sys.exit("entry.png PNG chunk chain is not well formed")
    OUT.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(src, OUT / "entry.png")
    print(f"entry.png written to {OUT / 'entry.png'}")
    print(f"size={len(data)} bytes sha256={hashlib.sha256(data).hexdigest()} "
          f"dimensions={dims[0]}x{dims[1]}")


if __name__ == "__main__":
    main()
