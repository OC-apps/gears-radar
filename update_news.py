#!/usr/bin/env python3
import json,re,hashlib,datetime as dt,concurrent.futures
from pathlib import Path
from urllib.request import Request,urlopen
from urllib.parse import urlencode
from xml.etree import ElementTree as ET
from html import unescape
from email.utils import parsedate_to_datetime
ROOT=Path(__file__).resolve().parent
NS={'a':'http://www.w3.org/2005/Atom'}
def clean(s):return re.sub(r'\s+',' ',unescape(re.sub('<[^>]*>',' ',s or ''))).strip()[:550]
def stamp(s):
 try:return parsedate_to_datetime(s).astimezone(dt.timezone.utc).isoformat()
 except:
  try:return dt.datetime.fromisoformat(s.replace('Z','+00:00')).astimezone(dt.timezone.utc).isoformat()
  except:return ''
def get(src):
 name,cat,url=src
 try:
  with urlopen(Request(url,headers={'User-Agent':'Mozilla/5.0 GEARS-RADAR/1.0','Accept':'application/rss+xml,application/atom+xml,application/xml'}),timeout=20) as r:root=ET.fromstring(r.read(1500000))
  if root.tag.endswith('rss'):
   entries=[(e.findtext('title',''),e.findtext('link',''),e.findtext('description',''),e.findtext('pubDate','')) for e in root.findall('./channel/item')]
  else:
   entries=[]
   for e in root.findall('.//a:entry',NS):
    links=e.findall('a:link',NS)
    href=next((l.attrib.get('href','') for l in links if l.attrib.get('rel')=='alternate'),links[0].attrib.get('href','') if links else '')
    entries.append((e.findtext('a:title','',NS),href,e.findtext('a:summary','',NS),e.findtext('a:published','',NS) or e.findtext('a:updated','',NS)))
  items=[]
  for title,link,summary,date in entries[:70]:
   if link.startswith('https://') and clean(title):
    items.append({'id':hashlib.sha256(link.encode()).hexdigest(),'title':clean(title),'url':link,'summary':clean(summary),'published':stamp(date),'source':name,'category':cat})
  return {'name':name,'count':len(items),'error':None},items
 except Exception as e:return {'name':name,'count':0,'error':str(e)[:120]},[]
def gn(q,lang='es-419',region='MX',ceid='MX:es-419'):return 'https://news.google.com/rss/search?'+urlencode({'q':q,'hl':lang,'gl':region,'ceid':ceid})
feeds=[('Gears of War · MX','noticias',gn('"Gears of War" when:7d')),('Gears of War · global','noticias',gn('"Gears of War" when:7d','en-US','US','US:en')),('Gears E-Day','oficial',gn('"Gears of War: E-Day" when:7d','en-US','US','US:en')),('The Coalition','oficial',gn('"The Coalition" "Gears" when:7d','en-US','US','US:en')),('Reddit r/GearsOfWar','comunidad','https://www.reddit.com/r/GearsOfWar/new/.rss?limit=40')]
creators=json.loads((ROOT/'creadores.json').read_text(encoding='utf-8'))['creators']
for c in creators:
 if not c.get('active',True):continue
 m=re.fullmatch(r'https?://(?:www\.)?youtube\.com/channel/(UC[A-Za-z0-9_-]{22})/?',c.get('url',''))
 if m:feeds.append((c['name']+' · YouTube','creador','https://www.youtube.com/feeds/videos.xml?channel_id='+m.group(1)))
for c in creators[:8]:
 name=c['name'].replace('"','')
 feeds.append((name+' · menciones','mencion',gn('"'+name+'" "Gears of War" when:7d')))
with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:results=list(pool.map(get,feeds))
path=ROOT/'data/news.json'
try:old=json.loads(path.read_text(encoding='utf-8')).get('items',[])
except:old=[]
allitems={x['id']:x for x in old if 'id' in x}
for _,items in results:
 for x in items:allitems[x['id']]=x
cutoff=dt.datetime.now(dt.timezone.utc)-dt.timedelta(days=14)
def valid(x):
 try:return dt.datetime.fromisoformat(x['published'])>=cutoff
 except:return False
news=sorted(filter(valid,allitems.values()),key=lambda x:x['published'],reverse=True)[:400]
path.parent.mkdir(exist_ok=True)
path.write_text(json.dumps({'updated_at':dt.datetime.now(dt.timezone.utc).isoformat(),'items':news,'sources':[s for s,_ in results]},ensure_ascii=False,indent=2),encoding='utf-8')
print('Noticias:',len(news),'Fuentes:',sum(not s['error'] for s,_ in results),'/',len(feeds))
