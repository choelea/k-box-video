"""N01 v2: regenerate brand lines only; align formal subtitles to speech events."""
import asyncio,json,pathlib,re,subprocess,wave
import edge_tts
R=pathlib.Path(__file__).resolve().parent.parent;REPO=R.parent.parent
plan=json.loads((R/'source/plan.json').read_text())
overrides=json.loads((R/'source/speech-overrides.json').read_text())
phrases=json.loads((R/'source/subtitle-phrases.json').read_text())
# Fail clearly when an edited sentence lacks a regeneration request.
base=json.loads((REPO/'archive/N01-intro-v1/source/plan.json').read_text())
changed={row['stem'] for row in overrides['lines']}
for ci,c in enumerate(plan):
 for li,text in enumerate(c['lines']):
  if f'{ci:02}_{li:02}' not in changed:
   assert text==base[ci]['lines'][li], 'Add changed sentence to speech-overrides.json'
voice=json.loads((REPO/'shared/pronunciation.json').read_text())['selected']
assert voice['status']=='approved' and voice['selected_candidate']=='C'
async def generate():
 for row in overrides['lines']:
  ci,li=map(int,row['stem'].split('_'));assert row['formal']==plan[ci]['lines'][li], 'Sync speech override with plan first'
  stem=R/'audio'/row['stem'];request={'text':row['speech'],'voice':voice['voice'],'rate':voice['rate']};saved=stem.with_suffix('.request.json')
  if saved.exists() and json.loads(saved.read_text())==request:continue
  for attempt in range(3):
   try:
    events=[]
    with stem.with_suffix('.mp3').open('wb') as stream:
     async for part in edge_tts.Communicate(request['text'],request['voice'],rate=request['rate'],boundary='WordBoundary').stream():
      if part['type']=='audio':stream.write(part['data'])
      elif part['type']=='WordBoundary':events.append(part)
    stem.with_suffix('.json').write_text(json.dumps(events,ensure_ascii=False,indent=2));break
   except Exception:
    if attempt==2:raise
    await asyncio.sleep(attempt+1)
  subprocess.run(['ffmpeg','-y','-v','error','-i',str(stem.with_suffix('.mp3')),'-ar','48000','-ac','1',str(stem.with_suffix('.wav'))],check=True)
  saved.write_text(json.dumps(request,ensure_ascii=False,indent=2)+'\n');print('updated brand speech',row['stem'],flush=True)
def plain(t):return re.sub(r'[\s，。？！；：、“”‘’]','',t)
def stamp(t):
 ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
def timeline():
 clock=.65;data=bytearray(round(clock*48000)*2);chapters=[];cues=[];brands=[]
 for ci,chapter in enumerate(plan):
  c={**chapter,'start':clock,'segments':[]}
  for li,text in enumerate(chapter['lines']):
   stem=R/'audio'/f'{ci:02}_{li:02}'
   with wave.open(str(stem.with_suffix('.wav')),'rb') as stream:audio=stream.readframes(stream.getnframes())
   start=clock;data.extend(audio);clock+=len(audio)/96000
   events=json.loads(stem.with_suffix('.json').read_text());positions=[];cursor=0;full=plain(text)
   for ev in events:
    token=plain(ev['text'])
    if not token:continue
    pos=full.find(token,cursor)
    if pos<0:raise ValueError(f'Unmatched speech token: {stem.name} {token}')
    positions.append((pos,pos+len(token),ev['offset']/1e7,(ev['offset']+ev['duration'])/1e7));cursor=pos+len(token)
    if token=='问学':brands.append({'stem':stem.name,'time':start+ev['offset']/1e7,'duration':ev['duration']/1e7,'text':text,'review':'C treatment applied; new context awaits listening'})
   cursor=0
   for frag in re.split('[，。？！；：]',text):
    if not frag:continue
    chunks=phrases.get(frag,[frag]);assert ''.join(plain(x) for x in chunks)==plain(frag)
    for chunk in chunks:
     assert len(chunk)<=26,chunk
     a,b=cursor,cursor+len(plain(chunk));matches=[p for p in positions if p[1]>a and p[0]<b];assert matches,chunk
     cues.append({'start':start+matches[0][2],'end':min(clock,start+matches[-1][3]+.12),'text':chunk});cursor=b
   c['segments'].append({'id':f'{chapter["id"]}-{li+1:02}','text':text,'start':start,'end':clock})
   gap=.25 if li+1<len(chapter['lines']) else .65;data.extend(b'\0\0'*round(gap*48000));clock+=gap
  c['end']=clock;chapters.append(c)
 data.extend(b'\0\0'*round(.7*48000));clock+=.7
 for i in range(len(cues)-1):cues[i]['end']=min(cues[i]['end'],cues[i+1]['start']-.03)
 with wave.open(str(R/'audio/narration.wav'),'wb') as out:out.setparams((1,2,48000,0,'NONE','not compressed'));out.writeframes(data)
 (R/'source/timeline.json').write_text(json.dumps({'duration':clock,'chapters':chapters,'cues':cues},ensure_ascii=False,indent=2)+'\n')
 (R/'source/brand-occurrences.json').write_text(json.dumps(brands,ensure_ascii=False,indent=2)+'\n')
 (R/'问学知识平台-基础介绍.srt').write_text(''.join(f'{i+1}\n{stamp(x["start"])} --> {stamp(x["end"])}\n{x["text"]}\n\n' for i,x in enumerate(cues)).rstrip()+'\n')
 notes=(R/'source/production-notes.md').read_text()
 (R/'讲解稿.md').write_text('# 问学知识平台 · 基础介绍\n\n'+'\n\n'.join('## '+c['title']+'\n\n'+'\n\n'.join(c['lines']) for c in plan)+'\n\n---\n\n'+notes)
 print(json.dumps({'duration':clock,'brand_occurrences':len(brands)},ensure_ascii=False))
if __name__=='__main__':asyncio.run(generate());timeline()
