#!/usr/bin/env python3
from __future__ import annotations
import argparse,csv,hashlib,json,pathlib,re,urllib.request
from datetime import datetime,timezone
from html.parser import HTMLParser
from urllib.parse import urljoin
REPOSITORY="StegVerse-Labs/Epsteinality";UA="StegVerse-ERL-Research/1.1"
def now():return datetime.now(timezone.utc).isoformat()
def sid(*p):return hashlib.sha256("|".join(map(str,p)).encode()).hexdigest()[:24]
def append(path,obj,dry):
    if not dry:
        path.parent.mkdir(parents=True,exist_ok=True)
        with path.open("a",encoding="utf-8") as f:f.write(json.dumps(obj,sort_keys=True)+"\n")
def jl(path):return [json.loads(x) for x in path.read_text(encoding="utf-8").splitlines() if x.strip()] if path.exists() else []
def js(path):return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
def wl(path):
    if not path.exists():return []
    with path.open(newline="",encoding="utf-8") as f:return list(csv.DictReader(f))
class Links(HTMLParser):
    def __init__(self):super().__init__();self.links=[];self.h=None;self.t=[]
    def handle_starttag(self,tag,attrs):
        if tag=="a":self.h=dict(attrs).get("href");self.t=[]
    def handle_data(self,d):
        if self.h is not None:self.t.append(d)
    def handle_endtag(self,tag):
        if tag=="a" and self.h is not None:self.links.append((" ".join(self.t).strip(),self.h));self.h=None;self.t=[]
def reqs(base):
    out=jl(base/"research/acquisition_requests.jsonl");f=js(base/"research/frontier.json")
    for t in f.get("trajectories",[]):
        if t.get("state") in {"OPEN","ACTIVE"}:
            for q in t.get("acquisition_queries",[]):out.append({"request_id":"frontier-"+sid(t.get("trajectory_id"),q),"trajectory_ids":[t.get("trajectory_id")],"query":q,"state":"ACTIVE"})
    return [r for r in out if r.get("state","ACTIVE") in {"OPEN","ACTIVE","RETRY"}]
def packet(r,s,title,link):return {"schema":"stegverse.erl.research_source_candidate.v1","candidate_id":"SRC-"+sid(r.get("request_id"),link),"repository":REPOSITORY,"trajectory_ids":r.get("trajectory_ids",[]),"acquisition_request_id":r.get("request_id"),"query":r.get("query",""),"source_url":link,"source_title":title,"retrieved_at":now(),"source_class":s.get("authority_class") or s.get("type") or "unknown","authority_proximity":"unknown","content_sha256":None,"custody_pointer":None,"verification_state":"UNVERIFIED","evidence_role":"lead-only","discovered_by":"scripts/search_agent.py","native_records_mutated":False,"evaluation_changed":False,"transport":{"source_repository":REPOSITORY,"destination_repository":"StegVerse-Labs/Executive_Rhetoric_Ledger","authority_effect":"NONE","credential_authority":"TV/TVC","github_token_authority":"NONE"}}
def main():
    p=argparse.ArgumentParser();p.add_argument("--base",default=".");p.add_argument("--dry-run",action="store_true");a=p.parse_args();b=pathlib.Path(a.base).resolve();R=reqs(b);S=wl(b/"data/sources/sources_whitelist.csv");n=0;seen=set()
    for r in R:
        terms=[x.lower() for x in re.findall(r"[A-Za-z0-9][A-Za-z0-9._-]{2,}",r.get("query",''))][:12]
        for s in S:
            u=(s.get("url") or "").strip()
            if not u:continue
            try:
                resp=urllib.request.urlopen(urllib.request.Request(u,headers={"User-Agent":UA}),timeout=15);data=resp.read(2000000);h=hashlib.sha256(data).hexdigest();parser=Links();parser.feed(data.decode(errors="ignore"));hits=[]
                for title,href in parser.links:
                    if terms and not all(t in (title+" "+href).lower() for t in terms):continue
                    link=urljoin(u,href);key=sid(link)
                    if key in seen:continue
                    seen.add(key);hits.append((title,link))
                for title,link in hits[:10]:append(b/"research/source_candidates.jsonl",packet(r,s,title,link),a.dry_run);n+=1
                append(b/"research/research_receipts.jsonl",{"receipt_id":"RSRCH-"+sid(r.get("request_id"),u,h),"request_id":r.get("request_id"),"trajectory_ids":r.get("trajectory_ids",[]),"source_scanned":u,"retrieved_at":now(),"response_hash":h,"hits":len(hits),"result":"NO_UPDATE" if not hits else "CANDIDATES_EMITTED","evaluation_changed":False},a.dry_run)
            except Exception as e:append(b/"research/research_receipts.jsonl",{"receipt_id":"RSRCH-"+sid(r.get("request_id"),u,now()),"request_id":r.get("request_id"),"trajectory_ids":r.get("trajectory_ids",[]),"source_scanned":u,"retrieved_at":now(),"result":"FAILED","error":type(e).__name__,"evaluation_changed":False},a.dry_run)
    print(json.dumps({"repository":REPOSITORY,"requests":len(R),"sources":len(S),"candidates":n,"dry_run":a.dry_run,"candidate_schema":"stegverse.erl.research_source_candidate.v1","credential_authority":"TV/TVC","github_token_authority":"NONE"},sort_keys=True))
if __name__=="__main__":main()
