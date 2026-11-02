import json,pathlib,subprocess,datetime
R=pathlib.Path(__file__).resolve().parent.parent
T=json.loads((R/'source/timeline.json').read_text())
def ass_time(t):
    cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
ass='''[Script Info]
Title: 问学知识平台 · 基础介绍
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,36,&H00FFFFFF,&H00FFFFFF,&H0010141F,&H90000000,0,0,0,0,100,100,0,0,1,1.5,1,2,100,100,41,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for c in T['cues']:
    ass+=f"Dialogue: 0,{ass_time(c['start'])},{ass_time(c['end'])},Default,,0,0,0,,{{\\fad(65,65)}}{c['text']}\n"
(R/'source/subtitles.ass').write_text(ass)
meta=';FFMETADATA1\ntitle=问学知识平台 · 基础介绍\nartist=K-BOX 问学\ncomment=基于指定六个公开页面制作的产品基础介绍，包含普通话配音及中文字幕。\n'
for i,c in enumerate(T['chapters']):
    meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round((0 if i==0 else c['start'])*1000)}\nEND={round(c['end']*1000)}\ntitle={c['title']}\n"
(R/'source/chapters.ffmeta').write_text(meta)
record=json.loads((R/'source/recording.json').read_text())
probe=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-of','json',record['videoPath']]))
duration=float(probe['format']['duration']);cut=max(0,duration-record['elapsed'])
(R/'source/cut.json').write_text(json.dumps({'raw_duration':duration,'trim_start':cut,'final_duration':T['duration']}))
cmd=['ffmpeg','-y','-hide_banner','-ss',str(cut),'-i',record['videoPath'],'-i',str(R/'audio/narration.wav'),'-f','ffmetadata','-i',str(R/'source/chapters.ffmeta'),'-i',str(R/'问学知识平台-基础介绍.srt'),'-map','0:v:0','-map','1:a:0','-map','3:0','-map_metadata','2','-map_chapters','2','-vf',f"ass={R}/source/subtitles.ass,fade=t=out:st={T['duration']-.55}:d=0.55",'-af','loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=out:st='+str(T['duration']-.55)+':d=0.55','-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','25','-c:a','aac','-b:a','192k','-ar','48000','-c:s','mov_text','-metadata:s:s:0','language=zho','-metadata:s:s:0','title=中文字幕','-disposition:s:0','0','-t',str(T['duration']),'-movflags','+faststart',str(R/'问学知识平台-基础介绍.mp4')]
print('Rendering',duration,cut,flush=True)
subprocess.run(cmd,check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(R/'audio/narration.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','libmp3lame','-b:a','192k',str(R/'问学知识平台-中文配音.mp3')],check=True)
