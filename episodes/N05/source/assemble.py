"""N05 视频合成脚本：将品牌幻灯片和演示截图/录屏合成为视频"""
import json
import pathlib
import subprocess
import sys

R = pathlib.Path(__file__).resolve().parent.parent
REPO = R.parent.parent

try:
    import imageio_ffmpeg
    FFMPEG = imageio_ffmpeg.get_ffmpeg_exe()
except ImportError:
    FFMPEG = 'ffmpeg'

# 读取时间线
timeline = json.loads((R / 'source' / 'timeline.json').read_text(encoding='utf-8'))
duration = timeline['duration']
chapters = timeline['chapters']

print(f"总时长: {duration:.2f}s ({duration/60:.1f}min)")
print(f"章节数: {len(chapters)}")

# 分镜配置
SEGMENT_CONFIG = {
    'intro': {
        'type': 'slide',
        'frame': 'brand-intro.png'
    },
    'limits': {
        'type': 'slide',
        'frame': 'brand-limits.png'
    },
    'value': {
        'type': 'slide',
        'frame': 'brand-value.png'
    },
    'demo-graph': {
        'type': 'recording',
        'source': 'assets/recordings/20261113-100237.mp4',
        'frame': 'brand-intro.png',
        'start_time': 0,
        'slowdown': 1.2  # 44.34秒章节，使用前37秒录屏
    },
    'demo-agent': {
        'type': 'recording',
        'source': 'assets/recordings/20261113-100237.mp4',
        'frame': 'brand-intro.png',
        'start_time': 80,
        'slowdown': 0.5  # 30.31秒章节，加速2倍
    },
    'comparison': {
        'type': 'slide',
        'frame': 'brand-comparison.png'
    },
    'outro': {
        'type': 'slide',
        'frame': 'brand-outro.png'
    }
}


def get_segment_duration(chapter_id, segment_index, timeline):
    """获取指定章节指定段数的配音时长"""
    chapter_data = None
    for ch in timeline.get('chapters', []):
        if ch['id'] == chapter_id:
            chapter_data = ch
            break

    if not chapter_data or 'segments' not in chapter_data:
        return None

    segments = chapter_data['segments']
    if segment_index >= len(segments):
        return None

    seg = segments[segment_index]
    return seg['end'] - seg['start']


def resolve_timing(timing_config, chapter_id, timeline, default=8):
    """解析时长配置：'segment:N' 或固定数字"""
    if isinstance(timing_config, str) and timing_config.startswith('segment:'):
        seg_idx = int(timing_config.split(':')[1])
        dur = get_segment_duration(chapter_id, seg_idx, timeline)
        return dur if dur else default
    elif isinstance(timing_config, (int, float)):
        return timing_config
    else:
        return default


def generate_segment_video(chapter, config, output_path):
    """为单个章节生成视频片段"""
    start = chapter['start']
    end = chapter['end']
    seg_duration = end - start
    frames = round(seg_duration * 25)

    if config['type'] == 'slide':
        # 纯品牌幻灯片
        frame_path = R / 'frames' / config['frame']
        inputs = [
            '-loop', '1', '-framerate', '25',
            '-i', str(frame_path)
        ]
        filter_complex = '[0:v]setsar=1[v]'

        cmd = [
            FFMPEG, '-y', '-v', 'warning',
            *inputs,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-an',
            '-frames:v', str(frames),
            '-r', '25',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '16',
            '-pix_fmt', 'yuv420p',
            str(output_path)
        ]
        subprocess.run(cmd, check=True)

    elif config['type'] == 'recording':
        # 品牌框架 + 录屏叠加
        rec_path = R / config['source']
        frame_path = R / 'frames' / config['frame']
        start_time = config.get('start_time', 0)
        slowdown = config.get('slowdown', 1.0)

        rec_duration = seg_duration / slowdown

        inputs = [
            '-loop', '1', '-framerate', '25',
            '-i', str(frame_path),
            '-ss', str(start_time), '-t', str(rec_duration),
            '-i', str(rec_path)
        ]

        filter_complex = (
            f'[1:v]scale=1760:880,setsar=1,'
            f'setpts={slowdown}*PTS,'
            f'tpad=stop_mode=clone:stop_duration={seg_duration}[ui];'
            f'[0:v][ui]overlay=80:116:shortest=1[v]'
        )

        cmd = [
            FFMPEG, '-y', '-v', 'warning',
            *inputs,
            '-filter_complex', filter_complex,
            '-map', '[v]',
            '-an',
            '-frames:v', str(frames),
            '-r', '25',
            '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '16',
            '-pix_fmt', 'yuv420p',
            str(output_path)
        ]
        subprocess.run(cmd, check=True)

    elif config['type'] == 'ui':
        # 品牌框架 + UI截图叠加
        sources = config['sources']
        img_duration = seg_duration / len(sources)

        parts = []
        for i, src_item in enumerate(sources):
            if isinstance(src_item, tuple):
                src, timing = src_item
            else:
                src, timing = src_item, None

            if timing:
                img_duration = resolve_timing(timing, chapter['id'], timeline, default=seg_duration / len(sources))

            part_path = R / 'temp' / f'{chapter["id"]}_part{i}.mp4'
            part_path.parent.mkdir(exist_ok=True)

            frame_path = R / 'frames' / config['frame']
            img_path = R / src

            inputs = [
                '-loop', '1', '-framerate', '25',
                '-i', str(frame_path),
                '-loop', '1', '-framerate', '25',
                '-i', str(img_path)
            ]

            part_frames = round(img_duration * 25)
            filter_complex = (
                f'[1:v]scale=1760:880,setsar=1,'
                f'tpad=stop_mode=clone:stop_duration={img_duration}[ui];'
                f'[0:v][ui]overlay=80:116:shortest=1[v]'
            )

            cmd = [
                FFMPEG, '-y', '-v', 'warning',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-an',
                '-frames:v', str(part_frames),
                '-r', '25',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '16',
                '-pix_fmt', 'yuv420p',
                str(part_path)
            ]
            subprocess.run(cmd, check=True)
            parts.append(str(part_path))

        # 合并片段
        if len(parts) > 1:
            concat_file = R / 'temp' / f'{chapter["id"]}_concat.txt'
            with open(concat_file, 'w', encoding='utf-8') as f:
                for p in parts:
                    f.write(f"file '{p}'\n")

            cmd = [
                FFMPEG, '-y', '-v', 'warning',
                '-f', 'concat', '-safe', '0',
                '-i', str(concat_file),
                '-c', 'copy',
                str(output_path)
            ]
            subprocess.run(cmd, check=True)
        else:
            import shutil
            shutil.copy(parts[0], output_path)

    print(f"  生成: {chapter['id']} ({seg_duration:.2f}s)")


