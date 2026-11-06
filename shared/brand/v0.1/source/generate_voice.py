"""Generate review candidates; never marks any pronunciation as approved."""
import asyncio
import hashlib
import json
import pathlib
import subprocess

import edge_tts

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / 'source/voice-plan.json').read_text())


def run(*args):
    subprocess.run(list(args), check=True)


async def synth(target, text, voice, rate):
    request = {'text': text, 'voice': voice, 'rate': rate, 'engine': 'edge-tts'}
    metadata = target.with_suffix('.request.json')
    if (target.exists() and target.with_suffix('.boundaries.json').exists()
            and metadata.exists() and json.loads(metadata.read_text()) == request):
        return
    events = []
    for attempt in range(3):
        try:
            with target.open('wb') as stream:
                async for part in edge_tts.Communicate(
                        text, voice, rate=rate, boundary='WordBoundary').stream():
                    if part['type'] == 'audio':
                        stream.write(part['data'])
                    elif part['type'] == 'WordBoundary':
                        events.append(part)
            target.with_suffix('.boundaries.json').write_text(
                json.dumps(events, ensure_ascii=False, indent=2) + '\n')
            metadata.write_text(json.dumps(request, ensure_ascii=False, indent=2) + '\n')
            return
        except Exception:
            events.clear()
            if attempt == 2:
                raise
            await asyncio.sleep(attempt + 1)


async def main():
    (ROOT / "review/frames").mkdir(parents=True, exist_ok=True)
    gate = asyncio.Semaphore(3)
    async def candidate(c):
        async with gate:
            for i, formal in enumerate(PLAN['formal_probes']):
                speech = formal.replace('问学知识平台', c['brand_input'])
                target = ROOT / 'voice' / f'{c["id"]}-{i+1}.mp3'
                await synth(target, speech, c['voice'], c['rate'])
                print('generated', target.name, flush=True)
    await asyncio.gather(*(candidate(c) for c in PLAN['candidates']))
    selected = next(c for c in PLAN['candidates'] if c['id'] == PLAN['sample']['candidate'])
    for line in PLAN['sample']['lines']:
        await synth(ROOT / 'voice' / f'sample-{line["id"]}.mp3',
                    line['speech'], selected['voice'], selected['rate'])
    # Normalize each candidate as a complete listening sequence; retain raw clips.
    silence = ROOT / 'build/silence.wav'
    run('ffmpeg', '-y', '-v', 'error', '-f', 'lavfi', '-i',
        'anullsrc=r=48000:cl=mono', '-t', '0.65', str(silence))
    for c in PLAN['candidates']:
        paths = []
        for i in range(3):
            wav = ROOT / 'build' / f'{c["id"]}-{i+1}.wav'
            run('ffmpeg', '-y', '-v', 'error', '-i',
                str(ROOT / 'voice' / f'{c["id"]}-{i+1}.mp3'),
                '-ar', '48000', '-ac', '1', str(wav))
            paths.extend([wav, silence])
        concat = ROOT / 'build' / f'{c["id"]}-concat.txt'
        concat.write_text(''.join(f"file '{p}'\n" for p in paths))
        run('ffmpeg', '-y', '-v', 'error', '-f', 'concat', '-safe', '0',
            '-i', str(concat), '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9',
            '-c:a', 'libmp3lame', '-b:a', '192k',
            str(ROOT / 'voice' / f'candidate-{c["id"]}.mp3'))
    entries = []
    for path in sorted((ROOT / 'voice').glob('*.mp3')):
        duration = float(subprocess.check_output([
            'ffprobe', '-v', 'error', '-show_entries', 'format=duration',
            '-of', 'csv=p=0', str(path)]))
        entries.append({'path': str(path.relative_to(ROOT)), 'duration': duration,
                        'sha256': hashlib.sha256(path.read_bytes()).hexdigest()})
    (ROOT / 'source/voice-manifest.json').write_text(json.dumps({
        'status': 'awaiting-human-listening', 'files': entries,
        'note': 'Audio generation and timing metadata do not prove pronunciation correctness.'
    }, ensure_ascii=False, indent=2) + '\n')


if __name__ == '__main__':
    asyncio.run(main())
