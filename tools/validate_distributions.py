#!/usr/bin/env python3
"""Validate built distributions against the repository's release policy."""

from __future__ import annotations

import argparse
import re
import sys
import tarfile
import zipfile
from pathlib import Path
from typing import Iterator


EMAIL_RE = re.compile(rb"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)
POSIX_HOME_RE = re.compile(rb"/(?:home|Users)/([^/\x00\s]+)/")
WINDOWS_HOME_RE = re.compile(rb"[A-Z]:\\Users\\([^\\\x00\s]+)\\", re.IGNORECASE)
PLACEHOLDER_USERS = {b"user", b"username", b"example", b"testuser"}


def archive_members(path: Path) -> Iterator[tuple[str, bytes]]:
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            for member in archive.infolist():
                if not member.is_dir():
                    yield member.filename, archive.read(member)
        return

    if path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            for member in archive.getmembers():
                if member.isfile():
                    extracted = archive.extractfile(member)
                    if extracted is not None:
                        yield member.name, extracted.read()
        return

    raise ValueError(f"unsupported distribution format: {path}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("artifacts", nargs="+", type=Path)
    parser.add_argument("--allowed-email", action="append", default=[])
    parser.add_argument("--allowed-email-domain", action="append", default=[])
    args = parser.parse_args()

    allowed_emails = {value.casefold() for value in args.allowed_email}
    allowed_domains = {value.casefold() for value in args.allowed_email_domain}
    findings: list[str] = []

    for artifact in args.artifacts:
        for member_name, content in archive_members(artifact):
            name_bytes = member_name.encode("utf-8", errors="surrogateescape")
            inspected = name_bytes + b"\n" + content

            for match in EMAIL_RE.finditer(inspected):
                email = match.group().decode("ascii", errors="replace")
                _, _, domain = email.rpartition("@")
                if email.casefold() not in allowed_emails and domain.casefold() not in allowed_domains:
                    findings.append(f"{artifact.name}:{member_name}: identity policy mismatch")

            for pattern in (POSIX_HOME_RE, WINDOWS_HOME_RE):
                for match in pattern.finditer(inspected):
                    username = match.group(1).lower()
                    if username not in PLACEHOLDER_USERS:
                        findings.append(f"{artifact.name}:{member_name}: path policy mismatch")

    if findings:
        print("distribution validation failed:", file=sys.stderr)
        for finding in sorted(set(findings)):
            print(f"  {finding}", file=sys.stderr)
        return 1

    print("distribution validation passed")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
