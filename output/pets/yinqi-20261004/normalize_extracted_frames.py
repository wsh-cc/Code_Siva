"""Correct row extraction scale for coherent idle/jump playback.

Apply one uniform transform to every frame of a row. Preserve vertical jump
displacement. Use bundled scripts afterward for inspection and composition.
"""
import argparse
import json
from pathlib import Path
from statistics import median

from PIL import Image


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('frames')
    parser.add_argument('--rest-height',type=int,default=162)
    args = parser.parse_args()
    root = Path(args.frames)
    states = ['idle','running-right','running-left','waving','jumping',
              'failed','waiting','running','review']
    idle = Image.open(root/'idle'/'00.png').convert('RGBA')
    idle_box = idle.getbbox()
    normal_scale = args.rest_height/(idle_box[3]-idle_box[1])
    reports = []
    for state in states:
        files = sorted((root/state).glob('*.png'))
        images = [Image.open(p).convert('RGBA') for p in files]
        boxes = [im.getbbox() for im in images]
        if state == 'jumping':
            rest_height = median([boxes[0][3]-boxes[0][1],
                                  boxes[-1][3]-boxes[-1][1]])
            scale = args.rest_height/rest_height
            ground = max(boxes[0][3], boxes[-1][3])-1
        else:
            scale = normal_scale
            ground = median(b[3]-1 for b in boxes)
        affine = (1/scale,0,96-96/scale,0,1/scale,ground-202/scale)
        for p, im in zip(files,images):
            fitted = im.transform((192,208),Image.Transform.AFFINE,affine,
                                  resample=Image.Resampling.BICUBIC)
            fitted.save(p)
        reports.append({'state':state,'shared_row_scale':scale,
                        'source_ground_y':ground,'target_ground_y':202,
                        'source_bboxes':boxes,
                        'output_bboxes':[Image.open(p).getbbox() for p in files]})
    result = {'purpose':'Shared row scale and ground registration correction',
              'idle_rest_height':args.rest_height,'rows':reports}
    (root/'normalization-report.json').write_text(json.dumps(result,indent=2),
                                                 encoding='utf-8')
    print(json.dumps(result,indent=2))


if __name__ == '__main__':
    main()
