from PIL import Image, ImageDraw
from pathlib import Path
import json, sys
sys.path.insert(0, 'C:/Users/wang/.codex/plugins/cache/openai-curated-remote/work-pets/0.1.6/skills/create-pet/scripts')
from extract_strip_frames import remove_chroma_background, component_frame_groups, component_bounds
root = Path('D:/Python_code/output/pets/yinqi-20261004/qa/rows/jumping')
frames = sorted((root / 'frames' / 'jumping').glob('*.png'))
sheet = Image.new('RGBA', (192 * len(frames), 232), (242,242,242,255))
draw = ImageDraw.Draw(sheet)
bounds=[]
for i,path in enumerate(frames):
    cell=Image.open(path).convert('RGBA')
    sheet.alpha_composite(cell, (i*192,24))
    draw.text((i*192+8,6), f'jumping {i+1}', fill=(0,0,0,255))
    bounds.append(cell.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox())
sheet.save(root / 'frame-sheet.png')
source=remove_chroma_background(Image.open(root.parents[2]/'decoded'/'jumping.png'),(0,255,0),96)
source_bounds=[component_bounds(g) for g in component_frame_groups(source,5)]
idle=Image.open(root.parent/'idle'/'frames'/'idle'/'00.png').convert('RGBA')
idle_bounds=idle.getchannel('A').point(lambda v:255 if v>16 else 0).getbbox()
result={'source_size':source.size,'source_bounds':source_bounds,'source_heights':[b[3]-b[1] for b in source_bounds],'source_baselines':[b[3] for b in source_bounds],'extracted_bounds':bounds,'extracted_heights':[b[3]-b[1] for b in bounds],'extracted_baselines':[b[3] for b in bounds],'extracted_lift':max(b[3] for b in bounds)-min(b[3] for b in bounds),'idle_bounds':idle_bounds,'landing_delta':abs(bounds[-1][3]-idle_bounds[3])}
(root/'geometry.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
