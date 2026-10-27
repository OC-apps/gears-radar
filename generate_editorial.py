#!/usr/bin/env python3
"""Prepara resumen editorial público en español usando IA durante GitHub Actions.
Requiere secreto OPENAI_API_KEY en GitHub Actions. No expone la clave."""
import os,json,datetime as dt,urllib.request,pathlib,re
ROOT=pathlib.Path(__file__).resolve().parent
output=ROOT/"data/editorial.json"
key=os.environ.get("OPENAI_API_KEY","").strip()
if not key:
 print("Sin OPENAI_API_KEY: se conserva la última edición, sin inventar resúmenes.")
 raise SystemExit(0)
items=json.loads((ROOT/"data/news.json").read_text(encoding="utf-8")).get("items",[])
now=dt.datetime.now(dt.timezone.utc)
recent=[]
for item in items:
 try:age=(now-dt.datetime.fromisoformat(item["published"])).total_seconds()/3600
 except:continue
 if age<0 or age>48:continue
 # Evita referencias imprecisas y repetidas; conservar diversidad de fuentes
 if not item.get("url","").startswith("https://"):continue
 recent.append(item)
recent=recent[:65]
if not recent:
 print("No hay elementos recientes. Se conserva la edición anterior.")
 raise SystemExit(0)
sources=[{"id":x["id"],"title":x["title"][:180],"summary":x.get("summary","")[:250],"source":x.get("source",""),"category":x.get("category",""),"url":x["url"],"published":x.get("published","")} for x in recent]
instructions="""Eres editor de noticias para GEARS RADAR, medio independiente sobre Gears of War y su comunidad hispanohablante.
Devuelve SOLO JSON válido, en español mexicano natural. Traduce el contenido en inglés y conserva nombres propios. NO inventes noticias, citas, cifras, reacciones, polémicas ni opiniones. Solo puedes usar la lista de fuentes aportada; son TITULARES Y EXTRACTOS, no textos completos. No afirmes haber leído artículos ni escuchado videos completos. Google News puede agrupar fuentes; no lo conviertas automáticamente en anuncio oficial. Distingue con cautela hechos, rumores, opiniones y simples preguntas de foro. Ignora ruido irrelevante y títulos genéricos. No infieras tendencia viral desde pocas publicaciones. Si no hay suficientes hechos, dilo.
Devuelve un objeto JSON con:
"resumen_dia": un texto de 100-180 palabras en español, fiel a las fuentes;
"temas": arreglo de 3 a 8 objetos {"titulo":texto español,"resumen":texto español de 40-85 palabras,"tipo":"confirmado|opinion|rumor|conversacion","relevancia":"alta|media|baja","source_ids":[ids presentes] ,"angulo_video":texto breve};
"guiones": arreglo hasta 3 de objetos {"titulo":texto,"duracion_estimada":"2 minutos","source_ids":[ids presentes],"texto":guion de opinión de unas 240-300 palabras en español, con introducción, contexto, análisis equilibrado, perspectiva sugerida claramente marcada como propuesta y cierre. No atribuyas una postura personal al usuario.} 
El resumen no debe afirmar que todo es tendencia; si solo hay pocas fuentes, reconoce la evidencia limitada."""
payload={"model":"gpt-4.1-mini","temperature":0.2,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":instructions},{"role":"user","content":json.dumps({"fecha_utc":now.isoformat(),"fuentes":sources},ensure_ascii=False)}],"max_tokens":6000}
req=urllib.request.Request("https://api.openai.com/v1/chat/completions",data=json.dumps(payload,ensure_ascii=False).encode("utf-8"),headers={"Authorization":"Bearer "+key,"Content-Type":"application/json"},method="POST")
try:
 with urllib.request.urlopen(req,timeout=95) as response:raw=json.loads(response.read().decode("utf-8"))
 doc=json.loads(raw["choices"][0]["message"]["content"])
 allowed={s["id"] for s in sources}
 for section in ("temas","guiones"):
  doc[section]=[t for t in doc.get(section,[]) if isinstance(t,dict) and (set(t.get("source_ids",[])) & allowed)]
  for t in doc[section]:t["source_ids"]=[v for v in t.get("source_ids",[]) if v in allowed]
 doc["fuentes"]={s["id"]:{"url":s["url"],"title":s["title"],"source":s["source"],"published":s["published"]} for s in sources}
 doc["generated_at"]=now.isoformat()
 output.write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding="utf-8")
 print("Edición editorial actualizada:",len(doc.get("temas",[])),"temas")
except Exception as exc:
 print("ERROR: no se pudo regenerar el editorial, se mantiene último resultado:",str(exc)[:220])
