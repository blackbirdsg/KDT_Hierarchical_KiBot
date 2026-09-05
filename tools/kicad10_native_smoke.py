"""Export an isolated copy of the upstream template; this is not a KiBot test."""
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess

ROOT = Path(__file__).resolve().parents[1]
WORK = ROOT / '.local-review' / 'native-smoke'
SOURCE = WORK / 'source'
CLI = Path(r'C:\Program Files\KiCad\10.0\bin\kicad-cli.exe')
SOURCE.mkdir(parents=True, exist_ok=True)
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode().split('\0')
cad = [ROOT / p for p in tracked if p.endswith(('.kicad_sch', '.kicad_pcb', '.kicad_pro', '.kicad_dru'))]
def hashes():
    return {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in cad}
before = hashes()
for name in filter(None, tracked):
    origin = ROOT / name
    if origin.is_file():
        target = SOURCE / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(origin, target)
config = WORK / 'kicad-config'
config.mkdir(exist_ok=True)
env = dict(os.environ, KICAD_CONFIG_HOME=str(config))
stem = SOURCE / 'KDT_Hierarchical_KiBot'
commands = [
    ['--version'],
    ['sch', 'export', 'netlist', '--format', 'kicadxml', '-o', str(WORK / 'template.xml'), str(stem.with_suffix('.kicad_sch'))],
    ['sch', 'export', 'pdf', '-o', str(WORK / 'template.pdf'), str(stem.with_suffix('.kicad_sch'))],
    ['pcb', 'drc', '--format', 'json', '--schematic-parity', '-o', str(WORK / 'drc.json'), str(stem.with_suffix('.kicad_pcb'))],
]
results = []
for arguments in commands:
    result = subprocess.run([str(CLI), *arguments], cwd=SOURCE, env=env, capture_output=True, text=True, encoding='utf-8', errors='replace', timeout=120)
    results.append(dict(arguments=arguments, exit_code=result.returncode, stdout=result.stdout, stderr=result.stderr))
report = dict(scope='Native CLI on isolated upstream template, not KiBot or Nano validation',
              source_hashes_unchanged=before == hashes(), source_sha256=before, commands=results)
if (WORK / 'drc.json').exists():
    report['drc_report'] = json.loads((WORK / 'drc.json').read_text(encoding='utf-8'))
out = ROOT / 'docs' / 'compatibility' / 'evidence' / 'native-smoke.json'
out.parent.mkdir(parents=True, exist_ok=True)
out.write_text(json.dumps(report, indent=2), encoding='utf-8')
print(json.dumps(dict(source_hashes_unchanged=report['source_hashes_unchanged'],
                     commands=[dict(command=r['arguments'][:3], exit_code=r['exit_code']) for r in results]), indent=2))
