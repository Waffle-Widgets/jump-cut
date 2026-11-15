"""Which packages are dirty in memory right now? (Never click the editor's "N Unsaved" button -
it opens a modal Save Content window that freezes the MCP.)

    py <repo>/tools/b1y_dirty.py
Reads only; saves nothing.
"""
import unreal, os, json

OUT = os.path.join(unreal.Paths.convert_relative_path_to_full(unreal.Paths.project_saved_dir()), 'jcpy')
os.makedirs(OUT, exist_ok=True)
rows = []
for p in unreal.EditorLoadingAndSavingUtils.get_dirty_content_packages():
    rows.append(p.get_name())
for p in unreal.EditorLoadingAndSavingUtils.get_dirty_map_packages():
    rows.append('[map] ' + p.get_name())
res = {'count': len(rows), 'packages': sorted(rows)}
with open(os.path.join(OUT, 'b1y_dirty.json'), 'w') as f:
    json.dump(res, f, indent=1)
print('B1Y_DIRTY %d' % len(rows))
