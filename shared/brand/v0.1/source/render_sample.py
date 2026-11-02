"""Render a 30-second review sample from versioned frames and audio."""
import hashlib
import json
import pathlib
import re
import subprocess
import wave

from PIL import Image, ImageDraw, ImageFont

ROOT = pathlib.Path(__file__).resolve().parent.parent
PLAN = json.loads((ROOT / 'source/voice-plan.json').read_text())
SHOTS = [('opening', 0, 6, .8), ('concept', 6, 16, 6.5),
         ('ui', 16, 26, 16.5), ('ending', 26, 30, 26.2)]


def run(args):
    subprocess.run(args, check=True)


def ass_time(t):
    cs = round(t * 100)
    return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'


def srt_time(t):
    ms = round(t * 1000)
    return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'


def plain(text):
    return re.sub(r'[\s，。？！；：、“”‘’]', '', text)


def main():
    build = ROOT / 'build'
    build.mkdir(exist_ok=True)
    cues = []
    # Assemble narration at exact sample positions, keeping uncropped speech clips.
    samples = bytearray(30 * 48000 * 2)
    clips = []
    for (scene, start, end, audio_start), line in zip(SHOTS, PLAN['sample']['lines']):
        wav_path = build / f'{scene}.wav'
        run(['ffmpeg', '-y', '-v', 'error', '-i',
             str(ROOT / f'voice/sample-{scene}.mp3'), '-ar', '48000', '-ac', '1',
             '-c:a', 'pcm_s16le', str(wav_path)])
        with wave.open(str(wav_path), 'rb') as stream:
            audio = stream.readframes(stream.getnframes())
        offset = round(audio_start * 48000) * 2
        if offset + len(audio) > end * 48000 * 2:
            raise ValueError('Speech exceeds scene: ' + scene)
        samples[offset:offset + len(audio)] = audio
        events = json.loads((ROOT / f'voice/sample-{scene}.boundaries.json').read_text())
        word_positions = []
        cursor = 0
        full = plain(line['display'])
        for event in events:
            token = plain(event['text'])
            pos = full.find(token, cursor)
            if pos < 0:
                raise ValueError(f'Cannot align token {token!r} in {scene}')
            word_positions.append((pos, pos + len(token), event['offset'] / 1e7,
                                   (event['offset'] + event['duration']) / 1e7))
            cursor = pos + len(token)
        cursor = 0
        for fragment in re.split('[，。？！；]', line['display']):
            if not fragment:
                continue
            a, b = cursor, cursor + len(plain(fragment))
            matches = [w for w in word_positions if w[1] > a and w[0] < b]
            if not matches:
                raise ValueError('No subtitle match: ' + fragment)
            cues.append({'start': audio_start + matches[0][2],
                         'end': min(end - .1, audio_start + matches[-1][3] + .13),
                         'text': fragment})
            cursor = b
        clip = build / f'{scene}.mp4'
        run(['ffmpeg', '-y', '-v', 'error', '-loop', '1', '-framerate', '25',
             '-i', str(ROOT / f'visual/frames/{scene}.png'), '-vf',
             f'fade=t=in:st=0:d=0.18,fade=t=out:st={end-start-.18}:d=0.18',
             '-t', str(end-start), '-an', '-c:v', 'libx264', '-preset', 'fast',
             '-crf', '18', '-pix_fmt', 'yuv420p', str(clip)])
        clips.append(clip)
    with wave.open(str(build / 'narration.wav'), 'wb') as stream:
        stream.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        stream.writeframes(samples)
    (ROOT / '品牌风格样片.srt').write_text(''.join(
        f'{i+1}\n{srt_time(c["start"])} --> {srt_time(c["end"])}\n{c["text"]}\n\n'
        for i, c in enumerate(cues)))
    ass = '''[Script Info]
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,36,&H00FFFFFF,&H00FFFFFF,&H001F1109,&H80000000,0,0,0,0,100,100,0,0,1,1.4,0,2,80,80,26,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
    for c in cues:
        ass += f'Dialogue: 0,{ass_time(c["start"])},{ass_time(c["end"])},Default,,0,0,0,,{{\\fad(50,50)}}{c["text"]}\n'
    ass_path = build / 'sample.ass'
    ass_path.write_text(ass)
    concat = build / 'sample-concat.txt'
    concat.write_text(''.join(f"file '{p}'\n" for p in clips))
    meta = ';FFMETADATA1\ntitle=问学知识平台 · 品牌风格样片 v0.1\n'
    for scene, start, end, _ in SHOTS:
        meta += f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={start*1000}\nEND={end*1000}\ntitle={scene}\n'
    (build / 'sample.ffmeta').write_text(meta)
    video = ROOT / '品牌风格样片.mp4'
    run(['ffmpeg', '-y', '-v', 'warning', '-f', 'concat', '-safe', '0', '-i',
         str(concat), '-i', str(build / 'narration.wav'), '-i',
         str(ROOT / '品牌风格样片.srt'), '-f', 'ffmetadata', '-i',
         str(build / 'sample.ffmeta'), '-vf', 'ass=' + str(ass_path),
         '-map', '0:v', '-map', '1:a', '-map', '2:0', '-map_metadata', '3',
         '-map_chapters', '3', '-af', 'loudnorm=I=-16:TP=-1.5:LRA=9',
         '-c:v', 'libx264', '-crf', '20', '-preset', 'fast', '-pix_fmt', 'yuv420p',
         '-r', '25', '-c:a', 'aac', '-b:a', '192k', '-c:s', 'mov_text',
         '-metadata:s:s:0', 'language=zho', '-disposition:s:0', '0',
         '-t', '30', '-movflags', '+faststart', str(video)])
    run(['ffmpeg', '-v', 'error', '-i', str(video), '-f', 'null', '-'])
    board = Image.new('RGB', (1920, 1140), '#09111f')
    font = ImageFont.truetype('/System/Library/Fonts/PingFang.ttc', 24)
    for i, (scene, _, _, _) in enumerate(SHOTS):
        im = Image.open(ROOT / f'visual/frames/{scene}.png').convert('RGB')
        im.thumbnail((960, 540))
        x, y = (i % 2) * 960, (i // 2) * 570
        board.paste(im, (x, y))
        ImageDraw.Draw(board).text((x + 20, y + 540),
                                  ['片头', '章节与图解', '真实界面', '片尾'][i],
                                  font=font, fill='#adbed4')
    board.save(ROOT / 'visual/风格总览.jpg', quality=92)
    probe = json.loads(subprocess.check_output([
        'ffprobe', '-v', 'error', '-show_streams', '-show_format', '-show_chapters',
        '-of', 'json', str(video)]))
    v = next(s for s in probe['streams'] if s['codec_type'] == 'video')
    assert (v['width'], v['height'], v['codec_name']) == (1920, 1080, 'h264')
    assert abs(float(probe['format']['duration']) - 30) < .1
    assert len(probe['chapters']) == 4
    assert any(s['codec_type'] == 'subtitle' for s in probe['streams'])
    (ROOT / 'source/sample-timeline.json').write_text(json.dumps({
        'duration': 30, 'shots': [dict(id=s, start=a, end=b, voice_start=v)
                                 for s, a, b, v in SHOTS],
        'cues': cues, 'voice_candidate': PLAN['sample']['candidate']
    }, ensure_ascii=False, indent=2) + '\n')
    (ROOT / 'source/sample-verification.json').write_text(json.dumps({
        'duration': float(probe['format']['duration']), 'resolution': [1920, 1080],
        'fps': v['r_frame_rate'], 'chapters': len(probe['chapters']),
        'full_decode': 'passed', 'pronunciation_approval': 'pending',
        'sha256': hashlib.sha256(video.read_bytes()).hexdigest()
    }, ensure_ascii=False, indent=2) + '\n')
    print('30-second sample rendered; pronunciation requires human listening.')


if __name__ == '__main__':
    main()
