import pathlib,json,subprocess
from PIL import Image,ImageDraw,ImageFont
r=pathlib.Path(__file__).resolve().parent.parent
f=r/'问学知识平台-基础介绍.mp4'
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(f)]))
video=next(s for s in p['streams'] if s['codec_type']=='video')
audio=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (video['width'],video['height'])==(1920,1080)
assert video['codec_name']=='h264' and audio['codec_name']=='aac'
assert abs(float(p['format']['duration'])-231.026)<.15
assert len(p['chapters'])==8
assert any(s['codec_type']=='subtitle' for s in p['streams'])
subprocess.run(['ffmpeg','-v','error','-i',str(f),'-f','null','-'],check=True)
shots=[(3,'开场'),(21,'产品定位'),(56,'产品能力'),(103,'知识消费'),(145,'应用场景'),(175,'企业级保障'),(200,'开发者文档'),(225,'结束')]
font=ImageFont.truetype('/System/Library/Fonts/PingFang.ttc',23)
board=Image.new('RGB',(1920,4*300),'#0b1120')
for i,(ts,title) in enumerate(shots):
    dst=r/'frames'/f'qa-{ts}.jpg'
    subprocess.run(['ffmpeg','-y','-v','error','-ss',str(ts),'-i',str(f),'-frames:v','1','-q:v','2',str(dst)],check=True)
    im=Image.open(dst).convert('RGB');im.thumbnail((960,265))
    x=(i%2)*960;y=(i//2)*300;board.paste(im,(x+(960-im.width)//2,y))
    ImageDraw.Draw(board).text((x+23,y+268),f'{ts//60:02}:{ts%60:02}  {title}',font=font,fill='#e7ecf4')
board.save(r/'frames/quality-review.jpg',quality=90)
subprocess.run(['ffmpeg','-y','-v','error','-ss','3','-i',str(f),'-frames:v','1','-q:v','2',str(r/'poster.jpg')],check=True)
report={'duration':float(p['format']['duration']),'resolution':[video['width'],video['height']],'fps':video['r_frame_rate'],'video_codec':video['codec_name'],'audio_codec':audio['codec_name'],'audio_channels':audio['channels'],'chapters':len(p['chapters']),'size_mb':round(f.stat().st_size/1024**2,2),'full_decode':'passed'}
(r/'source/verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report),flush=True)
