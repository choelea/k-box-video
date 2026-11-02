import json,pathlib,subprocess
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parent.parent
T=json.loads((R/'source/timeline.json').read_text())
NAME='N02-为什么还需要K-BOX'
font='/System/Library/Fonts/PingFang.ttc'
bg=Image.new('RGB',(1920,1080),'#070c16');d=ImageDraw.Draw(bg)
d.rounded_rectangle((75,105,1845,995),radius=14,fill='#25334b')
d.text((80,34),'N02  /  认知与选型',font=ImageFont.truetype(font,25),fill='#f1c34f')
d.text((1585,36),'K-BOX  问学',font=ImageFont.truetype(font,25),fill='#a5b4cb')
d.rectangle((80,83,1840,85),fill='#243149');bg.save(R/'source/frame.png')
def ast(t):
 cs=round(t*100);return f'{cs//360000}:{cs//6000%60:02}:{cs//100%60:02}.{cs%100:02}'
ass='''[Script Info]
Title: N02 · 为什么还需要 K-BOX
ScriptType: v4.00+
PlayResX: 1920
PlayResY: 1080
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Default,PingFang SC,33,&H00FFFFFF,&H00FFFFFF,&H00160C07,&H90000000,0,0,0,0,100,100,0,0,1,1.4,0,2,80,80,28,1
Style: Chapter,PingFang SC,25,&H00E9E2D8,&H00FFFFFF,&H00160C07,&H90000000,0,0,0,0,100,100,0,0,1,0,0,8,300,300,34,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
'''
for cue in T['cues']:
 ass+=f"Dialogue: 0,{ast(cue['start'])},{ast(cue['end'])},Default,,0,0,0,,{{\\fad(50,50)}}{cue['text']}\n"
for c in T['chapters']:
 ass+=f"Dialogue: 0,{ast(c['start'])},{ast(c['end'])},Chapter,,0,0,0,,{{\\fad(100,100)}}{c['title']}\n"
(R/'source/subtitles.ass').write_text(ass)
meta=';FFMETADATA1\ntitle=N02 · 已有文档系统和大模型，为什么还需要 K-BOX？\nartist=K-BOX 问学\ncomment=演示环境真实操作、概念示意、普通话配音与中文字幕。\n'
for i,c in enumerate(T['chapters']):
 meta+=f"[CHAPTER]\nTIMEBASE=1/1000\nSTART={round((0 if i==0 else c['start'])*1000)}\nEND={round(c['end']*1000)}\ntitle={c['title']}\n"
(R/'source/chapters.ffmeta').write_text(meta)
rec=json.loads((R/'source/recording.json').read_text());raw=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',rec['videoPath']]))
cut=max(0,raw-rec['elapsed']);(R/'source/cut.json').write_text(json.dumps({'raw_duration':raw,'trim_start':cut,'final_duration':T['duration']}))
filters=f"[2:v][0:v]overlay=80:110:shortest=1,ass={R}/source/subtitles.ass,fade=t=out:st={T['duration']-.6}:d=0.6[v]"
cmd=['ffmpeg','-y','-hide_banner','-ss',str(cut),'-i',rec['videoPath'],'-i',str(R/'audio/narration.wav'),'-loop','1','-framerate','25','-i',str(R/'source/frame.png'),'-f','ffmetadata','-i',str(R/'source/chapters.ffmeta'),'-i',str(R/(NAME+'.srt')),'-filter_complex',filters,'-map','[v]','-map','1:a:0','-map','4:0','-map_metadata','3','-map_chapters','3','-af',f"loudnorm=I=-16:TP=-1.5:LRA=9,afade=t=out:st={T['duration']-.6}:d=0.6",'-c:v','libx264','-preset','fast','-crf','20','-pix_fmt','yuv420p','-r','25','-c:a','aac','-b:a','192k','-ar','48000','-c:s','mov_text','-metadata:s:s:0','language=zho','-metadata:s:s:0','title=中文字幕','-disposition:s:0','0','-t',str(T['duration']),'-movflags','+faststart',str(R/(NAME+'.mp4'))]
print('render',raw,cut,flush=True);subprocess.run(cmd,check=True)
subprocess.run(['ffmpeg','-y','-v','error','-i',str(R/'audio/narration.wav'),'-af','loudnorm=I=-16:TP=-1.5:LRA=9','-c:a','libmp3lame','-b:a','192k',str(R/(NAME+'-配音.mp3'))],check=True)
