"""Compose current public UI captures, aligned to narration and observed transitions."""
import json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent.parent
T=json.loads((R/'source/timeline.json').read_text());records={r['id']:r for r in json.loads((R/'source/scene-recordings.json').read_text())}
(R/'build').mkdir(exist_ok=True);shots=[];clips=[]
def cue(text):
 found=[c for c in T['cues'] if c['text']==text];assert len(found)==1,text;return found[0]['start']
for ci,c in enumerate(T['chapters']):
 start=0 if ci==0 else c['start'];end=T['duration'] if ci==len(T['chapters'])-1 else c['end']
 if c['id']=='positioning':
  rec=records[c['id']]
  for j,seg in enumerate(c['segments']):
   old=rec['capture_segments'][j]
   shots.append({'id':f'positioning-{j+1:02}','chapter':'positioning','kind':'record','start':seg['start'],'end':c['segments'][j+1]['start'] if j+1<len(c['segments']) else end,'record_offset':old['start'],'source_duration':old['end']-old['start']})
 elif c['id']=='docs':
  points=[('entry',start,'v2-docs-0.png'),('quick-start',c['segments'][1]['start'],'v2-docs-1.png'),('product-guides',c['segments'][2]['start'],'v2-docs-product-guides.png'),('api-reference',cue('API 参考面向系统集成'),'v2-docs-api-reference.png'),('deployment',cue('部署运维则覆盖环境准备与上线检查'),'v2-docs-2.png'),('validation',c['segments'][3]['start'],'v2-docs-3.png')]
  for j,(id,s,source) in enumerate(points):shots.append({'id':'docs-'+id,'chapter':'docs','kind':'still','start':s,'end':points[j+1][1] if j+1<len(points) else end,'source':source})
 else:shots.append({'id':c['id'],'chapter':c['id'],'kind':'slide' if c['id'] in ['intro','outro'] else 'record','start':start,'end':end})
for i,s in enumerate(shots):
 a,b=round(s['start']*25),round(s['end']*25);d=(b-a)/25;out=R/'build'/f'v2-{i:02}-{s["id"]}.mp4';s.update(start_frame=a,end_frame=b)
 inputs=['-loop','1','-framerate','25','-i',str(R/'frames'/f'brand-{s["chapter"]}.png')];fc='[0:v]setsar=1[v]'
 if s['kind']!='slide':
  if s['kind']=='record':
   rec=records[s['chapter']];cut=rec['sync']['start_seconds']+s.get('record_offset',0);assert rec['sync']['spread_seconds']<.4
   inputs+=['-ss',str(cut),'-t',str(s.get('source_duration',d)),'-i',str(R/rec['videoPath'])];s.update(source=rec['videoPath'],trim_start=cut)
  else:inputs+=['-loop','1','-framerate','25','-i',str(R/'frames'/s['source'])]
  fc=f'[1:v]scale=1760:880,setsar=1,tpad=stop_mode=clone:stop_duration={d}[ui];[0:v][ui]overlay=80:116:shortest=1[v]'
 subprocess.run(['ffmpeg','-y','-v','warning',*inputs,'-filter_complex',fc,'-map','[v]','-an','-frames:v',str(b-a),'-r','25','-c:v','libx264','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p',str(out)],check=True)
 clips.append(out);print(s['id'],d,flush=True)
(R/'source/shots.json').write_text(json.dumps({'basis':'observed recording transitions; docs stills aligned to spoken clauses','shots':shots},ensure_ascii=False,indent=2)+'\n')
concat=R/'build/v2-concat.txt';concat.write_text(''.join(f"file '{p}'\n" for p in clips));out=R/'build/assembled.mp4'
subprocess.run(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(out)],check=True)
(R/'source/recording.json').write_text(json.dumps({'videoPath':'build/assembled.mp4','elapsed':round(T['duration']*25)/25,'layout':'1920x1080 branded full frame','revision':3},indent=2)+'\n')
