"""Align capture starts from real UI transitions, avoiding encoder tail padding."""
from pathlib import Path
from PIL import Image,ImageChops,ImageStat
import subprocess,json,statistics
R=Path(__file__).resolve().parent.parent;records=json.loads((R/'source/scene-recordings.json').read_text());reports=[]
for rec in records:
 id=rec['id']
 if id=='docs':
  rec['sync']={'method':'recording retained; still captures aligned to spoken clauses for readable sections'}
  reports.append({'id':id,**rec['sync']});continue
 buf=subprocess.check_output(['ffmpeg','-v','error','-i',str(R/rec['videoPath']),'-vf','fps=10,scale=352:176','-f','rawvideo','-pix_fmt','rgb24','-']);n=352*176*3;frames=[Image.frombytes('RGB',(352,176),buf[a:a+n]) for a in range(0,len(buf),n)]
 refs=[]
 if id=='docs':
  refs=[(1,next(x['time'] for x in rec['events'] if x['type']=='focus' and x['selector']=='.docs-choice')),(2,next(x['time'] for x in rec['events'] if x['type']=='scroll' and x['selector']=='#deployment')),(3,next(x['time'] for x in rec['events'] if x['type']=='focus' and x['selector']=='.quick-start-card:nth-child(2)'))]
 else:
  events=[e for e in rec['events'] if e['type']=='focus']
  if id=='positioning':refs=[(1,events[1]['time']),(2,events[2]['time'])]
  else:refs=[(i+1,e['time']) for i,e in enumerate(events)]
 templates=sorted((R/'frames').glob(f'v2-{id}-[0-9].png'))
 images={int(p.stem.split('-')[-1]):Image.open(p).convert('RGB').resize((352,176)) for p in templates}
 scores={li:[sum(ImageStat.Stat(ImageChops.difference(im,f)).mean)/3 for f in frames] for li,im in images.items()}
 labels=[min(scores,key=lambda k:scores[k][i]) for i in range(len(frames))]
 offsets=[];matches=[]
 for li,event_time in refs:
  values=scores[li];best=min(values)
  candidates=[i for i in range(len(frames)-2) if labels[i:i+3]==[li]*3 and values[i]<best+.2]
  assert candidates,(id,li)
  first=candidates[0]/10
  offset=first-event_time;offsets.append(offset);matches.append({'screenshot':f'v2-{id}-{li}.png','event_seconds':event_time,'video_transition_seconds':first,'start_estimate':offset,'pixel_mean_error':best})
 start=statistics.median(offsets);spread=max(offsets)-min(offsets)
 assert start>=0 and spread<.4,(id,offsets)
 rec['sync']={'method':'observed screenshot state transitions minus recorded action times','start_seconds':round(start,3),'spread_seconds':round(spread,3),'sampling_fps':10}
 reports.append({'id':id,**rec['sync'],'matches':matches});print(id,rec['sync'],flush=True)
(R/'source/scene-recordings.json').write_text(json.dumps(records,ensure_ascii=False,indent=2)+'\n');(R/'source/capture-sync-verification.json').write_text(json.dumps(reports,ensure_ascii=False,indent=2)+'\n')
