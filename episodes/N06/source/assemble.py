"""N06 视频合成脚本：基于 timeline.json 和录屏/截图生成最终视频"""
import json
import pathlib
import shutil
import subprocess
import sys
import imageio_ffmpeg
import edge_tts

R = pathlib.Path(__file__).resolve().parent.parent
S = R / 'source'
FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
TL = json.loads((S / 'timeline.json').read_text(encoding='utf-8'))

# 录屏路径
REC_PATH = R / 'assets' / 'recordings'
FRAMES = R / 'frames'
TEMP = R / 'temp' / 'segments'
TEMP.mkdir(parents=True, exist_ok=True)

# 章节配置
CHAPTERS = {
    'intro':    {'type': 'slide', 'frame': 'brand-intro.png'},
    'problem':  {'type': 'slide', 'frame': 'brand-problem.png'},
    'gap':      {'type': 'slide', 'frame': 'brand-gap.png'},
    'solution': {'type': 'slide', 'frame': 'brand-solution.png'},
    'demo-topic':  {
        'type': 'recording',
        'source': 'assets/recordings/20261116-093640.mp4',
        'frame': 'brand-intro.png',
        'start_time': 0,
        'slowdown': 1.1
    },
    'demo-agent':  {
        'type': 'recording',
        'source': 'assets/recordings/20261116-093756.mp4',
        'frame': 'brand-intro.png',
        'start_time': 0,
        'slowdown': 0.75
    },
    'demo-govern': {
        'type': 'recording',
        'source': 'assets/recordings/20261116-093857.mp4',
        'frame': 'brand-intro.png',
        'start_time': 0,
        'slowdown': 0.8
    },
    'when':     {'type': 'slide', 'frame': 'brand-when.png'},
    'outro':    {'type': 'slide', 'frame': 'brand-outro.png'},
}


def build_segment(seg_id, config, seg_duration, output_path):
    if config['type'] == 'slide':
        frame_path = FRAMES / config['frame']
        subprocess.run([
            FFMPEG, '-y', '-v', 'error',
            '-loop', '1', '-framerate', '25',
            '-t', str(seg_duration),
            '-i', str(frame_path),
            '-vf', 'scale=1920:1080,format=yuv420p',
            '-r', '25',
            str(output_path)
        ], check=True)
    elif config['type'] == 'recording':
        rec_path = R / config['source']
        frame_path = FRAMES / config['frame']
        start_time = config.get('start_time', 0)
        slowdown = config.get('slowdown', 1.0)
        rec_duration = seg_duration / slowdown
        pad_after = max(0.0, seg_duration - rec_duration * slowdown)
        inputs = [
            '-loop', '1', '-framerate', '25',
            '-i', str(frame_path),
            '-ss', str(start_time), '-t', str(rec_duration),
            '-i', str(rec_path)
        ]
        filter_complex = (
            f'[1:v]scale=1760:880,setsar=1,'
            f'setpts={slowdown}*PTS,'
            f'tpad=stop_mode=clone:stop_duration={pad_after}[ui];'
            f'[0:v][ui]overlay=80:116:shortest=1,'
            f'format=yuv420p[v]'
        )
        subprocess.run([
            FFMPEG, '-y', '-v', 'error',
            *inputs,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-r', '25',
            str(output_path)
        ], check=True)
    else:
        raise ValueError(f"Unknown type: {config['type']}")


def main():
    print("Generating N06 video...")
    print(f"Total duration: {TL['duration']:.2f}s")
    print(f"Chapters: {len(TL['chapters'])}")

    seg_files = []
    for ci, chapter in enumerate(TL['chapters']):
        seg_duration = chapter['end'] - chapter['start']
        config = CHAPTERS[chapter['id']]
        seg_out = TEMP / f'{ci:02}.mp4'

        print(f"\n[{ci:02}] {chapter['id']}: {chapter['title']} ({seg_duration:.2f}s)")
        build_segment(chapter['id'], config, seg_duration, seg_out)
        seg_files.append(seg_out)

    list_file = TEMP / 'list.txt'
    list_file.write_text(''.join(f"file '{f.resolve()}'\n" for f in seg_files), encoding='utf-8')

    concat_out = R / 'temp' / 'concat.mp4'
    concat_out.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run([
        FFMPEG, '-y', '-v', 'error',
        '-f', 'concat', '-safe', '0',
        '-i', str(list_file),
        '-c', 'copy',
        str(concat_out)
    ], check=True)

    audio_path = R / 'audio' / 'narration.wav'
    srt_path = R / 'N06-自然语言问数与业务语义.srt'
    output_path = R / 'N06-自然语言问数与业务语义.mp4'

    final_inputs = [
        '-i', str(concat_out),
        '-i', str(audio_path)
    ]

    subtitle_style = "FontSize=11,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=8,WrapStyle=3"

    if srt_path.exists():
        import shutil
        srt_temp = R / 'temp' / 'narration.srt'
        shutil.copy(srt_path, srt_temp)
        final_inputs.extend([
            '-vf', f"subtitles=narration.srt:force_style='{subtitle_style}'"
        ])

    import os
    os.chdir(R / 'temp')
    subprocess.run([
        FFMPEG, '-y', '-v', 'warning',
        *final_inputs,
        '-c:v', 'libx264', '-preset', 'medium', '-crf', '19',
        '-c:a', 'aac', '-b:a', '160k',
        '-movflags', '+faststart',
        str(output_path.resolve())
    ], check=True)

    print(f"\n=== 完成 ===")
    print(f"输出: {output_path}")
    print(f"时长: {TL['duration']:.2f} 秒")


if __name__ == '__main__':
    main()
