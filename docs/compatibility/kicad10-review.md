# KiCad 10 compatibility review

Update: Docker is now available and the full Nano output group has been exercised. See [the actual run](nano-full-run.md); it supersedes the earlier untested-container statements below. The pipeline generated its outputs but returned a failed validation status.

Reviewed 2026-09-05. Upstream: [nguyen-v/KDT_Hierarchical_KiBot](https://github.com/nguyen-v/KDT_Hierarchical_KiBot), commit `079a4ecd0e4bd50d8df339bb6126caf9e9403bf6`. Local branch: `kicad-compatibility`. Source CAD remains unchanged. The repository is MIT licensed; that licence is not assumed to cover its linked video.

## Assessment

The template is a useful documentation framework, but switching its version number to 10 is insufficient. Local launch selection and CI routing need changes, while its generated documentation and manufacturing outputs require a real KiBot 10 test. It must not yet be used to release manufacturing files.

| Priority | Finding and affected file | Consequence / action |
| --- | --- | --- |
| Critical | `.github/workflows/ci.yaml` has execution steps only for KiCad 8 and 9 | Setting `kicad_version: 10` can skip generation while later commit/release operations remain. Add a tested 10 path and enforce output completeness before publishing. CI is intentionally unchanged and unexecuted here. |
| Critical | `kibot_yaml/kibot_pre_drc_report.yaml` uses `dont_stop: true` | A CHECKED/RELEASED label can coexist with DRC failures and a manufacturing ZIP. Add a separate gate that stops on violations before packaging. This inherited issue is documented, not yet fixed. |
| High | `kibot_launch.sh` originally recognizes only an exact 9.x.x string | KiCad 10 falls back to the older group and loses the 9+ fabrication group. Local patch selects by major version and rejects unsupported versions. |
| High | Docker launchers expose only 8/9 images | Local patch adds explicit `-v 10` using KiBot 1.9.1. Existing defaults are retained. Old launchers still mount the user's home; Linux also mounts `/etc/shadow`. Use the new limited read-only environment probe for initial inspection. |
| High | KiBot owns the KiCad API integration | Pin a recent compatible KiBot image. Do not assume changing template YAML repairs Python API, plotting, drill, or zone-fill regressions. |
| High | Main YAML disables zone-fill checking; globals suppress several warnings | Restore review visibility and verify filled zones explicitly before manufacture. Hidden missing-model/version/output warnings can mask migration problems. |
| High | Stackup, tables, drawings and assembly documentation depend on named groups and custom layers | Test group retention, layer mappings, fonts, worksheets and generated PDF content on a populated board, not merely successful file creation. |
| High | Native KiCad 10 variants and template KiBoM variants are different systems | Keep the template variant model initially; verify component fitted/DNP status and VARIANT text semantics before adopting native variants. |
| High | Template `.kicad_dru` describes a particular six-layer PCBWay construction | It is not a universal PCBWay profile and must not replace the Nano's four-layer rules. Select manufacturer process/stackup first, then establish rules for that board. |
| Medium | 3D rendering and model retrieval change with newer KiBot/KiCad | Check camera, crop, transparency and model coverage. Do not assume old WRL download paths or GUI render settings work identically. |
| Medium | Position output includes both board sides and non-SMD parts | Validate placement origin, units, bottom-side angles and exclusions against the intended assembler, even if this Nano is hand soldered. |
| Medium | `get_sheet_title.py` assumes an XML title element exists | Test empty sheet titles and hierarchical exports; caught exceptions can become text output rather than a failed workflow. |

The inherited launcher's command construction uses `eval`; only trusted arguments should be supplied until it is refactored to argument arrays. This assessment is not a complete security audit.

## Changes in this branch

- Major-version dispatch for KiCad 8, 9 and 10; unsupported/failed detection stops generation.
- The second KiBot invocation no longer runs after the first invocation fails.
- `all_group_k10` explicitly aliases the existing 9+ group. This preserves intended output selection; it does not certify those outputs.
- Both legacy Docker launchers accept version 10 with `ghcr.io/inti-cmnb/kicad10_auto_full:1.9.1`.
- `docker_kibot_review.ps1` provides a read-only, project-only, digest-pinned environment probe without home mounts or published ports. It only prints KiCad/KiBot versions; it is not a generation command.
- Added regression tests, isolated native smoke procedure and knowledge documentation.

No automatic CI execution, release, source CAD conversion or Nano routing has been performed.

## Dependency evidence

[KiBot 1.9.1](https://github.com/INTI-CMNB/KiBot/releases/tag/v1.9.1), published 2026-07-28, was the latest release returned by the upstream API during this review. The [maintainer's KiCad 10 support discussion](https://github.com/INTI-CMNB/KiBot/discussions/901) records support beginning with 1.9.0 and subsequent API/CLI workarounds. Relevant issues include board deletion and singleton groups, zone filling, plotting/drill crashes and schematic parity. Treat this as a reason to pin and test versions, not proof that every feature is broken in the current release.

[Native variant limitations](https://github.com/INTI-CMNB/KiBot/discussions/906) and [3D model format changes](https://github.com/INTI-CMNB/KiBot/discussions/905) require particular attention. The [container project](https://github.com/INTI-CMNB/kicad_auto) documents the image families.

The public registry returned HTTP 200 for `ghcr.io/inti-cmnb/kicad10_auto_full:1.9.1`, resolving to manifest digest `sha256:dd3b846da945f204fa7b61916df34a99170b2a2095b49c3879cd96d414b8a7b8`. The new probe pins that digest. The image was not pulled or run; its bundled KiCad patch version and architecture were not measured. Local KiCad is 10.0.3. In particular, the maintainer discusses fixes in 10.0.4 that must not be assumed present in local 10.0.3.

## Validation boundary

The mocked launcher tests passed all four tests, including four supported version strings, unsupported versions, version-command failure and first-generation failure. These prove command selection and stop behavior only.

Native exports operate on a disposable copy; local machine-readable evidence in `docs/compatibility/evidence/native-smoke.json` records command output, exit status and unchanged source hashes. Generated diagnostics are not uploaded with the tooling repository. Native CLI export success does not exercise KiBot's preflights, custom documentation layers, renderers or production packaging.

The native schematic XML/PDF exports completed. The DRC run reported one error: the template has no board outline on Edge.Cuts. It reported zero unconnected items and zero schematic parity issues; these results on a template are not meaningful validation of a populated PCB. The command returned zero because this diagnostic invocation did not request a violation-based exit code. Registry-access warnings were also emitted under the sandbox, despite using an isolated KiCad configuration directory. Shell syntax checks and the read-only Docker probe's dry run passed.

The Docker client is installed but the engine was unavailable. Full KiBot execution, Gerber/drill inspection, 3D visual comparisons and CI parity remain open. See the [migration plan](migration-plan.md). This branch is not manufacturing-ready.
