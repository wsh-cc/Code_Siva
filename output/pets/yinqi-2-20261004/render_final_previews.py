"""Render supplementary motion evidence from exact validated atlas pixels.

The bundled Pets scripts remain authoritative for assembly and validation.
This helper only crops cells and renders previews required by the contract.
"""
import argparse
import json
from pathlib import Path

import imageio.v2 as imageio
import numpy as np
from PIL import Image, ImageDraw, ImageFont

STATES = [
    ('idle', [280, 110, 110, 140, 140, 320]),
    ('running-right', [120]*7+[220]),
    ('running-left', [120]*7+[220]),
    ('waving', [140]*3+[280]),
    ('jumping', [140]*4+[280]),
    ('failed', [140]*7+[240]),
    ('waiting', [150]*5+[260]),
    ('running', [120]*5+[220]),
    ('review', [150]*5+[280]),
]
LABELS=['待机','开心 · 右移','生气 · 左移','互动','开心 · 轻跃','委屈','撒娇','困倦','害羞']
FONT=ImageFont.truetype(r'C:\Windows\Fonts\msyh.ttc',16)


def gif(frames, durations, path):
    frames[0].save(path, save_all=True, append_images=frames[1:],
                   duration=durations, disposal=2, loop=0, optimize=False)


def card(cell, label):
    canvas = Image.new('RGB', (288, 256), '#f4f1f8')
    canvas.paste(cell, (48, 28), cell)
    ImageDraw.Draw(canvas).text((12, 8), label, fill='#453254',font=FONT)
    return canvas


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('atlas')
    parser.add_argument('output')
    args = parser.parse_args()
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)
    atlas = Image.open(args.atlas).convert('RGBA')
    assert atlas.size in [(1536, 1872), (1536, 2288)]
    rows = []
    sequence, durations = [], []
    for row, (state, timing) in enumerate(STATES):
        frames = [atlas.crop((c*192, row*208, (c+1)*192, (row+1)*208))
                  for c in range(len(timing))]
        rows.append(frames)
        folder = out/'frames'/state
        folder.mkdir(parents=True, exist_ok=True)
        for idx, frame in enumerate(frames):
            frame.save(folder/f'{idx:02d}.png')
            sequence.append(card(frame, f'{LABELS[row]}  {idx+1}/{len(frames)}'))
            durations.append(timing[idx])
    gif(sequence, durations, out/'all-states.gif')
    transition = rows[0] + rows[4] + rows[0]
    transition_timing = STATES[0][1] + STATES[4][1] + STATES[0][1]
    gif(transition, transition_timing, out/'idle-jump-idle-native.gif')
    degrees = ['000','022.5','045','067.5','090','112.5','135','157.5',
               '180','202.5','225','247.5','270','292.5','315','337.5']
    looks = []
    if atlas.height == 2288:
        for idx, degree in enumerate(degrees):
            row, col = 9 + idx//8, idx%8
            cell = atlas.crop((col*192,row*208,(col+1)*192,(row+1)*208))
            looks.append(card(cell, f'视线方向 {degree}°'))
        gif(looks, [220]*16, out/'look-loop.gif')
    chosen = [('待机',0,0),('互动 · 挥手',3,1),('开心 · 轻跃',4,2),('困倦',7,2),
              ('害羞',8,2),('开心 · 右移',1,2),('生气 · 左移',2,2),('撒娇',6,2)]
    proof = Image.new('RGB', (288*4,256*2), '#f4f1f8')
    for idx,(label,row,col) in enumerate(chosen):
        proof.paste(card(rows[row][col],label), ((idx%4)*288,(idx//4)*256))
    proof.save(out/'motion-stills.png')
    fps = 25
    with imageio.get_writer(out/'all-states.mp4', fps=fps, codec='libx264',
                            pixelformat='yuv420p', macro_block_size=16) as writer:
        for frame, ms in zip(sequence,durations):
            for _ in range(max(1,round(ms*fps/1000))):
                writer.append_data(np.asarray(frame))
    report = {'ok':True,'source_atlas':str(Path(args.atlas).resolve()),
              'standard_cells':sum(len(t) for _,t in STATES),
              'look_cells':len(looks),'preview_dir':str(out.resolve())}
    (out/'preview-report.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
    print(json.dumps(report))


if __name__ == '__main__':
    main()
