import pathlib,json,subprocess,math
R=pathlib.Path(__file__).resolve().parent.parent;T=json.loads((R/'source/timeline.json').read_text());D={c['id']:(0 if i==0 else c['start'],c['end']) for i,c in enumerate(T['chapters'])}
records={x['name']:x for x in json.loads((R/'source/scene-recordings.json').read_text())}
clips=[]
def encode(name,args,vf,dur):
 f=R/'build'/f'clip-{len(clips):02}-{name}.mp4';cmd=['ffmpeg','-y','-v','warning',*args,'-vf',vf,'-an','-t',str(dur),'-r','25','-c:v','libx264','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p',str(f)];subprocess.run(cmd,check=True);clips.append(f);print('clip',name,dur,flush=True)
def still(name,frame,dur):encode(name,['-loop','1','-framerate','25','-i',str(R/'frames'/frame)],'scale=1760:880,setsar=1',dur)
def recording(name,dur):
 rec=records[name];raw=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',rec['videoPath']]));cut=max(0,raw-rec['elapsed']);encode(name,['-ss',str(cut),'-i',rec['videoPath']],f'scale=1760:880,setsar=1,tpad=stop_mode=clone:stop_duration=1',dur)
for id in ['intro','case','roles']:still(id,'slide-'+id+'.png',D[id][1]-D[id][0])
recording('documents',D['documents'][1]-D['documents'][0]);recording('question',D['question'][1]-D['question'][0])
live=json.loads((R/'source/live-recording.json').read_text());raw=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',live['videoPath']]));cut=max(0,raw-live['elapsed']);submit=next(x['time'] for x in live['events'] if x['name']=='submit');answer=next(x['time'] for x in live['events'] if x['name']=='answer');dur=D['search'][1]-D['search'][0]
# Slow replay of the real search capture; explicit label avoids implying a latency measurement.
encode('search',['-ss',str(cut+submit),'-i',live['videoPath']],f"trim=duration={answer-submit},setpts=1.5*(PTS-STARTPTS),fps=25,tpad=stop_mode=clone:stop_duration=25,drawbox=x=1080:y=15:w=640:h=48:color=0x0b1120@0.92:t=fill,drawtext=fontfile=/System/Library/Fonts/PingFang.ttc:text='实际检索过程节选 · 慢放展示':x=1100:y=27:fontsize=24:fontcolor=0xf2c34e,setsar=1",dur)
# Hold genuine UI screenshots while the narration explains each result/source.
# Browser screencast timestamps drift during long scrolls; these exact captures
# keep each source legible and synchronized without altering its content.
still('answer-repair','record-answer-repair.png',163.286-D['answer'][0])
still('answer-batch','record-answer-batch.png',D['answer'][1]-163.286)
evidence_shots=[
 ('repair',D['evidence'][0],189.75),
 ('threshold',189.75,196.962),
 ('seven',196.962,203.962),
 ('three',203.962,210.174),
 ('ten',210.174,217.362),
 ('supplier',217.362,226.102),
]
for name,start,end in evidence_shots:
 still('evidence-'+name,'record-evidence-'+name+'.png',end-start)
still('limits','slide-limits.png',D['evidence'][1]-226.102)
still('decision','slide-decision.png',T['duration']-D['decision'][0])
(R/'source/concat.txt').write_text(''.join("file '"+str(f)+"'\n" for f in clips))
out=R/'build/assembled.mp4';subprocess.run(['ffmpeg','-y','-v','warning','-f','concat','-safe','0','-i',str(R/'source/concat.txt'),'-c','copy',str(out)],check=True)
d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(out)]));(R/'source/recording.json').write_text(json.dumps({'videoPath':str(out.relative_to(R)),'elapsed':d},indent=2));print('assembled',d,flush=True)
