from http.server import SimpleHTTPRequestHandler,ThreadingHTTPServer
import pathlib,os,re,shutil,argparse
parser=argparse.ArgumentParser()
parser.add_argument('project',type=pathlib.Path)
parser.add_argument('--port',type=int,default=8769)
args=parser.parse_args()
ROOT=args.project.resolve()
class Handler(SimpleHTTPRequestHandler):
    def __init__(self,*args,**kwargs):super().__init__(*args,directory=str(ROOT),**kwargs)
    def send_head(self):
        self.byte_range=None
        path=self.translate_path(self.path)
        if not os.path.isfile(path):return super().send_head()
        f=open(path,'rb');size=os.fstat(f.fileno()).st_size
        value=self.headers.get('Range','')
        match=re.fullmatch(r'bytes=(\d*)-(\d*)',value)
        if match:
            a,b=match.groups()
            if a:start=int(a);end=min(int(b),size-1) if b else size-1
            else:start=max(0,size-int(b));end=size-1
            if start>=size or end<start:
                f.close();self.send_response(416);self.send_header('Content-Range',f'bytes */{size}');self.end_headers();return
            self.byte_range=(start,end);self.send_response(206);self.send_header('Content-Range',f'bytes {start}-{end}/{size}');self.send_header('Content-Length',str(end-start+1));f.seek(start)
        else:self.send_response(200);self.send_header('Content-Length',str(size))
        self.send_header('Content-Type',self.guess_type(path));self.send_header('Accept-Ranges','bytes');self.end_headers();return f
    def copyfile(self,source,outputfile):
        try:
            if self.byte_range:
                remain=self.byte_range[1]-self.byte_range[0]+1
                while remain:
                    chunk=source.read(min(65536,remain))
                    if not chunk:break
                    outputfile.write(chunk);remain-=len(chunk)
            else:shutil.copyfileobj(source,outputfile)
        except (BrokenPipeError,ConnectionResetError):pass
print(f'http://127.0.0.1:{args.port}/%E8%AF%95%E7%9C%8B.html',flush=True)
ThreadingHTTPServer(('127.0.0.1',args.port),Handler).serve_forever()
