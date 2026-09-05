"""Archive the completed diagnostic run, verify source hashes, inspect exports."""
import collections
import csv
import hashlib
import json
from pathlib import Path
import re
import shutil
import zipfile
from pypdf import PdfReader

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / '.local-review/nano-run-20260905'
DEST = ROOT.parent / 'nano-usbc/evidence/kibot/2026-09-05-review'
DEST.mkdir(parents=True, exist_ok=True)
for name in ['3D', 'HTML', 'Images', 'KiRI', 'Manufacturing', 'Reports', 'Schematic',
             'Testing', 'gate', 'visual-review', 'kibot_yaml', 'kibot_resources', 'Templates', 'Logos']:
    if (RUN / name).exists():
        shutil.copytree(RUN / name, DEST / name, dirs_exist_ok=True)
inputs = DEST / 'inputs'
inputs.mkdir(exist_ok=True)
for source in RUN.iterdir():
    if source.is_file():
        if source.suffix in ['.kicad_sch', '.kicad_pcb', '.kicad_pro', '.kicad_sym', '.kicad_dru'] or source.name in ['sym-lib-table', 'fp-lib-table']:
            shutil.copy2(source, inputs / source.name)
        elif source.suffix in ['.log', '.exit', '.json', '.txt', '.net', '.xml', '.sh'] or source.name == 'LICENSE':
            shutil.copy2(source, DEST / source.name)
shutil.copytree(RUN / 'Nano.pretty', inputs / 'Nano.pretty', dirs_exist_ok=True)
shutil.copy2(RUN / 'README.md', DEST / 'generated-README.md')
shutil.copy2(RUN / 'README.md', DEST / 'README.md')
for name in ['prepare_nano_workflow.py', 'adapt_nano_fixture.py', 'collect_nano_run.py']:
    shutil.copy2(ROOT / 'tools' / name, DEST / name)
source_manifest = json.loads((RUN / 'source-manifest.json').read_text())
unchanged = {name: hashlib.sha256((ROOT.parent / 'nano-usbc/hardware' / name).read_bytes()).hexdigest() == digest
             for name, digest in source_manifest.items()}
log = (RUN / 'full-workflow-06.log').read_text(encoding='utf-8', errors='replace')
targets = re.findall(r"^- '.*?' \(([^)]+)\) \[([^]]+)\]", log, re.M)
with (DEST / 'Manufacturing/Assembly/nano-usbc-bom.csv').open(newline='', encoding='utf-8-sig') as f:
    bom = list(csv.DictReader(f))
with (DEST / 'Manufacturing/Assembly/nano-usbc-CPL.csv').open(newline='', encoding='utf-8-sig') as f:
    positions = list(csv.DictReader(f))
pdfs = {}
for relative in ['Schematic/nano-usbc-schematic.pdf', 'Manufacturing/Assembly/nano-usbc-assembly.pdf',
                 'Manufacturing/Fabrication/nano-usbc-fabrication.pdf']:
    reader = PdfReader(DEST / relative)
    pdfs[relative] = dict(pages=len(reader.pages))
archives = {}
for source in (DEST / 'Manufacturing/Fabrication').glob('*.zip'):
    with zipfile.ZipFile(source) as archive:
        archives[source.name] = dict(entries=len(archive.namelist()), corrupt_entry=archive.testzip())
def drc_summary(filename):
    data = json.loads((DEST / 'gate' / filename).read_text(encoding='utf-8-sig'))
    return dict(kicad_version=data.get('kicad_version'),
                violations=dict(collections.Counter(v['type'] for v in data['violations'])),
                unconnected_items=len(data.get('unconnected_items', [])),
                schematic_parity=len(data.get('schematic_parity', [])))
summary = dict(status='FAIL - DIAGNOSTIC OUTPUTS ONLY', image='ghcr.io/inti-cmnb/kicad10_auto_full@sha256:dd3b846da945f204fa7b61916df34a99170b2a2095b49c3879cd96d414b8a7b8',
    versions=(RUN / 'versions.txt').read_text().splitlines(),
    workflow_exit=int((RUN / 'full-workflow-06.exit').read_text()), workflow_exit_meaning='IGNORED_ERRORS',
    output_targets_attempted=[dict(name=n, type=t) for n, t in targets],
    canonical_inputs_unchanged=unchanged, bom_quantity=sum(int(row['Quantity Per PCB']) for row in bom),
    placement_rows=len(positions), placement_sides=dict(collections.Counter(row['Side'] for row in positions)),
    pdfs=pdfs, archives=archives, baseline_drc=drc_summary('drc.json'),
    windows_comparison_drc=drc_summary('drc-windows-10.0.3.json'),
    erc_exit=int((DEST / 'gate/erc.exit').read_text()), drc_exit=int((DEST / 'gate/drc.exit').read_text()),
    limitations=['Missing crystal model', 'Reference fallback for schematic/PCB association',
                 'Missing template documentation groups', 'Document title-block overlap; not presentation-ready',
                 'No physical test, CAM acceptance or production approval'])
(DEST / 'run-summary.json').write_text(json.dumps(summary, indent=2))
manifest = {str(p.relative_to(DEST)): dict(bytes=p.stat().st_size, sha256=hashlib.sha256(p.read_bytes()).hexdigest())
            for p in DEST.rglob('*') if p.is_file() and p.name != 'artifact-manifest.json'}
(DEST / 'artifact-manifest.json').write_text(json.dumps(manifest, indent=2))
print(json.dumps(dict(destination=str(DEST), targets=len(targets), files=len(manifest),
                     source_unchanged=all(unchanged.values()), summary=summary), indent=2))
