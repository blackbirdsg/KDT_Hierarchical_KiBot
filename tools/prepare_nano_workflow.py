"""Prepare an isolated Nano/KDT integration fixture, never modify source CAD."""
import hashlib
import json
from pathlib import Path
import shutil

ROOT = Path(__file__).resolve().parents[1]
NANO = ROOT.parent / 'nano-usbc' / 'hardware'
RUN = ROOT / '.local-review' / 'nano-run-20260905'
if RUN.exists():
    raise SystemExit('Run directory exists: refusing to overwrite evidence.')
RUN.mkdir(parents=True)
for name in ['kibot_yaml', 'kibot_resources', 'Templates', 'Logos']:
    shutil.copytree(ROOT / name, RUN / name)
for name in ['kibot_launch.sh', 'LICENSE']:
    shutil.copy2(ROOT / name, RUN / name)
manifest = {}
for source in NANO.iterdir():
    if source.is_file() and (source.suffix in ['.kicad_pcb', '.kicad_sch', '.kicad_pro', '.kicad_dru', '.kicad_sym'] or source.name in ['fp-lib-table', 'sym-lib-table']):
        shutil.copy2(source, RUN / source.name)
        manifest[source.name] = hashlib.sha256(source.read_bytes()).hexdigest()
shutil.copytree(NANO / 'Nano.pretty', RUN / 'Nano.pretty')
(RUN / 'source-manifest.json').write_text(json.dumps(manifest, indent=2))
(RUN / 'CHANGELOG.md').write_text('# Changelog\n\n## [Unreleased]\n\nIsolated Nano A2 documentation trial. NOT FOR FABRICATION.\n')
(RUN / 'README.md').write_text('# Nano A2 workflow trial\n\nNOT FOR FABRICATION. Generated documentation is diagnostic only.\n')
config = RUN / 'kibot_yaml' / 'kibot_main.yaml'
text = config.read_text()
replacements = {
    'PROJECT_NAME: Project Name': 'PROJECT_NAME: Nano USB-C - REVIEW ONLY',
    'BOARD_NAME: Board Name': 'BOARD_NAME: Nano A2 - NOT FOR FABRICATION',
    'COMPANY: Company Name': 'COMPANY: Personal prototype',
    'DESIGNER: Author': 'DESIGNER: Helio',
    "MPN_FIELD: 'Manufacturer Part Number'": "MPN_FIELD: 'MPN'",
    "GIT_URL: 'https://github.com/nguyen-v/KDT_Hierarchical_KiBot'": "GIT_URL: ''",
}
for old, new in replacements.items():
    text = text.replace(old, new)
config.write_text(text)
for name in ['fabrication_notes.txt', 'assembly_notes.txt']:
    (RUN / 'kibot_resources' / 'templates' / name).write_text(
        'NANO A2 - NOT FOR FABRICATION\nDiagnostic KiBot workflow trial only.\n'
        '33 unconnected items and 15 dangling-via warnings in the canonical review.\n'
        'Four copper layers. Stackup and manufacturing acceptance unconfirmed.\n'
        'Hand assembly intended. No order or production release authorized.\n')
print(RUN)
