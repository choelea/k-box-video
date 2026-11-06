"""Repository entry point; runs legacy episode scripts from their project root."""
import argparse
import hashlib
import json
import pathlib
import runpy
import subprocess
import sys

ROOT = pathlib.Path(__file__).resolve().parent.parent
MEDIA = {'.mp4', '.webm', '.wav', '.mp3', '.png', '.jpg', '.jpeg', '.mov'}


def read(path):
    return json.loads(path.read_text())


def media_entries(project):
    for path in sorted(project.rglob('*')):
        relative = path.relative_to(project)
        if (path.is_file() and 'build' not in relative.parts
                and relative.as_posix() != 'source/frame.png' and path.suffix.lower() in MEDIA):
            with path.open('rb') as stream:
                digest = hashlib.file_digest(stream, 'sha256').hexdigest()
            yield {'path': relative.as_posix(), 'bytes': path.stat().st_size,
                   'sha256': digest}


def inventory(project):
    (project / 'assets.json').write_text(json.dumps(
        {'version': 1, 'files': list(media_entries(project))}, ensure_ascii=False, indent=2) + '\n')


def check(project):
    meta = read(project / 'episode.json')
    actual = {row['path']: row for row in media_entries(project)}
    expected = {row['path']: row for row in read(project / 'assets.json')['files']}
    if actual != expected:
        changed = sorted(key for key in actual.keys() | expected.keys()
                         if actual.get(key) != expected.get(key))
        raise ValueError('素材清单有变化，请先核查再运行 inventory：' + ', '.join(changed))
    # Check all recording metadata paths used by the imported production scripts.
    for name in ['recording.json', 'scene-recordings.json', 'live-recording.json',
                 'recording-tail.json', 'recording-evidence.json', 'recover.json']:
        path = project / 'source' / name
        if not path.exists():
            continue
        rows = read(path)
        for row in rows if isinstance(rows, list) else [rows]:
            target = row.get('videoPath')
            if target and not target.startswith('build/'):
                resolved = (project / target).resolve()
                if not resolved.is_relative_to(project) or not resolved.is_file():
                    raise ValueError(f'{name} 引用缺失或不在项目内：{target}')
    video = project / meta['video']
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_format', '-show_streams', '-show_chapters',
        '-of', 'json', str(video)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    a = next(s for s in probe['streams'] if s['codec_type'] == 'audio')
    duration = float(probe['format']['duration'])
    if not 120 <= duration <= 420:
        raise ValueError('成片不在 2–7 分钟范围内')
    if (v['width'], v['height'], v['codec_name'], a['codec_name']) != (1920, 1080, 'h264', 'aac'):
        raise ValueError('成片规格与当前基线不符')
    if v['r_frame_rate'] != '25/1':
        raise ValueError('帧率与 25fps 基线不符')
    timeline = read(project / 'source/timeline.json')
    if abs(duration - timeline['duration']) > .2 or abs(duration - meta['duration_seconds']) > .2:
        raise ValueError('成片、时间线与选题卡时长不一致')
    if len(probe['chapters']) != len(timeline['chapters']):
        raise ValueError('章节不完整')
    if not any(s['codec_type'] == 'subtitle' for s in probe['streams']):
        raise ValueError('缺少字幕轨道')
    subprocess.run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'], check=True)
    result = {'episode': str(project.relative_to(ROOT)), 'duration_seconds': duration,
              'media_files': len(actual), 'asset_hashes': 'passed', 'decode': 'passed',
              'pending_content_review': meta.get('pending', [])}
    (project / 'review').mkdir(exist_ok=True)
    (project / 'review/repository-verification.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n')
    print(json.dumps(result, ensure_ascii=False))


def main():
    parser = argparse.ArgumentParser(description='问学视频核验、导出与试看')
    parser.add_argument('action', choices=['check', 'render', 'serve', 'inventory'])
    parser.add_argument('episode', help='例如 N01 或 N02')
    parser.add_argument('--port', type=int, default=8769)
    args = parser.parse_args()
    project = (ROOT / (args.episode if '/' in args.episode else 'episodes/' + args.episode)).resolve()
    if not project.is_relative_to(ROOT) or not (project / 'episode.json').is_file():
        parser.error('不是仓库内有效的视频项目')
    if args.action == 'check':
        check(project)
    elif args.action == 'inventory':
        inventory(project)
        print('已更新素材清单；该操作不代表内容核验通过。')
    elif args.action == 'render':
        (project / 'build').mkdir(exist_ok=True)
        scripts = ['assemble.py', 'finish.py', 'verify.py']
        for name in scripts:
            script = project / 'source' / name
            if name == 'assemble.py' and not script.exists():
                continue
            subprocess.run([sys.executable, str(script)], cwd=project, check=True)
        # Existing scripts may write absolute runtime paths; retain portable metadata.
        path = project / 'source/recording.json'
        record = read(path)
        target = pathlib.Path(record['videoPath'])
        if target.is_absolute():
            record['videoPath'] = target.relative_to(project).as_posix()
            path.write_text(json.dumps(record, ensure_ascii=False, indent=2) + '\n')
        preview = project / 'source/preview.py'
        if preview.exists():
            subprocess.run([sys.executable, str(preview)], cwd=project, check=True)
        inventory(project)
        check(project)
    else:
        sys.argv = ['serve.py', str(project), '--port', str(args.port)]
        runpy.run_path(str(ROOT / 'tools/serve.py'), run_name='__main__')


if __name__ == '__main__':
    main()
