# Local development guidance

Development target: **KiCad 10**, branch `kicad-compatibility`. The full local trial used KiCad 10.0.5 and KiBot 1.9.1. Keep documentation explicit about the distinction between tested local generation, failed board validation and the inherited KiCad 8/9 CI workflow.

Read docs/README.md, docs/compatibility/kicad10-review.md and docs/compatibility/migration-plan.md before extending this branch. Workflow knowledge is in docs/knowledge/workflow-handbook.md. The video guide is not a transcript.

Preserve the upstream MIT licence. Persistent local notes belong in docs/, because KiBot regenerates the root README. Use isolated copies for generation: preflights can modify project metadata and board drawings. Keep generated experiments in ignored .local-review/.

Do not treat CHECKED or RELEASED as proof of manufacturing readiness. The inherited DRC configuration allows generation to continue on violations. Do not run automatic publishing workflows, push, order, or upload manufacturing files without user authorization. The existing Nano project's three-pass limit remains exhausted; this tooling task does not authorize another board design pass.

Run tools/test_launcher.py for launcher changes. tools/kicad10_native_smoke.py checks a disposable template copy using the local Windows KiCad installation. It does not validate KiBot, outputs, or a real populated PCB. Record tool versions, input hashes, actual results and remaining gaps. Never rename a summary as a transcript or invent missing video content.
