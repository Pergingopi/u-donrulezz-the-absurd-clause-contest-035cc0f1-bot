"""Publish one absurd terms-of-service clause to ``entry.txt``.

The clause is a single deadpan sentence (1-200 characters) that reads like
ordinary legal boilerplate until the absurdity lands: your shadow, licensed
and sold to third parties. This module checks the text against the
competition gate, then writes it atomically into the output directory --
a staging file inside that directory, ``os.replace``, an fsync, an explicit
0644 mode, and a read-back check that the published bytes are exactly the
validated payload.

Run it with::

    MAKEFUN_OUTPUT_DIR=/output python3 main.py
"""

import os
import stat
import sys
import unicodedata

CLAUSE = (
    "By using this service, you agree that your shadow may be licensed, "
    "sublicensed, or sold to third parties for promotional purposes."
)

GATE_MIN = 1
GATE_MAX = 200
ENTRY_FILENAME = "entry.txt"


def _reject_bom_and_c1(text):
    """Refuse a byte-order mark or any C1 control character."""
    if "\ufeff" in text:
        return "BOM (U+FEFF) is not allowed"
    for char in text:
        code = ord(char)
        if 0x80 <= code <= 0x9F:
            return "C1 control character U+%04X is not allowed" % code
    return None


def _reject_separators_and_surrogates(text):
    """Refuse line/paragraph separators and surrogate code points."""
    for char in text:
        code = ord(char)
        if code in (0x2028, 0x2029):
            return "line/paragraph separator U+%04X is not allowed" % code
        if 0xD800 <= code <= 0xDFFF:
            return "surrogate U+%04X is not allowed" % code
    return None


def _reject_invisible_categories(text):
    """Refuse control, format and otherwise invisible characters."""
    for char in text:
        code = ord(char)
        category = unicodedata.category(char)
        if category == "Cc":
            return "control character U+%04X is not allowed" % code
        if category in ("Cf", "Zl", "Zp", "Cs"):
            return "invisible character U+%04X is not allowed" % code
    return None


def _forbidden_character(text):
    """Return the first reason *text* fails the character rules, or None."""
    for checker in (
        _reject_bom_and_c1,
        _reject_separators_and_surrogates,
        _reject_invisible_categories,
    ):
        reason = checker(text)
        if reason is not None:
            return reason
    return None


def _check_gate_shape(text):
    """Return a reason when *text* breaks the gate's shape rules, or None."""
    if not text or not text.strip():
        return "entry is empty or whitespace-only"
    if text != text.strip():
        return "entry has leading or trailing whitespace"
    if len(text) < GATE_MIN or len(text) > GATE_MAX:
        return "entry is %d characters, outside the %d-%d gate" % (
            len(text),
            GATE_MIN,
            GATE_MAX,
        )
    if "\n" in text or "\r" in text:
        return "entry must be a single line"
    return None


def check_entry_text(text):
    """Raise ValueError unless *text* passes every gate rule."""
    reason = _check_gate_shape(text)
    if reason is not None:
        raise ValueError(reason)
    reason = _forbidden_character(text)
    if reason is not None:
        raise ValueError(reason)


def resolve_output_directory():
    """Return the output directory from the environment, default /output."""
    raw = os.environ.get("MAKEFUN_OUTPUT_DIR", "")
    path = os.path.abspath(raw.strip() or "/output")
    if path == os.path.abspath(os.sep):
        raise ValueError("refusing to use the filesystem root as output dir")
    if os.path.exists(path) and not os.path.isdir(path):
        raise ValueError("output path %r is a file, not a directory" % path)
    return path


def sweep_output_files(path):
    """Delete every plain file inside *path*; never *path* itself.

    Subdirectories are left alone: the grader may mount other content
    beside our file, and removing a directory we do not own (or cannot
    empty as the grader's user) must not fail the run.
    """
    os.makedirs(path, exist_ok=True)
    for name in os.listdir(path):
        target = os.path.join(path, name)
        if os.path.isdir(target) and not os.path.islink(target):
            continue
        os.unlink(target)


def _write_fully(fd, data):
    """Write every byte of *data* to file descriptor *fd*."""
    view = memoryview(data)
    while view:
        written = os.write(fd, view)
        if written == 0:
            raise OSError("short write while publishing entry")
        view = view[written:]


def _fsync_directory(path):
    """Best-effort fsync of *path* so the rename is durable."""
    try:
        fd = os.open(path, os.O_RDONLY)
    except OSError:
        return
    try:
        os.fsync(fd)
    except OSError:
        pass
    finally:
        os.close(fd)


def _verify_published_file(destination, payload, output_dir):
    """Check the published file: exact bytes, mode 0644, no stray files."""
    with open(destination, "rb") as handle:
        written = handle.read()
    if written != payload:
        raise OSError("read-back mismatch after publishing entry")
    mode = stat.S_IMODE(os.stat(destination).st_mode)
    if mode != 0o644:
        raise OSError("entry.txt mode is %o, expected 0644" % mode)
    stray = [
        name
        for name in os.listdir(output_dir)
        if name != ENTRY_FILENAME
        and not (
            os.path.isdir(os.path.join(output_dir, name))
            and not os.path.islink(os.path.join(output_dir, name))
        )
    ]
    if stray:
        raise OSError("output directory holds files other than entry.txt")


def publish_entry_atomically(text, output_dir):
    """Atomically publish *text* as entry.txt inside *output_dir*."""
    check_entry_text(text)
    sweep_output_files(output_dir)
    payload = text.encode("utf-8")
    staging = os.path.join(output_dir, ".entry-%d.tmp" % os.getpid())
    if os.path.lexists(staging):
        os.unlink(staging)
    fd = os.open(staging, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    try:
        _write_fully(fd, payload)
        os.fsync(fd)
    finally:
        os.close(fd)
    os.chmod(staging, 0o644)
    destination = os.path.join(output_dir, ENTRY_FILENAME)
    # The rename is the atomic step: readers see the old file or the new
    # one, never a half-written staging file.
    os.replace(staging, destination)
    _fsync_directory(output_dir)
    _verify_published_file(destination, payload, output_dir)
    return destination


def run():
    """Validate the clause and publish it; return the process exit code."""
    output_dir = resolve_output_directory()
    destination = publish_entry_atomically(CLAUSE, output_dir)
    print("wrote %s (%d characters)" % (destination, len(CLAUSE)))
    return 0


if __name__ == "__main__":
    sys.exit(run())
