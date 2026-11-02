import pathlib,json,subprocess
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parent.parent
N='N02-企业场景版';F=R/(N+'.mp4');T=json.loads((R/'source/timeline.json').read_text())
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(F)]))
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio');assert (v['width'],v['height'])==(1920,1080);assert v['codec_name']=='h264' and a['codec_name']=='aac';assert abs(float(p['format']['duration'])-T['duration'])<.2;assert len(p['chapters'])==9;assert any(s['codec_type']=='subtitle' for s in p['streams']);assert 120<=float(p['format']['duration'])<=420
subprocess.run(['ffmpeg','-v','error','-i',str(F),'-f','null','-'],check=True)
shots=[(3,'开场'),(25,'企业场景'),(60,'能力分工'),(85,'三份制度'),(120,'深度提问'),(138,'实际检索'),(158,'单车建议'),(172,'批次建议'),(190,'维修依据'),(194,'批次阈值'),(202,'评估时限'),(217,'供应商要求'),(231,'核验边界'),(255,'选型结论')]
font=ImageFont.truetype('/System/Library/Fonts/PingFang.ttc',21);board=Image.new('RGB',(1920,7*570),'#0b1120')
for i,(ts,title) in enumerate(shots):
 dst=R/'frames'/f'qa-{ts}.jpg';subprocess.run(['ffmpeg','-y','-v','error','-ss',str(ts),'-i',str(F),'-frames:v','1','-q:v','2',str(dst)],check=True);im=Image.open(dst).convert('RGB');im.thumbnail((960,540));x=(i%2)*960;y=(i//2)*570;board.paste(im,(x,y));ImageDraw.Draw(board).text((x+20,y+543),f'{ts//60:02}:{ts%60:02} {title}',font=font,fill='#dce6f9')
board.save(R/'frames/quality-review.jpg',quality=90)
subprocess.run(['ffmpeg','-y','-v','error','-ss','3','-i',str(F),'-frames:v','1','-q:v','2',str(R/'poster.jpg')],check=True)
report={'duration':float(p['format']['duration']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'chapters':len(p['chapters']),'size_mb':round(F.stat().st_size/1024**2,2),'full_decode':'passed'}
(R/'source/verification.json').write_text(json.dumps(report,indent=2));print(json.dumps(report))
