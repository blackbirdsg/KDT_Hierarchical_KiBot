"""Run inside the container at /work: add documentation-only layers to the copy."""
import json
from pathlib import Path
import pcbnew

root = Path('/work')
project = root / 'nano-usbc.kicad_pro'
data = json.loads(project.read_text(encoding='utf-8-sig'))
for entry in data['schematic']['top_level_sheets']:
    if entry['filename'] == 'nano-usbc.kicad_sch':
        entry['uuid'] = 'eb460db6-4772-5f8a-8b39-fd5613bbcb9a'
project.write_text(json.dumps(data, indent=2))
board = pcbnew.LoadBoard(str(root / 'nano-usbc.kicad_pcb'))
layers = board.GetEnabledLayers()
names = ['TitlePage', 'F.DNP', 'B.DNP', 'DrillMap', 'F.TestPointList',
         'B.TestPointList', 'F.AssemblyText', 'B.AssemblyText', 'F.Dimensions', 'B.Dimensions']
mapping = {}
for index, name in enumerate(names, start=5):
    layer = getattr(pcbnew, 'User_' + str(index))
    layers.AddLayer(layer)
    mapping[name] = layer
board.SetEnabledLayers(layers)
for name, layer in mapping.items():
    board.SetLayerName(layer, name)
pcbnew.SaveBoard(str(root / 'nano-usbc.kicad_pcb'), board)
(root / 'adapter-record.json').write_text(json.dumps(dict(root_sheet_uuid_corrected=True,
    added_empty_documentation_layers=mapping, note='No routes, components or copper layers intentionally changed.'), indent=2))
