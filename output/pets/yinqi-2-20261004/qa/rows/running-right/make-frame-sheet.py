from PIL import Image, ImageDraw
from pathlib import Path
root=Path('D:/Python_code/output/pets/yinqi-2-20261004/qa/rows/running-right')
files=sorted((root/'frames'/'running-right').glob('*.png'))
sheet=Image.new('RGBA',(192*len(files),232),(242,242,242,255))
draw=ImageDraw.Draw(sheet)
for i,p in enumerate(files):
    sheet.alpha_composite(Image.open(p).convert('RGBA'),(i*192,24))
    draw.text((i*192+6,6),f'right {i+1}',fill=(0,0,0,255))
sheet.save(root/'frame-sheet.png')
