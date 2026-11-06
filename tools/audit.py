"""Read-only structure, content duplication, link, and asset integrity audit."""
import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path
import re
from urllib.parse import unquote
from video import media_entries

ROOT = Path(__file__).resolve().parent.parent
EXCLUDED = {'.git', '.venv', 'node_modules', '__pycache__', 'build'}
GENERATED_REPORTS = {'reports/repository-audit.json'}


def digest(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def audit():
    files = [p for p in sorted(ROOT.rglob('*')) if p.is_file()
             and not EXCLUDED.intersection(p.relative_to(ROOT).parts)
             and p.name != '.DS_Store'
             and not (p.parent.name == 'source' and p.name in {'frame.png', 'concat.txt', 'subtitles.ass', 'chapters.ffmeta', 'cut.json'})
             and p.relative_to(ROOT).as_posix() not in GENERATED_REPORTS]
    errors = []
    groups = defaultdict(list)
    folders = defaultdict(lambda: {'files': 0, 'bytes': 0})
    for path in files:
        relative = path.relative_to(ROOT)
        folders[relative.parts[0]]['files'] += 1
        folders[relative.parts[0]]['bytes'] += path.stat().st_size
        groups[digest(path)].append(relative.as_posix())
    policies = json.loads((ROOT / 'standards/保留重复内容.json').read_text())['groups']
    duplicates = []
    for sha256, paths in groups.items():
        if len(paths) < 2:
            continue
        policy = next((p for p in policies if set(p['files']) == set(paths)), None)
        duplicates.append({'sha256': sha256, 'bytes_each': (ROOT / paths[0]).stat().st_size,
                           'files': paths, 'classification': 'intentional' if policy else 'unclassified',
                           'reason': policy['reason'] if policy else '需要人工判断；工具不自动删除'})
    links_checked = 0
    for path in files:
        if path.suffix not in {'.md', '.html'}:
            continue
        text = path.read_text()
        targets = (re.findall(r'\]\(([^)]+)\)', text) if path.suffix == '.md'
                   else re.findall(r'(?:src|href)=[\"\x27]([^\"\x27]+)', text))
        for target in targets:
            if target.startswith(('#', '/', '${')) or re.match(r'[a-zA-Z][\w+.-]*:', target):
                continue
            value = unquote(target.strip('<>').split('#')[0].split('?')[0].split(' "')[0])
            if not value:
                continue
            links_checked += 1
            if not (path.parent / value).is_file():
                errors.append({'file': path.relative_to(ROOT).as_posix(), 'missing_link': target})
    manifests_checked = 0
    for path in files:
        if path.name != 'assets.json':
            continue
        owner = path.parent
        rows = json.loads(path.read_text())['files']
        for row in rows:
            target = (owner / row['path']).resolve()
            if not target.is_relative_to(owner) or not target.is_file():
                errors.append({'file': path.relative_to(ROOT).as_posix(), 'missing_asset': row['path']})
            elif target.stat().st_size != row['bytes'] or digest(target) != row['sha256']:
                errors.append({'file': path.relative_to(ROOT).as_posix(), 'changed_asset': row['path']})
            manifests_checked += 1
        actual = {row['path'] for row in media_entries(owner)}
        if actual != {row['path'] for row in rows}:
            errors.append({'file': path.relative_to(ROOT).as_posix(), 'asset_inventory': 'paths differ'})
    for episode in sorted((ROOT / 'episodes').iterdir()):
        if not episode.is_dir():
            continue
        meta = json.loads((episode / 'episode.json').read_text())
        for key in ('video', 'script', 'reading_copy', 'timeline', 'narration_manifest'):
            if not (episode / meta[key]).is_file():
                errors.append({'episode': episode.name, 'missing_metadata_target': key})
        for name in ('recording.json', 'scene-recordings.json', 'live-recording.json'):
            source = episode / 'source' / name
            if not source.exists():
                continue
            rows = json.loads(source.read_text())
            for row in rows if isinstance(rows, list) else [rows]:
                target = row.get('videoPath', '')
                if target and not target.startswith('build/') and not (episode / target).is_file():
                    errors.append({'episode': episode.name, 'missing_recording': target})
    return {'scope': '当前工作区；排除 .git、build、依赖、缓存和本报告自身',
            'folders': dict(folders), 'files_checked': len(files),
            'local_links_checked': links_checked, 'asset_hashes_checked': manifests_checked,
            'exact_duplicate_groups': duplicates,
            'potential_duplicate_bytes': sum(d['bytes_each'] * (len(d['files']) - 1) for d in duplicates),
            'unclassified_duplicate_groups': sum(d['classification'] == 'unclassified' for d in duplicates),
            'errors': errors}


def main():
    parser = argparse.ArgumentParser(description='检查目录、重复内容、链接和素材哈希；不修改素材')
    parser.add_argument('--output', type=Path, help='可选的 JSON 报告位置')
    args = parser.parse_args()
    report = audit()
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps({'files': report['files_checked'], 'local_links': report['local_links_checked'],
                      'asset_hashes': report['asset_hashes_checked'],
                      'duplicate_groups': len(report['exact_duplicate_groups']),
                      'unclassified_duplicate_groups': report['unclassified_duplicate_groups'],
                      'errors': report['errors']}, ensure_ascii=False))
    if report['errors'] or report['unclassified_duplicate_groups']:
        raise SystemExit(1)


if __name__ == '__main__':
    main()
