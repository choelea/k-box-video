"""Bind editable narration text to saved audio without depending on archived projects."""
import hashlib
import json


def segments(plan):
    return {f'{ci:02}_{li:02}': text
            for ci, chapter in enumerate(plan)
            for li, text in enumerate(chapter['lines'])}


def validate_existing(project, plan, overrides):
    current = segments(plan)
    rows = overrides['lines']
    requested = {row['stem']: row for row in rows}
    if len(rows) != len(requested):
        raise ValueError('Duplicate speech override stem')
    manifest = json.loads((project / 'source/narration-manifest.json').read_text())
    saved = {row['stem']: row for row in manifest['segments']}
    for stem, row in requested.items():
        if stem not in current or row['formal'] != current[stem]:
            raise ValueError(f'{stem}: synchronize formal text in speech-overrides.json')
    for stem, text in current.items():
        if stem in requested:
            continue
        if stem not in saved or saved[stem]['text'] != text:
            raise ValueError(f'{stem}: changed sentence must be added to speech-overrides.json')
        for extension in ('mp3', 'wav'):
            path = project / 'audio' / f'{stem}.{extension}'
            if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest() != saved[stem][extension + '_sha256']:
                raise ValueError(f'{stem}: saved {extension} changed; regenerate through speech-overrides.json')


def write_manifest(project, plan):
    rows = []
    for stem, text in segments(plan).items():
        row = {'stem': stem, 'text': text}
        for extension in ('mp3', 'wav'):
            row[extension + '_sha256'] = hashlib.sha256(
                (project / 'audio' / f'{stem}.{extension}').read_bytes()).hexdigest()
        rows.append(row)
    (project / 'source/narration-manifest.json').write_text(json.dumps({
        'version': 1, 'note': '现存配音与正式文本的绑定基线；新语境仍待核听',
        'segments': rows}, ensure_ascii=False, indent=2) + '\n')
