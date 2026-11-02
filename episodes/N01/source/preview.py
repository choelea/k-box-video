import pathlib,json,html
r=pathlib.Path(__file__).resolve().parent.parent
t=json.loads((r/'source/timeline.json').read_text())
chapters=''.join(f'<button type="button" data-time="{c["start"]:.3f}"><span>{i:02}</span>{html.escape(c["title"])}<small>{int(c["start"])//60:02}:{int(c["start"])%60:02}</small></button>' for i,c in enumerate(t['chapters'][1:-1],1))
transcript=''.join('<section><h3>'+html.escape(c['title'])+'</h3>'+''.join('<p>'+html.escape(s)+'</p>' for s in c['lines'])+'</section>' for c in t['chapters'])
s='''<!doctype html><html lang="zh-CN"><meta charset="UTF-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>问学知识平台 · 基础介绍</title>
<style>
*{box-sizing:border-box}body{margin:0;background:#090e19;color:#f1f4fa;font-family:-apple-system,BlinkMacSystemFont,"PingFang SC",sans-serif}main{max-width:1240px;margin:auto;padding:45px 28px 60px}.brand{display:flex;align-items:center;gap:12px;font-weight:600;font-size:16px;letter-spacing:1px}.logo{width:32px;height:32px;background:#f5bf22;border-radius:10px;display:grid;place-items:center;color:#0b1120}.brand em{color:#f5bf22;font-style:normal}h1{font-size:36px;letter-spacing:1px;margin:32px 0 12px}.meta{font-size:14px;color:#9aa7bc;margin-bottom:25px}.meta b{color:#f5bf22;font-weight:500}.player{overflow:hidden;border:1px solid #2d374a;border-radius:14px;background:#05080f;box-shadow:0 25px 85px #0004}video{width:100%;display:block;aspect-ratio:16/9}.actions{display:flex;gap:12px;align-items:center;margin:22px 0 30px;flex-wrap:wrap}.actions a{text-decoration:none;border-radius:7px;border:1px solid #364056;color:#d9e0ec;padding:11px 19px;font-size:14px}.actions a:first-child{background:#f5bf22;color:#0b1120;border-color:#f5bf22;font-weight:650}.intro{font-size:15px;color:#a5b1c4;line-height:1.8;margin:26px 0 20px}h2{font-size:17px;font-weight:600;margin:0 0 14px}.chapters{display:grid;grid-template-columns:repeat(3,1fr);gap:10px}.chapters button{display:flex;gap:12px;align-items:center;padding:17px 16px;background:#121a2b;border:1px solid #263146;border-radius:8px;color:#e7edf6;font:inherit;font-size:14px;cursor:pointer;text-align:left}.chapters button:hover,.chapters button.active{border-color:#f5bf22;background:#1b2330}.chapters span{color:#f5bf22;font-size:12px}.chapters small{margin-left:auto;color:#8391aa;font-size:12px}details{margin-top:30px;border-top:1px solid #263146;padding-top:22px}summary{cursor:pointer;color:#aab6c9;font-size:14px}.transcript{max-width:850px;color:#b5c1d2;line-height:1.9;font-size:15px}.transcript h3{color:#eef2f8;margin-top:30px;font-size:18px}.transcript p{margin:9px 0}footer{color:#65758e;font-size:12px;margin-top:38px}footer a{color:#8596b1;text-decoration:none}@media(max-width:650px){main{padding:25px 14px}.chapters{grid-template-columns:repeat(2,1fr)}h1{font-size:27px}.chapters button{padding:15px 11px;gap:7px}}
</style><main><div class="brand"><span class="logo">K</span>K-BOX <em>问学</em></div><h1>问学知识平台 · 基础介绍</h1><div class="meta"><b>03:51</b>　/　1080p　/　普通话配音　/　中文字幕</div><div class="player"><video id="video" controls playsinline preload="metadata" poster="poster.jpg" src="问学知识平台-基础介绍.mp4"></video></div><div class="actions"><a href="问学知识平台-基础介绍.mp4" download>下载视频 MP4 ↓</a><a href="问学知识平台-基础介绍.srt" download>下载字幕 SRT ↓</a><a href="问学知识平台-中文配音.mp3" download>下载配音 MP3 ↓</a></div><p class="intro">从产品定位开始，依次了解产品能力、知识消费、应用场景、企业级保障和开发者文档。</p><h2>选择章节</h2><div class="chapters">CHAPTERS</div><details><summary>查看完整讲解稿</summary><div class="transcript">TRANSCRIPT</div></details><footer>内容来源：<a href="https://kbox.dcsmartvision.com/wiki/positioning" target="_blank" rel="noreferrer">K-BOX 问学产品网站 ↗</a></footer></main><script>
const video=document.querySelector('video'),buttons=[...document.querySelectorAll('[data-time]')];buttons.forEach(b=>b.addEventListener('click',()=>{video.currentTime=Number(b.dataset.time);video.play()}));video.addEventListener('timeupdate',()=>{let index=-1;buttons.forEach((b,i)=>{if(Number(b.dataset.time)<=video.currentTime)index=i});buttons.forEach((b,i)=>b.classList.toggle('active',i===index))});
</script></html>'''
(r/'试看.html').write_text(s.replace('CHAPTERS',chapters).replace('TRANSCRIPT',transcript))
(r/'制作说明.md').write_text('''# 问学知识平台 · 基础介绍

- 时长：3 分 51 秒
- 画面：1920 × 1080，25 帧/秒，真实公开网页导览，配章节与重点高亮
- 配音：普通话女声（晓晓）
- 字幕：画面内嵌中文字幕，另附独立 SRT 和 MP4 可选字幕轨
- 交付：MP4、MP3、SRT、讲解稿和本地试看页面

讲解按产品定位、产品能力、知识消费、应用场景、企业级保障、开发者文档展开。依据录制时公开页面内容编写，不涉及真实业务数据或后台修改。

`source/` 保留制作脚本、讲解计划、准确时间线和页面文字快照，便于后续修改。`audio/`、`frames/`、`build/` 保存制作中间文件。
''')
