"""N07 视频合成脚本：基于 timeline.json 生成最终视频"""
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

FRAMES = R / 'frames'
TEMP = R / 'temp' / 'segments'
TEMP.mkdir(parents=True, exist_ok=True)

# 章节配置（全部使用品牌帧，演示章节待录屏后替换）
CHAPTERS = {
    'intro':   {'type': 'slide', 'frame': 'brand-intro.png'},
    'why':     {'type': 'slide', 'frame': 'brand-why.png'},
    'api':     {'type': 'slide', 'frame': 'brand-api.png'},
    'mcp':     {'type': 'slide', 'frame': 'brand-mcp.png'},
    'skill':   {'type': 'slide', 'frame': 'brand-skill.png'},
    'compare': {'type': 'slide', 'frame': 'brand-compare.png'},
    'demo':    {'type': 'slide', 'frame': 'brand-demo.png'},
    'outro':   {'type': 'slide', 'frame': 'brand-outro.png'},
}


def build_segment(seg_id, config, seg_duration, output_path):
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


def main():
    print("Generating N07 video...")
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
    srt_path = R / 'N07-API-MCP-Skill接入路径.srt'
    output_path = R / 'N07-API-MCP-Skill接入路径.mp4'

    final_inputs = [
        '-i', str(concat_out),
        '-i', str(audio_path)
    ]

    subtitle_style = "FontSize=11,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=8,WrapStyle=3"

    if srt_path.exists():
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
