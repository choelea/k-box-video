import json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent.parent;T=json.loads((R/'source/timeline.json').read_text());NAME='N02-企业场景版'
def ast(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
ass='''[Script Info]
Title: N02 · 企业场景优化版
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,36,&H00FFFFFF,&H00FFFFFF,&H001F1109,&H90000000,0,0,0,0,100,100,0,0,1,1.4,0,2,80,80,26,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for cue in T['cues']:ass+=f'Dialogue: 0,{ast(cue["start"])},{ast(cue["end"])},Default,,0,0,0,,{{\\fad(50,50)}}{cue["text"]}\n'
asspath=R/'build/subtitles.ass';asspath.write_text(ass)
meta=';FFMETADATA1\ntitle=N02 · 已有文档系统和大模型，为什么还需要 K-BOX？\nartist=问学知识平台 · K-BOX\ncomment=企业场景优化版 v2；真实演示素材；品牌基线 0.1。\n'
for i,c in enumerate(T['chapters']):meta+=f'[CHAPTER]\nTIMEBASE=1/1000\nSTART={round((0 if i==0 else c["start"])*1000)}\nEND={round((T["duration"] if i==len(T["chapters"])-1 else c["end"])*1000)}\ntitle={c["title"]}\n'
metapath=R/'build/chapters.ffmeta';metapath.write_text(meta)
rec=json.loads((R/'source/recording.json').read_text())
subprocess.run(['ffmpeg','-y','-hide_banner','-i',str(R/rec['videoPath']),'-i',str(R/'audio/narration.wav'),'-i',str(R/(NAME+'.srt')),'-f','ffmetadata','-i',str(metapath),'-vf',f'ass={asspath},fade=t=in:st=0:d=0.18,fade=t=out:st={T["duration"]-.4}:d=0.4','-map','0:v','-map','1:a','-map','2:0','-map_metadata','3','-map_chapters','3','-af',f'loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=out:st={T["duration"]-.4}:d=0.4','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','25','-c:a','aac','-b:a','192k','-ar','48000','-c:s','mov_text','-metadata:s:s:0','language=zho','-metadata:s:s:0','title=中文字幕','-disposition:s:0','0','-t',str(T['duration']),'-movflags','+faststart',str(R/(NAME+'.mp4'))],check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(R/'audio/narration.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','libmp3lame','-b:a','192k',str(R/(NAME+'-配音.mp3'))],check=True)