def main():
    print("开始合成视频...")

    # 生成每个章节的视频片段
    segment_videos = []
    for chapter in chapters:
        config = SEGMENT_CONFIG.get(chapter['id'])
        if not config:
            print(f"  跳过: {chapter['id']} (无配置)")
            continue

        output_path = R / 'temp' / f'{chapter["id"]}.mp4'
        generate_segment_video(chapter, config, output_path)
        segment_videos.append(str(output_path))

    # 合并所有视频片段
    print("\n合并视频片段...")
    concat_file = R / 'temp' / 'final_concat.txt'
    with open(concat_file, 'w', encoding='utf-8') as f:
        for v in segment_videos:
            f.write(f"file '{v}'\n")

    video_only = R / 'temp' / 'video_only.mp4'
    cmd = [
        FFMPEG, '-y', '-v', 'warning',
        '-f', 'concat', '-safe', '0',
        '-i', str(concat_file),
        '-c', 'copy',
        str(video_only)
    ]
    subprocess.run(cmd, check=True)

    # 检查是否有配音文件
    audio_path = R / 'audio' / 'narration.wav'
    if not audio_path.exists():
        print("\n[WARNING] 配音文件不存在，生成无声视频...")
        final_output = R / 'N05-知识图谱适用场景-nosound.mp4'
        cmd = [
            FFMPEG, '-y', '-v', 'warning',
            '-i', str(video_only),
            '-c:v', 'copy',
            '-t', str(duration),
            str(final_output)
        ]
        subprocess.run(cmd, check=True)
        file_size = final_output.stat().st_size / 1024 / 1024
        print(f"\n=== 合成完成（无配音）===")
        print(f"输出文件: {final_output}")
        print(f"文件大小: {file_size:.1f} MB")
        return

    # 合并音频
    print("合并音频和视频...")
    final_output = R / 'N05-知识图谱适用场景.mp4'

    # 生成字幕文件
    subtitle_path = R / 'N05-知识图谱适用场景.srt'
    generate_subtitles(timeline, subtitle_path)

    # 使用相对路径进行字幕烧录
    subtitle_rel = 'N05-知识图谱适用场景.srt'

    cmd = [
        FFMPEG, '-y', '-v', 'warning',
        '-i', str(video_only),
        '-i', str(audio_path),
        '-vf', f"subtitles={subtitle_rel}:force_style='FontSize=11,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=8,WrapStyle=3'",
        '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
        '-c:a', 'aac', '-b:a', '192k',
        '-shortest',
        str(final_output)
    ]

    try:
        subprocess.run(cmd, check=True)
        print("字幕烧录成功")
    except subprocess.CalledProcessError as e:
        print(f"字幕烧录失败，生成无字幕版本...")
        cmd = [
            FFMPEG, '-y', '-v', 'warning',
            '-i', str(video_only),
            '-i', str(audio_path),
            '-c:v', 'copy',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(final_output)
        ]
        subprocess.run(cmd, check=True)

    file_size = final_output.stat().st_size / 1024 / 1024
    print(f"\n=== 合成完成 ===")
    print(f"输出文件: {final_output}")
    print(f"文件大小: {file_size:.1f} MB")
    print(f"视频时长: {duration:.2f}s ({duration/60:.1f}min)")


def generate_subtitles(timeline, output_path):
    """从时间线生成字幕文件"""
    srt_lines = []
    idx = 1

    for chapter in timeline.get('chapters', []):
        for seg in chapter.get('segments', []):
            start = format_srt_time(seg['start'])
            end = format_srt_time(seg['end'])
            text = seg['text']
            srt_lines.append(f"{idx}\n{start} --> {end}\n{text}\n")
            idx += 1

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write('\n'.join(srt_lines))


def format_srt_time(seconds):
    """将秒数转换为SRT时间格式"""
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    s = int(seconds % 60)
    ms = int((seconds % 1) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"


if __name__ == '__main__':
    main()
