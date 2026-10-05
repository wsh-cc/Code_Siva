"""Diagnostic call to the bundled quality gate's exact look-geometry function.

This does not replace the mandatory complete final quality validation.
"""
import json
import sys
from pathlib import Path
from PIL import Image
sys.path.insert(0,r'C:\Users\wang\.codex\plugins\cache\openai-curated-remote\work-pets\0.1.6\skills\create-pet\scripts')
from validate_pet_quality import inspect_look_registration
atlas=Image.open(sys.argv[1]).convert('RGBA')
continuity=json.loads(Path(sys.argv[2]).read_text(encoding='utf-8'))
errors,warnings=[],[]
metrics=inspect_look_registration(atlas,continuity,26,1.5,errors,warnings)
print(json.dumps({'diagnostic_only':True,'geometry_errors':errors,'metrics':metrics},indent=2))
