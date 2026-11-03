import pathlib,json,subprocess,math
from PIL import Image,ImageDraw,ImageFont
R=pathlib.Path(__file__).resolve().parent.parent;F=R/'问学知识平台-基础介绍.mp4';T=json.loads((R/'source/timeline.json').read_text());S=json.loads((R/'source/shots.json').read_text())['shots']
p=json.loads(subprocess.check_output(['ffprobe','-v','error','-show_format','-show_streams','-show_chapters','-of','json',str(F)]))
v=next(s for s in p['streams'] if s['codec_type']=='video');a=next(s for s in p['streams'] if s['codec_type']=='audio')
assert (v['width'],v['height'],v['r_frame_rate'],v['codec_name'],a['codec_name'])==(1920,1080,'25/1','h264','aac');assert abs(float(p['format']['duration'])-T['duration'])<.2;assert len(p['chapters'])==8;assert any(s['codec_type']=='subtitle' for s in p['streams']);assert 120<=float(p['format']['duration'])<=420
for i,c in enumerate(T['cues']):
 assert c['start']<c['end'] and len(c['text'])<=26
 if i:assert c['start']>=T['cues'][i-1]['end']
assert len(json.loads((R/'source/brand-occurrences.json').read_text()))==3
for i,s in enumerate(S):
 assert s['end_frame']>s['start_frame']
 if i:assert s['start_frame']==S[i-1]['end_frame']
subprocess.run(['ffmpeg','-v','error','-i',str(F),'-f','null','-'],check=True)
font=ImageFont.truetype('/System/Library/Fonts/PingFang.ttc',21);board=Image.new('RGB',(1920,math.ceil(len(S)/2)*570),'#09111f')
for i,s in enumerate(S):
 ts=(s['start']+s['end'])/2;dst=R/'frames'/f'qa-v2-{s["id"]}.jpg'
 subprocess.run(['ffmpeg','-y','-v','error','-ss',str(ts),'-i',str(F),'-frames:v','1','-q:v','2',str(dst)],check=True)
 im=Image.open(dst).convert('RGB');im.thumbnail((960,540));x=(i%2)*960;y=(i//2)*570;board.paste(im,(x,y));ImageDraw.Draw(board).text((x+20,y+543),f'{int(ts)//60:02}:{int(ts)%60:02} {s["id"]}',font=font,fill='#adbed4')
board.save(R/'frames/quality-review.jpg',quality=90)
subprocess.run(['ffmpeg','-y','-v','error','-ss','3','-i',str(F),'-frames:v','1','-q:v','2',str(R/'poster.jpg')],check=True)
report={'revision':3,'duration':float(p['format']['duration']),'resolution':[v['width'],v['height']],'fps':v['r_frame_rate'],'video_codec':v['codec_name'],'audio_codec':a['codec_name'],'chapters':len(p['chapters']),'size_mb':round(F.stat().st_size/1024**2,2),'full_decode':'passed','subtitle_semantic_chunks':'passed','continuous_shot_frames':'passed','brand_occurrences':3,'brand_treatment':'approved-C treatment applied; three N01 contexts require listening'}
(R/'source/verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2)+'\n');print(json.dumps(report,ensure_ascii=False))
