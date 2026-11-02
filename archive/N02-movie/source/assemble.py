import json,pathlib,subprocess
R=pathlib.Path(__file__).resolve().parent.parent
T=json.loads((R/'source/timeline.json').read_text())
def read_clip(name):
 rec=json.loads((R/'source'/name).read_text());d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',rec['videoPath']]));return rec,max(0,d-rec['elapsed'])
tail,ct=read_clip('recording-tail.json');evidence,ce=read_clip('recording-evidence.json')
fc=f'[0:v]trim=duration=125,setpts=PTS-STARTPTS[p];[1:v]trim=start={ct}:duration=3.3,setpts=PTS-STARTPTS[q];[2:v]trim=start={ce}:duration=30.6,setpts=PTS-STARTPTS[e];[1:v]trim=start={ct+33.9}:duration={T["duration"]-158.9},setpts=PTS-STARTPTS[t];[p][q][e][t]concat=n=4:v=1:a=0[v]'
cmd=['ffmpeg','-y','-v','warning','-i',str(R/'assets/recordings/prefix.mp4'),'-i',tail['videoPath'],'-i',evidence['videoPath'],'-filter_complex',fc,'-map','[v]','-an','-r','25','-c:v','libx264','-preset','ultrafast','-crf','16','-pix_fmt','yuv420p',str(R/'build/assembled.mp4')]
print('assembling',ct,ce,flush=True);subprocess.run(cmd,check=True)
p=R/'build/assembled.mp4';d=float(subprocess.check_output(['ffprobe','-v','error','-show_entries','format=duration','-of','csv=p=0',str(p)]));(R/'source/recording.json').write_text(json.dumps({'videoPath':str(p),'elapsed':d,'edit':'Initial capture through 125s; saved session source review; architecture and conclusion.'},indent=2));print('assembled',d,flush=True)
