"""N03 视频合成脚本：将截图、录屏和配音合成为最终视频（N01/N02 风格）"""
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

# 分镜配置：每个章节对应的截图/录屏素材
# type: 'slide' = 纯品牌幻灯片, 'ui' = 品牌框架 + 截图叠加, 'mixed' = 截图 + 录屏混合
# screenshot_timing: 截图时长配置，基于配音内容卡点
#   - 'segment:N' = 使用第N段配音的时长
#   - 数字 = 固定秒数
# recordings: 录屏序列列表，按顺序播放
SEGMENT_CONFIG = {
    'intro': {
        'type': 'slide',
        'frame': 'brand-intro.png'
    },
    'overview': {
        'type': 'slide',
        'frame': 'brand-overview.png'
    },
    'document': {
        'type': 'mixed',
        'frame': 'brand-intro.png',
        'intro_frame': 'brand-document-intro.png',
        'intro_timing': 'segment:0',  # 使用第1段配音时长（介绍性文字）
        'sources': [
            ('frames/v3-shouhou-files.png', 3)  # 截图缩短为3秒
        ],
        'recordings': [
            ('assets/recordings/知识库文件详情.mp4', 8),  # 详情展示（固定8秒）
            ('assets/recordings/知识问答 - Trim.mp4', 'segment:2')  # 问答流程（使用第3段配音时长）
        ]
    },
    'wiki': {
        'type': 'mixed',
        'frame': 'brand-intro.png',
        'intro_frame': 'brand-wiki-intro.png',
        'intro_timing': 'segment:0',  # 第二类是企业Wiki...
        'sources': [
            ('frames/v3-wiki-pages.png', 3),
            ('frames/v3-wiki-content.png', 3)
        ],
        'recordings': [
            ('assets/recordings/Wiki库详情.mp4', 'full'),  # 完整播放详情（~18秒）
            ('assets/recordings/Wiki库问答.mp4', 'full')  # 完整播放问答（~17秒）
        ]
    },
    'graph': {
        'type': 'mixed',
        'frame': 'brand-intro.png',
        'intro_frame': 'brand-graph-intro.png',
        'intro_timing': 'segment:0',  # 第三类是知识图谱...
        'sources': [
            ('frames/v3-graph-list.png', 3),  # 截图缩短为3秒
            ('frames/v3-graph-visual.png', 3)  # 截图缩短为3秒
        ],
        'recordings': [
            ('assets/recordings/图谱库详情.mp4', 10),  # 详情展示（固定10秒）
            ('assets/recordings/图谱问答 - Trim.mp4', 'segment:3')  # 图谱问答查询演示
        ]
    },
    'insight': {
        'type': 'mixed',
        'frame': 'brand-intro.png',
        'intro_frame': 'brand-insight-intro.png',
        'intro_timing': 'segment:0',  # 第四类是数据洞察...
        'sources': [
            ('frames/v3-insight-list.png', 3),  # 截图缩短为3秒
            ('frames/v3-insight-tables.png', 3)  # 截图缩短为3秒
        ],
        'recordings': [
            ('assets/recordings/数据主题详情.mp4', 10),  # 详情展示（固定10秒）
            ('assets/recordings/数据洞察问答 - Trim - Trim.mp4', 'segment:3')  # 数据洞察问答演示
        ]
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
        duration = get_segment_duration(chapter_id, seg_idx, timeline)
        return duration if duration else default
    elif isinstance(timing_config, (int, float)):
        return timing_config
    else:
        return default


def generate_segment_video(chapter, config, output_path):
    """为单个章节生成视频片段（N01/N02 风格：品牌框架 + UI 叠加）"""
    start = chapter['start']
    end = chapter['end']
    seg_duration = end - start
    frames = round(seg_duration * 25)  # 25fps

    if config['type'] == 'slide':
        # 纯品牌幻灯片：直接使用品牌页面
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

    elif config['type'] == 'ui':
        # 品牌框架 + 截图叠加（N01/N02 风格）
        sources = config['sources']
        img_duration = seg_duration / len(sources)

        # 生成每张截图的视频片段
        parts = []
        for i, src in enumerate(sources):
            part_path = R / 'temp' / f'{chapter["id"]}_part{i}.mp4'
            part_path.parent.mkdir(exist_ok=True)

            frame_path = R / 'frames' / config['frame']
            img_path = R / src

            # 品牌框架作为底层，截图缩放到 1760x880 并叠加在 (80, 116) 位置
            inputs = [
                '-loop', '1', '-framerate', '25',
                '-i', str(frame_path),
                '-loop', '1', '-framerate', '25',
                '-i', str(img_path)
            ]

            # 截图缩放 + 叠加 + 时长控制
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

    elif config['type'] == 'record':
        # 品牌框架 + 录屏叠加（N01/N02 风格）
        rec_path = R / config['source']
        frame_path = R / 'frames' / config['frame']

        inputs = [
            '-loop', '1', '-framerate', '25',
            '-i', str(frame_path),
            '-ss', '0', '-t', str(seg_duration),
            '-i', str(rec_path)
        ]

        # 录屏缩放 + 叠加 + 时长补齐
        filter_complex = (
            f'[1:v]scale=1760:880,setsar=1,'
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

    elif config['type'] == 'mixed':
        # 品牌框架 + 介绍页 + 截图序列 + 录屏混合
        sources = config['sources']
        intro_frame = config.get('intro_frame')
        intro_timing = config.get('intro_timing', 8)

        parts = []
        chapter_id = chapter['id']
        total_duration = 0  # 累计实际时长

        # 1. 生成介绍页面部分（如果有）
        if intro_frame:
            intro_duration = resolve_timing(intro_timing, chapter_id, timeline)
            intro_part_path = R / 'temp' / f'{chapter_id}_intro.mp4'
            intro_frame_path = R / 'frames' / intro_frame

            intro_inputs = [
                '-loop', '1', '-framerate', '25',
                '-i', str(intro_frame_path)
            ]

            intro_frames = round(intro_duration * 25)
            intro_filter = '[0:v]setsar=1[v]'

            cmd = [
                FFMPEG, '-y', '-v', 'warning',
                *intro_inputs,
                '-filter_complex', intro_filter,
                '-map', '[v]',
                '-an',
                '-frames:v', str(intro_frames),
                '-r', '25',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '16',
                '-pix_fmt', 'yuv420p',
                str(intro_part_path)
            ]
            subprocess.run(cmd, check=True)
            parts.append(str(intro_part_path))
            total_duration += intro_duration

        # 2. 生成截图序列部分（固定3秒/张）
        for i, src_item in enumerate(sources):
            if isinstance(src_item, tuple):
                src, timing = src_item
            else:
                src, timing = src_item, 3

            img_duration = resolve_timing(timing, chapter_id, timeline, default=3)

            part_path = R / 'temp' / f'{chapter_id}_img{i}.mp4'
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
            total_duration += img_duration

        # 3. 生成录屏部分（支持加速播放或完整播放）
        recordings = config.get('recordings', [])
        for ri, rec_item in enumerate(recordings):
            # 解析配置：(文件, 时长, 加速倍率) 或 (文件, 时长) 或 文件
            if isinstance(rec_item, tuple):
                if len(rec_item) == 3:
                    rec_file, rec_timing, speed = rec_item
                elif len(rec_item) == 2:
                    rec_file, rec_timing = rec_item
                    speed = 1.0
                else:
                    rec_file = rec_item[0]
                    rec_timing, speed = None, 1.0
            else:
                rec_file, rec_timing, speed = rec_item, None, 1.0

            rec_path = R / rec_file
            rec_part_path = R / 'temp' / f'{chapter_id}_rec{ri}.mp4'
            frame_path = R / 'frames' / config['frame']

            # 计算目标时长
            if rec_timing == 'full':
                # 完整播放，使用录屏实际时长
                target_duration = None  # 稍后计算
                speed = 1.0
            elif rec_timing:
                target_duration = resolve_timing(rec_timing, chapter_id, timeline)
            else:
                # 使用剩余时长
                remaining = seg_duration - total_duration
                target_duration = max(remaining, 5)

            # 获取录屏实际时长
            import re
            probe_cmd = [FFMPEG, '-i', str(rec_path)]
            result = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
            match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr)
            if match:
                h, m, s = match.groups()
                rec_actual_duration = int(h)*3600 + int(m)*60 + float(s)
            else:
                rec_actual_duration = 30

            if rec_timing == 'full':
                target_duration = rec_actual_duration

            # 如果录屏时长超过目标时长，需要加速
            if rec_actual_duration > target_duration and speed == 1.0:
                speed = rec_actual_duration / target_duration

            # 构建滤镜
            if speed > 1.0:
                pts_factor = 1.0 / speed
                filter_complex = (
                    f'[1:v]scale=1760:880,setsar=1,'
                    f'setpts={pts_factor}*PTS,'
                    f'tpad=stop_mode=clone:stop_duration={target_duration}[ui];'
                    f'[0:v][ui]overlay=80:116:shortest=1[v]'
                )
            else:
                filter_complex = (
                    f'[1:v]scale=1760:880,setsar=1,'
                    f'tpad=stop_mode=clone:stop_duration={target_duration}[ui];'
                    f'[0:v][ui]overlay=80:116:shortest=1[v]'
                )

            inputs = [
                '-loop', '1', '-framerate', '25',
                '-i', str(frame_path),
                '-i', str(rec_path)
            ]

            cmd = [
                FFMPEG, '-y', '-v', 'warning',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-an',
                '-frames:v', str(round(target_duration * 25)),
                '-r', '25',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '16',
                '-pix_fmt', 'yuv420p',
                str(rec_part_path)
            ]
            subprocess.run(cmd, check=True)
            parts.append(str(rec_part_path))
            total_duration += target_duration

        # 如果视频总时长小于配音时长，用最后一帧补齐
        if total_duration < seg_duration:
            padding_duration = seg_duration - total_duration
            padding_part_path = R / 'temp' / f'{chapter_id}_padding.mp4'
            frame_path = R / 'frames' / config['frame']

            # 使用最后一张截图或录屏的最后一帧
            last_source = sources[-1] if sources else None
            if last_source:
                if isinstance(last_source, tuple):
                    last_img = R / last_source[0]
                else:
                    last_img = R / last_source
            else:
                last_img = R / 'frames' / config['frame']

            inputs = [
                '-loop', '1', '-framerate', '25',
                '-i', str(frame_path),
                '-loop', '1', '-framerate', '25',
                '-i', str(last_img)
            ]

            filter_complex = (
                f'[1:v]scale=1760:880,setsar=1,'
                f'tpad=stop_mode=clone:stop_duration={padding_duration}[ui];'
                f'[0:v][ui]overlay=80:116:shortest=1[v]'
            )

            cmd = [
                FFMPEG, '-y', '-v', 'warning',
                *inputs,
                '-filter_complex', filter_complex,
                '-map', '[v]',
                '-an',
                '-frames:v', str(round(padding_duration * 25)),
                '-r', '25',
                '-c:v', 'libx264', '-preset', 'ultrafast', '-crf', '16',
                '-pix_fmt', 'yuv420p',
                str(padding_part_path)
            ]
            subprocess.run(cmd, check=True)
            parts.append(str(padding_part_path))
            total_duration = seg_duration

        # 输出实际总时长
        print(f"    实际时长: {total_duration:.1f}s (配音: {seg_duration:.1f}s)")

        # 合并所有片段（介绍页 + 截图序列 + 录屏）
        concat_file = R / 'temp' / f'{chapter_id}_concat.txt'
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

    # 合并音频
    print("合并音频和视频...")
    audio_path = R / 'audio' / 'narration.wav'
    subtitle_path = 'N03-四种知识能力怎么选.srt'  # 使用相对路径
    final_output = R / 'N03-四种知识能力怎么选.mp4'

    # 获取视频实际时长
    import re
    probe_cmd = [FFMPEG, '-i', str(video_only)]
    result = subprocess.run(probe_cmd, capture_output=True, text=True, encoding='utf-8', errors='ignore')
    match = re.search(r'Duration: (\d+):(\d+):(\d+\.\d+)', result.stderr)
    if match:
        h, m, s = match.groups()
        video_duration = int(h)*3600 + int(m)*60 + float(s)
    else:
        video_duration = duration

    # 如果视频比配音长，需要在音频后面添加静音
    if video_duration > duration + 1:
        print(f"    视频({video_duration:.1f}s)比配音({duration:.1f}s)长，添加静音填充...")
        # 使用 afilters 在音频后添加静音
        silence_duration = video_duration - duration
        cmd = [
            FFMPEG, '-y', '-v', 'warning',
            '-i', str(video_only),
            '-i', str(audio_path),
            '-filter_complex', f'[1:a]apad=pad_dur={silence_duration}[audio]',
            '-map', '0:v',
            '-map', '[audio]',
            '-vf', f"subtitles={subtitle_path}:force_style='FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=20'",
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(final_output)
        ]
    else:
        cmd = [
            FFMPEG, '-y', '-v', 'warning',
            '-i', str(video_only),
            '-i', str(audio_path),
            '-vf', f"subtitles={subtitle_path}:force_style='FontSize=18,PrimaryColour=&H00FFFFFF,OutlineColour=&H00000000,Outline=2,Alignment=2,MarginV=20'",
            '-c:v', 'libx264', '-preset', 'fast', '-crf', '22',
            '-c:a', 'aac', '-b:a', '192k',
            '-shortest',
            str(final_output)
        ]

    try:
        subprocess.run(cmd, check=True)
        print("字幕烧录成功")
    except subprocess.CalledProcessError as e:
        # 如果字幕烧录失败，先不烧字幕
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

    # 输出结果
    file_size = final_output.stat().st_size / 1024 / 1024
    print(f"\n=== 合成完成 ===")
    print(f"输出文件: {final_output}")
    print(f"文件大小: {file_size:.1f} MB")
    print(f"视频时长: {duration:.2f}s ({duration/60:.1f}min)")


if __name__ == '__main__':
    main()
