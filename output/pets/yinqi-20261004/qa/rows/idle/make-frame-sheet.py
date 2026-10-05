from PIL import Image, ImageDraw
from pathlib import Path
root = Path('D:/Python_code/output/pets/yinqi-20261004/qa/rows/idle')
frames = sorted((root / 'frames' / 'idle').glob('*.png'))
sheet = Image.new('RGBA', (192 * len(frames), 232), (242, 242, 242, 255))
draw = ImageDraw.Draw(sheet)
for i, path in enumerate(frames):
    sheet.alpha_composite(Image.open(path).convert('RGBA'), (i * 192, 24))
    draw.text((i * 192 + 8, 6), f'idle {i + 1}', fill=(0, 0, 0, 255))
sheet.save(root / 'frame-sheet.png')
