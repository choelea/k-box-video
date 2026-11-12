"""N04 配音生成脚本：根据 plan.json 生成 AI 配音和时间线"""
import asyncio
import json
import pathlib
import re
import subprocess
import wave
import sys
import edge_tts

R = pathlib.Path(__file__).resolve().parent.parent
REPO = R.parent.parent

# 读取配置
plan = json.loads((R / 'source' / 'plan.json').read_text(encoding='utf-8'))
pronunciation = json.loads((REPO / 'shared' / 'pronunciation.json').read_text(encoding='utf-8'))
voice_config = pronunciation['selected']

VOICE = voice_config['voice']
RATE = voice_config['rate']
BRAND_INPUT = voice_config['speech_brand_input']

print(f"Using voice: {VOICE}, rate: {RATE}")


async def generate_segment(stem, text):
    """生成单个配音片段"""
    audio_dir = R / 'audio'
    audio_dir.mkdir(exist_ok=True)

    mp3_path = audio_dir / f'{stem}.mp3'
    wav_path = audio_dir / f'{stem}.wav'
    json_path = audio_dir / f'{stem}.json'

    # 品牌词处理
    speech_text = text.replace('问学知识平台', BRAND_INPUT)

    events = []
    for attempt in range(3):
        try:
            with mp3_path.open('wb') as stream:
                async for part in edge_tts.Communicate(
                    speech_text, VOICE, rate=RATE, boundary='WordBoundary'
                ).stream():
                    if part['type'] == 'audio':
                        stream.write(part['data'])
                    elif part['type'] == 'WordBoundary':
                        events.append(part)
            break
        except Exception as e:
            if attempt == 2:
                raise
            print(f'Retry {attempt+1} for {stem}: {e}')
            await asyncio.sleep(attempt + 1)

    # 转换为 WAV
    try:
        import imageio_ffmpeg
        FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
    except ImportError:
        FFMPEG = 'ffmpeg'
    subprocess.run([
        FFMPEG, '-y', '-v', 'error',
        '-i', str(mp3_path),
        '-ar', '48000', '-ac', '1',
        str(wav_path)
    ], check=True)

    # 保存词边界事件
    json_path.write_text(json.dumps(events, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f'Generated: {stem}')
    return events


def plain(t):
    """去除标点"""
    return re.sub(r'[\s，。？！；：、""''（）《》]', '', t)


def stamp(t):
    """生成 SRT 时间戳"""
    ms = round(t * 1000)
    return f'{ms // 3600000:02}:{ms // 60000 % 60:02}:{ms // 1000 % 60:02},{ms % 1000:03}'


async def main():
    print(f"Generating narration for N04...")
    print(f"Total chapters: {len(plan)}")

    # 生成所有配音片段
    for ci, chapter in enumerate(plan):
        for li, text in enumerate(chapter['lines']):
            stem = f'{ci:02}_{li:02}'
            await generate_segment(stem, text)

    # 构建时间线
    clock = 0.65  # 初始静音
    data = bytearray(round(clock * 48000) * 2)
    chapters = []
    cues = []

    for ci, chapter in enumerate(plan):
        c = {**chapter, 'start': clock, 'segments': []}

        for li, text in enumerate(chapter['lines']):
            stem = R / 'audio' / f'{ci:02}_{li:02}'
            wav_path = stem.with_suffix('.wav')

            with wave.open(str(wav_path), 'rb') as stream:
                audio = stream.readframes(stream.getnframes())

            start = clock
            data.extend(audio)
            clock += len(audio) / 96000

            # 读取词边界
            events = json.loads(stem.with_suffix('.json').read_text(encoding='utf-8'))
            positions = []
            cursor = 0
            full = plain(text)

            for ev in events:
                token = plain(ev['text'])
                if not token:
                    continue
                pos = full.find(token, cursor)
                if pos < 0:
                    continue
                positions.append((pos, pos + len(token), ev['offset'] / 1e7, (ev['offset'] + ev['duration']) / 1e7))
                cursor = pos + len(token)

            # 生成字幕 cue
            cursor = 0
            for frag in re.split('[，。？！；：]', text):
                if not frag:
                    continue
                frag = frag.strip()
                if not frag:
                    continue

                # 简单分句（每句不超过 26 字）
                chunks = []
                while len(frag) > 26:
                    cut = frag[:26].rfind('，')
                    if cut < 0:
                        cut = 13
                    chunks.append(frag[:cut + 1])
                    frag = frag[cut + 1:]
                if frag:
                    chunks.append(frag)

                for chunk in chunks:
                    if not chunk:
                        continue
                    a, b = cursor, cursor + len(plain(chunk))
                    matches = [p for p in positions if p[1] > a and p[0] < b]
                    if matches:
                        cues.append({
                            'start': start + matches[0][2],
                            'end': min(clock, start + matches[-1][3] + 0.12),
                            'text': chunk
                        })
                    cursor = b

            c['segments'].append({
                'id': f'{chapter["id"]}-{li+1:02}',
                'text': text,
                'start': start,
                'end': clock
            })

            # 句间停顿
            gap = 0.25 if li + 1 < len(chapter['lines']) else 0.65
            data.extend(b'\0\0' * round(gap * 48000))
            clock += gap

        c['end'] = clock
        chapters.append(c)

    # 尾部静音
    data.extend(b'\0\0' * round(0.7 * 48000))
    clock += 0.7

    # 调整 cue 结束时间
    for i in range(len(cues) - 1):
        cues[i]['end'] = min(cues[i]['end'], cues[i + 1]['start'] - 0.03)

    # 输出音频
    with wave.open(str(R / 'audio' / 'narration.wav'), 'wb') as out:
        out.setparams((1, 2, 48000, 0, 'NONE', 'not compressed'))
        out.writeframes(data)

    # 输出时间线
    timeline = {'duration': clock, 'chapters': chapters, 'cues': cues}
    (R / 'source' / 'timeline.json').write_text(
        json.dumps(timeline, ensure_ascii=False, indent=2) + '\n', encoding='utf-8'
    )

    # 输出字幕
    srt_content = ''.join(
        f'{i+1}\n{stamp(x["start"])} --> {stamp(x["end"])}\n{x["text"]}\n\n'
        for i, x in enumerate(cues)
    )
    (R / 'N04-企业Wiki知识沉淀.srt').write_text(srt_content.rstrip() + '\n', encoding='utf-8')

    # 更新 episode.json
    episode = json.loads((R / 'episode.json').read_text(encoding='utf-8'))
    episode['duration_seconds'] = round(clock, 2)
    episode['status'] = 'audio-generated'
    (R / 'episode.json').write_text(json.dumps(episode, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

    print(f"\n=== 生成完成 ===")
    print(f"总时长: {clock:.2f} 秒 ({clock/60:.1f} 分钟)")
    print(f"章节数: {len(chapters)}")
    print(f"字幕数: {len(cues)}")


if __name__ == '__main__':
    asyncio.run(main())
