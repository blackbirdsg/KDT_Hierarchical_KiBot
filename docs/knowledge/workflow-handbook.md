# Repository-based workflow handbook

Provenance: this handbook summarizes the MIT-licensed [upstream repository](https://github.com/nguyen-v/KDT_Hierarchical_KiBot/tree/079a4ecd0e4bd50d8df339bb6126caf9e9403bf6), reviewed 2026-09-05. It is not based on an obtained video transcript. Preserve upstream licence attribution when reusing its files.

## Intended pipeline

The project combines a hierarchical KiCad template with KiBot output definitions, documentation templates and GitHub automation. CAD metadata and repository revision information feed notes, drawings, BOMs and fabrication outputs. Generated Markdown also replaces the project README. The intended benefit is repeatable documentation from the same engineering source, rather than manually updating each deliverable.

`kibot_launch.sh` is the local entry point. It selects a stage/variant, obtains a revision from the changelog unless supplied, and invokes `kibot_yaml/kibot_main.yaml`. That file imports the detailed output/preflight definitions. Named output groups collect document, fabrication and other deliverables. The 9+ group includes fabrication outputs unavailable in the older selection.

## Stage meanings

| Stage | Template behavior | Interpretation for future work |
| --- | --- | --- |
| DRAFT | Schematic-oriented outputs; several checks/preflights skipped | Work in progress |
| PRELIMINARY | Broader schematic/PCB documentation; ERC and DRC skipped | Review documents, not production approval |
| CHECKED | Broader output group with check preflights requested | Verify actual reports and stop conditions; the name is insufficient |
| RELEASED | Similar generation with release metadata | Use only after a separate acceptance decision |

These are KiBoM/template variants and lifecycle labels. Do not automatically map them to KiCad 10 native component variants.

## Metadata and layout contracts

Maintain sheet titles and hierarchy, project title/revision variables, changelog, and documentation inputs together. The XML export drives sheet/title extraction and text-variable generation. Some preflights alter project or PCB content, so generation is not a purely read-only operation.

Documentation expects named layers such as `TitlePage`, `F.DNP`, `B.DNP`, `DrillMap`, `F.TestPointList`, `B.TestPointList`, `F.AssemblyText` and `B.AssemblyText`. Groups including `kibot_fancy_stackup`, `kibot_table_*` and `kibot_image_*` anchor generated content. Copying YAML without these conventions can produce incomplete drawings or wrong placement. Preserve and test the associated worksheet, color, font and resource files.

The stackup and `.kicad_dru` are board-specific. Never import a template's six-layer fabrication assumptions into a four-layer board simply because both use PCBWay.

## Deliverables and review

Treat schematic PDF, assembly/fabrication drawings, BOM, placement data, 3D images and manufacturing archive as separate output families with explicit content checks. A successful command and a ZIP file do not prove electrical correctness or manufacturability. Check component counts, fitted state, layer presence, drill registration and human-readable drawings.

Cost generation is optional and has its own local configuration. Do not add credentials to version control or request external services merely to validate basic documentation.

## Local and hosted execution

The upstream workflow automates Git operations as well as generation. It can commit generated files and publish releases; its tag/changelog handling deserves review before adoption. Start with local, disposable input copies and output-only review. Keep CI publishing disabled until equivalent local and hosted runs are proven.

Legacy Docker launchers expose broad home-directory access. The new `docker_kibot_review.ps1` limits its mount to the project and makes it read-only, but is only a version probe. A future generation launcher should use isolated writable inputs/outputs, avoid mounting the entire home, and record exact dependency versions.

## Agent handoff checklist

- Read the compatibility review and actual evidence before claiming support.
- Identify the source commit and current branch changes; do not confuse this scaffold with a completed port.
- State which board, layer stackup, variants and output families are being qualified.
- Keep authoritative engineering notes in `docs/`, outside generated README content.
- Preserve source hashes and logs; label untested steps explicitly.
- Use the separate video guide only for navigation. No full transcript was obtained.
