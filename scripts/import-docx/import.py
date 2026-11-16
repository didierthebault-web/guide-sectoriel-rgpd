"""Lossless ordered OOXML import. Standard Python library only; never executes source text."""
import argparse, collections, hashlib, html, json, re, shutil, zipfile
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
NS = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
W = '{'+NS['w']+'}'
P = '{http://schemas.microsoft.com/office/word/2010/wordml}paraId'
def text(e):
    return ''.join(x.text or '' if x.tag == W+'t' else '\t' if x.tag == W+'tab' else '\n' if x.tag in [W+'br',W+'cr'] else '' for x in e.iter())
def val(e,path,default=None):
    n=e.find(path,NS)
    return n.get(W+'val',default) if n is not None else default
def dump(path,data):
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def main():
    ap=argparse.ArgumentParser();ap.add_argument('source',nargs='?',default=str(ROOT/'public/documents/FULBI_Guide_RGPD_harmonise_integral_V3.docx'));a=ap.parse_args()
    source=Path(a.source);z=zipfile.ZipFile(source);body=ET.fromstring(z.read('word/document.xml')).find('w:body',NS)
    anomalies=[]
    for tag in ['ins','del','commentRangeStart']:
        if body.findall('.//w:'+tag,NS): raise SystemExit('Révisions/commentaires détectés : examen humain requis avant publication.')
    for note in ['footnotes','endnotes']:
        root=ET.fromstring(z.read('word/'+note+'.xml')) if 'word/'+note+'.xml' in z.namelist() else []
        if any(text(x).strip() for x in root): raise SystemExit('Notes de fond détectées : prise en charge requise avant publication.')
    if any(x.startswith('word/media/') for x in z.namelist()): raise SystemExit('Médias détectés : traitement explicite requis.')
    numbering=ET.fromstring(z.read('word/numbering.xml'));abstract={x.get(W+'abstractNumId'):x for x in numbering.findall('w:abstractNum',NS)}
    nums={x.get(W+'numId'):x for x in numbering.findall('w:num',NS)};counters={};seen=set()
    ledger=[];parts=[];sections=[];current=None;part=None;stack=[];table_no=0
    def inline(p):
        out=''
        for run in p.findall('.//w:r',NS):
            t=html.escape(text(run)).replace('\n','<br>').replace('\t','&#9;')
            if val(run,'w:rPr/w:b','false') not in ['false','0']: t='<strong>'+t+'</strong>'
            elif run.find('w:rPr/w:b',NS) is not None and val(run,'w:rPr/w:b') != '0': t='<strong>'+t+'</strong>'
            if run.find('w:rPr/w:i',NS) is not None and val(run,'w:rPr/w:i') != '0': t='<em>'+t+'</em>'
            out+=t
        return out
    def paragraph(p,idx):
        t=text(p);style=val(p,'w:pPr/w:pStyle','default');num=val(p,'w:pPr/w:numPr/w:numId');level=int(val(p,'w:pPr/w:numPr/w:ilvl','0'));ident=p.get(P) or hashlib.sha256((str(idx)+t).encode()).hexdigest()[:12]
        if ident in seen: ident+='-'+str(idx)
        seen.add(ident)
        rec={'kind':'paragraph','sourceId':ident,'text':t,'style':style,'numId':num,'listLevel':level};ledger.append(rec)
        markup=inline(p);prefix='';list_type=None
        if num:
            spec=nums.get(num);absid=val(spec,'w:abstractNumId') if spec is not None else None
            abstract_node=abstract.get(absid);lvl=abstract_node.find("w:lvl[@w:ilvl='"+str(level)+"']",NS) if abstract_node is not None else None
            fmt=val(lvl,'w:numFmt','bullet') if lvl is not None else 'bullet';start=int(val(lvl,'w:start','1')) if lvl is not None else 1
            key=(num,level);counters[key]=counters.get(key,start-1)+1
            for k in list(counters):
                if k[0]==num and k[1]>level: del counters[k]
            list_type='ul' if fmt=='bullet' else 'ol'
            if fmt not in ['bullet','decimal']: anomalies.append({'type':'list-format','sourceId':ident,'format':fmt})
            rec['listType']=list_type;rec['listNumber']=counters[key]
        rec['html']=f'<p data-source="{ident}">{markup}</p>'
        rec['inline']=markup
        return rec
    def blocks_html(blocks):
        out=[];opened=None
        for b in blocks:
            kind=b.get('listType');key=(kind,b.get('numId'),b.get('listLevel')) if kind else None
            if key != opened:
                if opened: out.append('</'+opened[0]+'>')
                if key: out.append('<'+kind+(f' start="{b["listNumber"]}"' if kind=='ol' else '')+f' class="list-level-{b["listLevel"]}">')
                opened=key
            out.append(f'<li data-source="{b["sourceId"]}">{b["inline"]}</li>' if key else b['html'])
        if opened: out.append('</'+opened[0]+'>')
        return ''.join(out)
    def new_section(t,ident,level,heading=None):
        nonlocal current,stack
        while stack and stack[-1]['level']>=level: stack.pop()
        current={'id':ident,'part':part['id'],'title':t,'level':level,'parent':stack[-1]['id'] if stack else None,'blocks':[],'heading':heading}
        stack.append(current);sections.append(current);part['sections'].append(ident)
    for idx,e in enumerate(body):
        if e.tag==W+'p':
            b=paragraph(e,idx);t=b['text'];m=re.match(r'^PARTIE (VII|VI|IV|V|III|II|I)\b',t)
            if m:
                part={'id':m[1],'title':t,'sections':[],'provisional':m[1]=='VI'};parts.append(part);stack=[]
                new_section(t,part['id']+'-introduction',1,b);continue
            if part is None:
                part={'id':'liminaire','title':'Présentation et préambule','sections':[],'provisional':False};parts.append(part)
                new_section(part['title'],'liminaire-introduction',1)
            fiche=re.match(r'^FICHE (\d{2})\s',t);h=re.match(r'^Titre([123])$',b['style'])
            if fiche or (h and b['style']!='Titre1'):
                level=2 if fiche else int(h[1]);ident=(part['id']+'-fiche-'+fiche[1]) if fiche else part['id']+'-'+b['sourceId'].lower()
                if any(s['id']==ident for s in sections):
                    anomalies.append({'type':'duplicate-fiche','sourceId':b['sourceId'],'text':t,'note':'Complément conservé à sa place, sans fusion avec la fiche initiale.'});ident+='-complement-'+b['sourceId'].lower()
                if fiche: anomalies.append({'type':'fiche-without-heading-style','sourceId':b['sourceId'],'text':t})
                if h and re.match(r'^\d+\. ',t) and len(t)>110: anomalies.append({'type':'heading-to-review','sourceId':b['sourceId'],'text':t})
                new_section(t,ident,level,b)
            else: current['blocks'].append(b)
        elif e.tag==W+'tbl':
            table_no+=1;rows=[];table_text=[]
            for ri,row in enumerate(e.findall('w:tr',NS)):
                cells=[]
                for ci,cell in enumerate(row.findall('w:tc',NS)):
                    if cell.findall('w:tbl',NS): raise SystemExit('Tableau imbriqué non pris en charge')
                    bs=[paragraph(p,f'{idx}-{ri}-{ci}-{pi}') for pi,p in enumerate(cell.findall('w:p',NS))]
                    span=val(cell,'w:tcPr/w:gridSpan','1');merge=cell.find('w:tcPr/w:vMerge',NS)
                    if merge is not None: raise SystemExit('Fusion verticale : traitement explicite requis')
                    tag='th' if ri==0 else 'td';cells.append(f'<{tag}'+(' scope="col"' if ri==0 else '')+(f' colspan="{span}"' if span!='1' else '')+'>'+blocks_html(bs)+f'</{tag}>');table_text.extend(b['text'] for b in bs)
                rows.append('<tr>'+''.join(cells)+'</tr>')
            table={'kind':'table','sourceId':f'table-{table_no}','text':'\n'.join(table_text),'html':f'<div class="table-scroll" role="region" aria-label="Tableau {table_no} — {html.escape(current["title"],quote=True)}" tabindex="0"><table><caption>Tableau {table_no} · {html.escape(current["title"])}</caption><thead>{rows[0]}</thead><tbody>{"".join(rows[1:])}</tbody></table></div>'}
            ledger.append({k:v for k,v in table.items() if k!='html'});current['blocks'].append(table)
        elif e.tag!=W+'sectPr': raise SystemExit('Bloc OOXML non pris en charge : '+e.tag)
    for s in sections:
        s['html']=blocks_html(s['blocks']);s['hash']=hashlib.sha256(json.dumps({'heading':s['heading'],'blocks':s['blocks']},ensure_ascii=False,sort_keys=True).encode()).hexdigest()
    tools=[]
    for table in body.findall('w:tbl',NS):
        for row in table.findall('w:tr',NS):
            cells=[text(c).strip() for c in row.findall('w:tc',NS)]
            if cells and re.fullmatch('O\\d{2}',cells[0]):
                code=cells[0];section=next(s for s in sections if s['part']=='VII' and re.search(r'\b'+code+r'\b',s['title']))
                tools.append({'code':code,'title':cells[1],'description':cells[2],'purpose':cells[2],'parts':cells[3],'section':section['id'],'version':'V3','date':None,'format':'Texte dans le guide','status':'Modèle consultable · fichier modifiable non fourni','download':None})
    fiches=[{'id':s['id'],'title':s['title'],'complements':[x['id'] for x in sections if x['id'].startswith(s['id']+'-complement-')]} for s in sections if '-fiche-' in s['id'] and '-complement-' not in s['id']]
    assert len(parts)==8 and len(fiches)==20 and len(tools)==18 and table_no==60, 'Structure inattendue'
    sha=hashlib.sha256(source.read_bytes()).hexdigest()
    guide={'version':'V3','updated':'2026-11-16','source':source.name,'sourceSha256':sha,'parts':parts,'sections':sections,'fiches':fiches,'tools':tools}
    dump(ROOT/'src/data/guide.json',guide)
    dest=ROOT/'public/documents'/source.name;dest.parent.mkdir(parents=True,exist_ok=True)
    if source.resolve()!=dest.resolve(): shutil.copyfile(source,dest)
    validation_path=ROOT/'src/data/validations.json';previous={s['id']:s for s in json.loads(validation_path.read_text(encoding='utf-8'))} if validation_path.exists() else {}
    validations=[]
    for s in sections:
        prev=previous.get(s['id']);v=prev or {'id':s['id'],'status':'Non examinée','date':None,'decision':None,'outstanding':[],'contentHash':s['hash'],'version':'V3'}
        if prev and prev['contentHash']!=s['hash']:
            v={**v,'status':'À réexaminer','previousDecision':{k:prev.get(k) for k in ['date','decision','contentHash','version']},'date':None,'decision':None,'contentHash':s['hash'],'version':'V3'}
        validations.append(v)
    dump(validation_path,validations)
    # Ledger intentionally records the exact source paragraph sequence including table cells and empty paragraphs.
    audit=[{k:v for k,v in b.items() if k not in ['html','inline']} for b in ledger]
    dump(ROOT/'reports/source-ledger.json',audit)
    report={'sourceSha256':sha,'parts':7,'sections':len(sections),'fiches':len(fiches),'tools':len(tools),'tables':table_no,'paragraphs':sum(b['kind']=='paragraph' for b in audit),'listItems':sum(bool(b.get('numId')) for b in audit),'headings':sum(b.get('style','').startswith('Titre') for b in audit),'anomalies':anomalies,'notes':'Préambule conservé. Champ TOC Word conservé par son texte visible ; sommaire web généré. Séparateurs décoratifs VML exclus. Aucun média, commentaire, suivi de modification ou note de fond. Titres Word conservés même lorsque leur style paraît incohérent. En-têtes de colonnes web déduits de la première ligne ; aucun libellé source réécrit.'}
    dump(ROOT/'reports/concordance.json',report);dump(ROOT/'public/documents/concordance.json',report)
    (ROOT/'reports/concordance.md').write_text('# Concordance documentaire\n\n'+json.dumps(report,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps({k:v for k,v in report.items() if k not in ['anomalies','notes']},ensure_ascii=True))
if __name__=='__main__': main()
