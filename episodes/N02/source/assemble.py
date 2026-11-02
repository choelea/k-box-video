"""Build full-frame branded shots from speech anchors and saved real captures."""
import json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent.parent
T=json.loads((R/'source/timeline.json').read_text());C={c['id']:c for c in T['chapters']}
records={r['name']:r for r in json.loads((R/'source/scene-recordings.json').read_text())}
shots=[]
def cue(text):
 matches=[c for c in T['cues'] if c['text']==text]
 assert len(matches)==1,text
 return matches[0]['start']
def add(id,kind,start,end,**kw):
 assert end>start,(id,start,end)
 shots.append(dict(id=id,kind=kind,start=start,end=end,**kw))
for id in ['intro','case','roles']:add(id,'slide',0 if id=='intro' else C[id]['start'],C[id]['end'],frame='brand-'+id+'.png')
for id in ['documents','question']:add(id,'record',C[id]['start'],C[id]['end'],record=id,frame='brand-ui-'+id+'.png')
add('search','live',C['search']['start'],C['search']['end'],frame='brand-ui-search.png')
a=C['answer']['start'];b=cue('批次方面');e=C['answer']['end']
add('answer-repair','still',a,b,source='record-answer-repair.png',frame='brand-ui-answer-repair.png')
add('answer-batch','still',b,e,source='record-answer-batch.png',frame='brand-ui-answer-batch.png')
points=[('repair',C['evidence']['start']),('threshold',cue('以及三十起及以上进入三级评估的条件')-.04),('seven',cue('再看应急预案')-.04),('three',cue('供应商管理部门需要在三级评估启动后')-.04),('ten',cue('十个工作日对应供应商提交八步法整改报告')-.04),('supplier',cue('供应商制度还涉及关键件报告的专项评审')-.04),('limits',cue('原文没有规定的维修完成时间')-.04)]
for i,(id,start) in enumerate(points):
 end=points[i+1][1] if i+1<len(points) else C['evidence']['end']
 if id=='limits':add(id,'slide',start,end,frame='brand-limits.png')
 else:add('evidence-'+id,'still',start,end,source='record-evidence-'+id+'.png',frame='brand-ui-evidence-'+id+'.png')
end_start=T['duration']-4
add('decision','slide',C['decision']['start'],end_start,frame='brand-decision.png')
add('ending','slide',end_start,T['duration'],frame='brand-ending.png')
# Each boundary is rounded once to a video frame, avoiding cumulative clip drift.
clips=[]
for i,s in enumerate(shots):
 frames=round(s['end']*25)-round(s['start']*25);duration=frames/25;out=R/'build'/f'v2-{i:02}-{s["id"]}.mp4'
 base=['-loop','1','-framerate','25','-i',str(R/'frames'/s['frame'])]
 if s['kind']=='slide':
  inputs=base;fc='[0:v]setsar=1[v]'
 else:
  source_filter='scale=1760:880,setsar=1'
  if s['kind']=='still':inputs=base+['-loop','1','-framerate','25','-i',str(R/'frames'/s['source'])]
  else:
   rec=records[s['record']] if s['kind']=='record' else json.loads((R/'source/live-recording.json').read_text())
   raw=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(R/rec['videoPath'])]));cut=max(0,raw-rec['elapsed'])
   if s['kind']=='live':
    submit=next(e['time'] for e in rec['events'] if e['name']=='submit');answer=next(e['time'] for e in rec['events'] if e['name']=='answer');cut+=submit
    source_filter+=f",trim=duration={answer-submit},setpts=1.5*(PTS-STARTPTS),fps=25,tpad=stop_mode=clone:stop_duration={duration},drawbox=x=1080:y=15:w=640:h=48:color=0x09111f@0.95:t=fill,drawtext=fontfile=/System/Library/Fonts/PingFang.ttc:text='实际检索过程节选 · 慢放展示':x=1100:y=27:fontsize=24:fontcolor=0xf2c34e"
   else:source_filter+=f',tpad=stop_mode=clone:stop_duration={duration}'
   inputs=base+['-ss',str(cut),'-i',str(R/rec['videoPath'])]
  if s['id'].startswith('evidence-'):source_filter+=',drawbox=x=1088:y=1:w=670:h=878:color=0xf2c34e@0.8:t=2'
  fc=f'[1:v]{source_filter}[ui];[0:v][ui]overlay=80:116:shortest=1[v]'
 subprocess.run(['ffmpeg','-y','-v','warning',*inputs,'-filter_complex',fc,'-map','[v]','-an','-frames:v',str(frames),'-r','25','-c:v','libx264','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p',str(out)],check=True)
 s['start_frame']=round(s['start']*25);s['end_frame']=round(s['end']*25);clips.append(out);print(s['id'],duration,flush=True)
(R/'source/shots.json').write_text(json.dumps({'basis':'speech-segment-and-subtitle-anchors','shots':shots},ensure_ascii=False,indent=2)+'\n')
concat=R/'build/v2-concat.txt';concat.write_text(''.join(f"file '{f}'\n" for f in clips))
out=R/'build/assembled.mp4';subprocess.run(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(concat),'-c','copy',str(out)],check=True)
duration=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]))
(R/'source/recording.json').write_text(json.dumps({'videoPath':'build/assembled.mp4','elapsed':duration,'layout':'1920x1080 full branded frame','revision':2},indent=2)+'\n');print('assembled',duration,flush=True)
