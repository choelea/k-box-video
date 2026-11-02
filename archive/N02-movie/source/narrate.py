import asyncio,json,pathlib,subprocess,re,wave
import edge_tts
ROOT=pathlib.Path(__file__).resolve().parent.parent
plan=json.loads((ROOT/'source/plan.json').read_text())
async def main():
    sem=asyncio.Semaphore(3)
    async def one(ci,li,text):
        async with sem:
            stem=ROOT/'audio'/f'{ci:02}_{li:02}'
            for attempt in range(3):
                try:
                    events=[]
                    with stem.with_suffix('.mp3').open('wb') as f:
                        async for chunk in edge_tts.Communicate(text,'zh-CN-XiaoxiaoNeural',rate='+12%',boundary='WordBoundary').stream():
                            if chunk['type']=='audio':f.write(chunk['data'])
                            elif chunk['type']=='WordBoundary':events.append(chunk)
                    stem.with_suffix('.json').write_text(json.dumps(events,ensure_ascii=False))
                    subprocess.run(['ffmpeg','-y','-v','error','-i',str(stem.with_suffix('.mp3')),'-ar','48000','-ac','1',str(stem.with_suffix('.wav'))],check=True)
                    print(f'voice {ci:02}/{li:02}',flush=True)
                    return
                except Exception:
                    if attempt==2:raise
                    await asyncio.sleep(1+attempt)
    await asyncio.gather(*(one(ci,li,t) for ci,c in enumerate(plan) for li,t in enumerate(c['lines'])))
asyncio.run(main())
# Assemble uncompressed narration, retaining exact sample positions.
clock=0; cues=[]; chapters=[]
out=wave.open(str(ROOT/'audio/narration.wav'),'wb');out.setparams((1,2,48000,0,'NONE','not compressed'))
def silence(sec):
    global clock
    n=round(sec*48000);out.writeframes(b'\0\0'*n);clock+=n/48000
silence(.65)
for ci,c in enumerate(plan):
    chapter={**c,'start':clock,'segments':[]}
    for li,t in enumerate(c['lines']):
        stem=ROOT/'audio'/f'{ci:02}_{li:02}'
        with wave.open(str(stem.with_suffix('.wav')),'rb') as w:
            duration=w.getnframes()/48000;data=w.readframes(w.getnframes())
        start=clock;out.writeframes(data);clock+=duration
        events=json.loads(stem.with_suffix('.json').read_text())
        positions=[];cursor=0
        for ev in events:
            token=ev['text'];i=t.find(token,cursor)
            if i<0:continue
            positions.append((i,i+len(token),ev['offset']/1e7,(ev['offset']+ev['duration'])/1e7));cursor=i+len(token)
        # Readable punctuation-aware chunks, anchored to speech word boundaries.
        chunks=[];a=0
        for m in re.finditer('[，。？！；]',t):
            b=m.end()
            if b-a>24:
                while b-a>24:
                    chunks.append((a,a+22));a+=22
            if b-a>=5: chunks.append((a,b));a=b
        if a<len(t):chunks.append((a,len(t)))
        for k,(a,b) in enumerate(chunks):
            matching=[p for p in positions if p[1]>a and p[0]<b]
            if not matching:continue
            s=start+matching[0][2];e=start+matching[-1][3]+.12
            text=t[a:b].strip('，。；')
            cues.append({'start':s,'end':min(e,clock),'text':text})
        chapter['segments'].append({'text':t,'start':start,'end':clock})
        silence(.25 if li+1<len(c['lines']) else .65)
    chapter['end']=clock;chapters.append(chapter)
silence(.7);out.close()
for i in range(len(cues)-1):cues[i]['end']=min(cues[i]['end'],cues[i+1]['start']-.03)
def stamp(t):
    ms=round(t*1000);return f'{ms//3600000:02}:{ms//60000%60:02}:{ms//1000%60:02},{ms%1000:03}'
(ROOT/'N02-为什么还需要K-BOX.srt').write_text('\n\n'.join(f"{i+1}\n{stamp(x['start'])} --> {stamp(x['end'])}\n{x['text']}" for i,x in enumerate(cues))+'\n')
(ROOT/'source/timeline.json').write_text(json.dumps({'duration':clock,'chapters':chapters,'cues':cues},ensure_ascii=False,indent=2))
(ROOT/'讲解稿.md').write_text('# N02 · 已有文档系统和大模型，为什么还需要 K-BOX？\n\n'+ '\n\n'.join('## '+c['title']+'\n\n'+'\n\n'.join(c['lines']) for c in plan)+'\n\n来源：\n'+ '\n'.join('- https://kbox.dcsmartvision.com/wiki/'+s for s in ['positioning','capabilities','consumption','scenarios','enterprise','docs'])+'\n')
print(json.dumps({'duration':clock,'chapters':[{k:c[k] for k in ['id','start','end']} for c in chapters]},ensure_ascii=False),flush=True)
