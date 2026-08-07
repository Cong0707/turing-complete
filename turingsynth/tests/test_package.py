from __future__ import annotations

import unittest

from turingsynth.formats.package import (
    PackageDependency,
    PackageFile,
    SchematicPackage,
    decode_package,
    encode_package,
)


class PackageTests(unittest.TestCase):
    def test_current_package_round_trip_preserves_dependencies(self) -> None:
        package = SchematicPackage(
            level="",
            dependencies=(
                PackageDependency(
                    path="codex/a",
                    files=(PackageFile("circuit.data", b"\x0fchild"),),
                ),
            ),
            main_files=(PackageFile("circuit.data", b"\x0fmain"),),
        )

        payload = encode_package(package)
        self.assertEqual(payload[0], 0)
        self.assertEqual(decode_package(payload), package)


if __name__ == "__main__":
    unittest.main()
