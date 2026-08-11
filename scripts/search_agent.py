#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,pathlib,re,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urljoin
UA='StegVerse-ERL-Research/1.0'
def now():return datetime.now(timezone.utc).isoformat()
def sid(*p):return hashlib.sha256('|'.join(map(str,p)).encode()).hexdigest()[:24]
def append(path,obj,dry):
    if dry:return
    path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('a',encoding='utf-8') as f:f.write(json.dumps(obj,sort_keys=True)+'\n')
def jsonl(path):return [json.loads(x) for x in path.read_text().splitlines() if x.strip()] if path.exists() else []
def frontier(path):return json.loads(path.read_text()) if path.exists() else {}
def white(path):
    if not path.exists():return []
    with path.open(newline='',encoding='utf-8') as f:return list(csv.DictReader(f))
class P(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.h=None;self.t=[]
    def handle_starttag(self,tag,attrs):
        if tag=='a':self.h=dict(attrs).get('href');self.t=[]
    def handle_data(self,d):
        if self.h is not None:self.t.append(d)
    def handle_endtag(self,tag):
        if tag=='a' and self.h is not None:self.links.append((' '.join(self.t).strip(),self.h));self.h=None;self.t=[]
def requests(base):
    out=jsonl(base/'research/acquisition_requests.jsonl');f=frontier(base/'research/frontier.json')
    for t in f.get('trajectories',[]):
        if t.get('state') in {'OPEN','ACTIVE'}:
            for q in t.get('acquisition_queries',[]):out.append({'request_id':'frontier-'+sid(t.get('trajectory_id'),q),'trajectory_ids':[t.get('trajectory_id')],'query':q,'state':'ACTIVE'})
    return [r for r in out if r.get('state','ACTIVE') in {'OPEN','ACTIVE','RETRY'}]
def main():
    a=argparse.ArgumentParser();a.add_argument('--base',default='.');a.add_argument('--dry-run',action='store_true');z=a.parse_args();b=pathlib.Path(z.base).resolve();R=requests(b);S=white(b/'data/sources/sources_whitelist.csv');n=0
    for r in R:
        ts=[x.lower() for x in re.findall(r'[A-Za-z0-9][A-Za-z0-9._-]{2,}',r.get('query',''))][:12]
        for s in S:
            u=(s.get('url') or '').strip()
            if not u:continue
            try:
                req=urllib.request.Request(u,headers={'User-Agent':UA});resp=urllib.request.urlopen(req,timeout=15);data=resp.read(2000000);h=hashlib.sha256(data).hexdigest();p=P();p.feed(data.decode(errors='ignore'));hits=[]
                for title,href in p.links:
                    hay=(title+' '+href).lower()
                    if ts and not all(t in hay for t in ts):continue
                    hits.append((title,urljoin(u,href)))
                for title,link in hits[:10]:append(b/'research/source_candidates.jsonl',{'candidate_id':'SRC-'+sid(r.get('request_id'),link),'repository':b.name,'trajectory_ids':r.get('trajectory_ids',[]),'acquisition_request_id':r.get('request_id'),'query':r.get('query',''),'source_url':link,'source_title':title,'retrieved_at':now(),'source_class':s.get('authority_class') or 'unknown','verification_state':'unverified','evidence_role':'lead-only','discovered_by':'scripts/search_agent.py'},z.dry_run);n+=1
                append(b/'research/research_receipts.jsonl',{'receipt_id':'RSRCH-'+sid(r.get('request_id'),u,h),'request_id':r.get('request_id'),'trajectory_ids':r.get('trajectory_ids',[]),'source_scanned':u,'retrieved_at':now(),'response_hash':h,'hits':len(hits),'result':'NO_UPDATE' if not hits else 'CANDIDATES_EMITTED'},z.dry_run)
            except Exception as e:append(b/'research/research_receipts.jsonl',{'receipt_id':'RSRCH-'+sid(r.get('request_id'),u,now()),'request_id':r.get('request_id'),'trajectory_ids':r.get('trajectory_ids',[]),'source_scanned':u,'retrieved_at':now(),'result':'FAILED','error':type(e).__name__},z.dry_run)
    print(json.dumps({'requests':len(R),'sources':len(S),'candidates':n,'dry_run':z.dry_run},sort_keys=True))
if __name__=='__main__':main()
