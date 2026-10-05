"""Correct cross-row scale/baseline after bundled component extraction.

Only uniform transforms of generated pixels. One transform per complete row;
gesture extent and intentional jump offsets are preserved.
"""
import json
import shutil
import statistics
from pathlib import Path
from PIL import Image

R=Path(__file__).resolve().parent
root=R/'frames'
backup=R/'frames-extracted'
if backup.exists():
    raise SystemExit('An extracted-frame backup already exists; inspect before repeating alignment.')
shutil.copytree(root,backup)
idle=[Image.open(p).convert('RGBA') for p in sorted((root/'idle').glob('*.png'))]
target=round(statistics.median(im.getbbox()[3] for im in idle))
target_height=max(im.getbbox()[3]-im.getbbox()[1] for im in idle)
records=[]
for folder in sorted(p for p in root.iterdir() if p.is_dir()):
    paths=sorted(folder.glob('*.png'))
    ims=[Image.open(p).convert('RGBA') for p in paths]
    boxes=[im.getbbox() for im in ims]
    height=max(b[3]-b[1] for b in boxes)
    baseline=boxes[-1][3] if folder.name=='jumping' else round(statistics.median(b[3] for b in boxes))
    scale=target_height/height if folder.name in {'running-left','running-right','failed','review'} else 1.0
    outputs=[]
    for im in ims:
        size=(round(im.width*scale),round(im.height*scale))
        scaled=im.resize(size,Image.Resampling.LANCZOS) if scale!=1 else im.copy()
        x=round(96-96*scale)
        y=round(target-baseline*scale)
        b=scaled.getbbox()
        if b[0]+x<2 or b[1]+y<2 or b[2]+x>190 or b[3]+y>206:
            raise SystemExit(f'Alignment would clip {folder.name}: {b}, offset {x,y}')
        out=Image.new('RGBA',(192,208))
        out.alpha_composite(scaled,(x,y))
        outputs.append(out)
    for path,im in zip(paths,outputs):
        im.save(path)
    records.append({'state':folder.name,'uniform_scale':scale,'source_baseline':baseline,'target_baseline':target,'source_max_height':height,'target_reference_height':target_height,'source_bounds':boxes,'final_bounds':[im.getbbox() for im in outputs]})
(R/'qa/standard-registration.json').write_text(json.dumps({'reason':'Match resting face/body scale across independent source rows; one uniform row transform. Waving hand extent and jumping lift are preserved.','rows':records},indent=2),encoding='utf-8')
print(json.dumps({'target_baseline':target,'reference_height':target_height,'rows':len(records)}))
