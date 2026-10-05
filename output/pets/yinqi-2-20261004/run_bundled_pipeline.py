"""Orchestrate the authoritative bundled Pets tools; no custom QA gates."""
import argparse
import subprocess
import sys
from pathlib import Path
from PIL import Image

R = Path(__file__).resolve().parent
S = Path(r'C:\Users\wang\.codex\plugins\cache\openai-curated-remote\work-pets\0.1.6\skills\create-pet\scripts')

def run(name, *args):
    subprocess.run([sys.executable, str(S/name), *map(str,args)], check=True)

def main():
    p=argparse.ArgumentParser()
    p.add_argument('stage',choices=['standard','row9','extended','quality'])
    stage=p.parse_args().stage
    (R/'final').mkdir(exist_ok=True)
    if stage=='standard':
        run('extract_strip_frames.py','--decoded-dir',R/'decoded','--output-dir',R/'frames','--method','auto','--chroma-key','#00FF00')
        run('inspect_frames.py','--frames-root',R/'frames','--json-out',R/'qa/review-extracted.json','--require-components')
        subprocess.run([sys.executable,str(R/'align_standard_frames.py')],check=True)
        run('inspect_frames.py','--frames-root',R/'frames','--json-out',R/'qa/review.json','--require-components')
        run('compose_atlas.py','--frames-root',R/'frames','--output',R/'final/spritesheet.png')
        run('make_contact_sheet.py',R/'final/spritesheet.png','--output',R/'qa/contact-sheet.png')
        run('render_animation_previews.py','--frames-root',R/'frames','--output-dir',R/'qa/previews-standard')
        subprocess.run([sys.executable,str(R/'render_final_previews.py'),str(R/'final/spritesheet.png'),str(R/'qa/previews-standard')],check=True)
    elif stage=='row9':
        run('assemble_extended_atlas.py','--base-atlas',R/'final/spritesheet.png','--look-row-9',R/'decoded/look-row-9.png','--registered-row-output',R/'qa/look-row-9-registered.png','--registration-manifest-output',R/'qa/look-row-9-registration.json','--chroma-key','#00FF00')
    elif stage=='extended':
        run('assemble_extended_atlas.py','--base-atlas',R/'final/spritesheet.png','--registered-row-9',R/'qa/look-row-9-registered.png','--row-9-registration',R/'qa/look-row-9-registration.json','--look-row-10',R/'decoded/look-row-10.png','--output',R/'final/spritesheet-extended-raw.png','--chroma-key','#00FF00')
        run('despill_chroma_edges.py',R/'final/spritesheet-extended-raw.png','--output',R/'final/spritesheet-extended.png','--json-out',R/'qa/chroma-despill-extended.json','--chroma-key','#00FF00')
        run('validate_atlas.py',R/'final/spritesheet-extended.png','--require-v2','--chroma-key','#00FF00','--json-out',R/'final/validation-extended.json')
        run('make_contact_sheet.py',R/'final/spritesheet-extended.png','--output',R/'qa/contact-sheet-extended.png')
        run('make_direction_qa_sheet.py',R/'final/spritesheet-extended.png','--output',R/'qa/direction-qa.png')
        run('measure_direction_continuity.py',R/'final/spritesheet-extended.png','--json-out',R/'qa/look-continuity.json')
        subprocess.run([sys.executable,str(R/'render_final_previews.py'),str(R/'final/spritesheet-extended.png'),str(R/'qa/previews-final')],check=True)
        run('render_animation_previews.py','--frames-root',R/'qa/previews-final/frames','--output-dir',R/'qa/previews-final/states')
        run('make_direction_blind_qa_sheet.py',R/'final/spritesheet-extended.png','--output',R/'qa/direction-blind.png','--answer-key',R/'qa/direction-blind-answer-key.json')
        blind=Image.open(R/'qa/direction-blind.png')
        for i,start in enumerate(range(0,14,4)):
            blind.crop((0,start*236,384,min(start+4,14)*236)).save(R/f'qa/direction-blind-part-{i+1}.png')
    else:
        run('validate_pet_quality.py',R/'final/spritesheet-extended.png','--atlas-validation',R/'final/validation-extended.json','--chroma-report',R/'qa/chroma-despill-extended.json','--frame-review',R/'qa/review.json','--direction-semantics',R/'qa/direction-semantics.json','--continuity',R/'qa/look-continuity.json','--json-out',R/'qa/pet-quality.json')

if __name__=='__main__':
    main()
