# Full Nano workflow result

On 2026-09-05 the pinned image was pulled and run successfully as an environment: KiCad 10.0.5, KiBot 1.9.1, Linux/amd64. This supersedes the earlier Docker-unavailable limitation.

The full 29-target output group reached the final archive and HTML navigator on an adapted, isolated Nano copy. Validation failed: exit 38 (`IGNORED_ERRORS`), with 33 unconnected findings, 8 hole-clearance errors and 15 dangling-via warnings. Source CAD hashes remained unchanged. No routing pass or publication occurred.

The complete run report and machine-readable evidence are retained in the separate local Nano project at `nano-usbc/evidence/kibot/2026-09-05-review/` (`RUN-REPORT.md` and `run-summary.json`). They are not uploaded with this tooling repository. Generation is exercised; manufacturing readiness is not established.

The same unchanged snapshot in Windows KiCad 10.0.3 reports 33 unconnected items and 15 dangling-via warnings without the eight hole-clearance errors observed in container KiCad 10.0.5. ERC and schematic parity were clear. This observed version/platform difference needs investigation; no rules were waived.

The isolated integration required correcting a zero root-sheet UUID in project metadata, adding empty documentation layers and supplying a local fixture Git snapshot. Canonical Nano CAD was unchanged. Output limitations include reference-based footprint association warnings, a missing crystal 3D model, incomplete template drawing groups and title-block overlap. The 29 targets include Gerbers, ODB++, drills, BOMs, placement data, schematic/assembly/fabrication PDFs, 3D exports and the HTML navigator. ZIP integrity and output counts were checked; these are not manufacturing acceptance tests.
