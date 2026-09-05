"""Inspect public video metadata/caption availability without storing a transcript."""
import json,re,urllib.request,hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
URL='https://www.youtube.com/watch?v=63R6Wnx44uY'
def get(url):
    with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=30) as response:return response.read().decode('utf-8')
page=get(URL);decoder=json.JSONDecoder()
def field(name):
    match=re.search('"'+name+'"\\s*:',page)
    return decoder.raw_decode(page[match.end():])[0] if match else None
tracks=field('captionTracks') or []
description=field('shortDescription') or ''
record={'url':URL,'retrieved':'2026-09-05','title':'KiCad 9 - Fully Automated Documentation Generation With CI/CD','author':'Vincent Nguyen','description_sha256':hashlib.sha256(description.encode()).hexdigest(),'chapter_times':re.findall(r'(?m)(?:^|\\n)(\d{1,2}:\d{2}(?::\d{2})?)\s*-',description),'caption_tracks':[{'language':t.get('languageCode'),'kind':t.get('kind','not-labelled-asr')} for t in tracks],'transcript_stored':False,'reason':'Full reproduction permission not established. Repository MIT licence is not assumed to cover the video.'}
if tracks:
    url=tracks[0]['baseUrl'].replace('\\u0026','&')
    if url.startswith('/'):url='https://www.youtube.com'+url
    try:
        caption=get(url+'&fmt=json3');record['caption_response_characters']=len(caption)
        record['caption_response_is_json']=caption.lstrip().startswith('{')
    except Exception as exc:record['caption_retrieval_error']=str(exc)
out=ROOT/'docs/knowledge/video-metadata.json';out.parent.mkdir(parents=True,exist_ok=True)
out.write_text(json.dumps(record,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in record.items() if k!='description'},indent=2))
