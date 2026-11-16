"""Independent source-vs-built-HTML concordance, including exact ordered paragraph text."""
from pathlib import Path
from html.parser import HTMLParser
import hashlib,json,xml.etree.ElementTree as ET,zipfile
ROOT=Path(__file__).resolve().parents[2]
class Extract(HTMLParser):
    def __init__(self): super().__init__(convert_charrefs=True);self.items=[];self.active=None;self.tables=0;self.lists=0;self.headings=0
    def handle_starttag(self,tag,attrs):
        d=dict(attrs)
        if tag=='table': self.tables+=1
        if 'data-source' in d and d['data-source']:
            if self.active is not None: raise AssertionError('Bloc source imbriqué')
            self.active={'tag':tag,'id':d['data-source'],'text':''};self.items.append(self.active)
            if tag=='li': self.lists+=1
            if tag in ['h1','h2','h3']: self.headings+=1
        elif self.active is not None and tag=='br': self.active['text']+='\n'
    def handle_data(self,data):
        if self.active is not None:self.active['text']+=data
    def handle_endtag(self,tag):
        if self.active is not None and self.active['tag']==tag:self.active=None
def main():
    g=json.loads((ROOT/'src/data/guide.json').read_text(encoding='utf-8'));source=ROOT/'public/documents'/g['source'];z=zipfile.ZipFile(source);w='{http://schemas.openxmlformats.org/wordprocessingml/2006/main}';body=ET.fromstring(z.read('word/document.xml')).find(w+'body')
    expected=[''.join(x.text or '' if x.tag==w+'t' else '\t' if x.tag==w+'tab' else '\n' if x.tag in [w+'br',w+'cr'] else '' for x in p.iter()) for p in body.iter(w+'p')]
    actual=[];tables=lists=0
    for part in g['parts']:
        parser=Extract();parser.feed((ROOT/'dist/parties'/part['id'].lower()/'index.html').read_text(encoding='utf-8'));actual.extend(x['text'] for x in parser.items);tables+=parser.tables;lists+=parser.lists
    errors=[{'position':i,'source':a,'published':b} for i,(a,b) in enumerate(zip(expected,actual)) if a!=b]
    assert len(expected)==len(actual),(len(expected),len(actual))
    assert not errors,errors[:5]
    assert tables==len(list(body.iter(w+'tbl')))==60
    assert lists==len([p for p in body.iter(w+'p') if p.find(w+'pPr/'+w+'numPr') is not None])
    ids=[]
    for s in g['sections']:
        p=ROOT/'dist/sections'/s['id']/'index.html';assert p.exists(),s['id'];html=p.read_text(encoding='utf-8');assert f'id="{s["id"]}"' in html;assert 'data-pagefind-body' in html;ids.append(s['id'])
    assert len(set(ids))==len(ids)
    assert hashlib.sha256(source.read_bytes()).hexdigest()==g['sourceSha256']
    result={'result':'PASS','paragraphsCompared':len(expected),'order':'identical','text':'identical including empty paragraphs and table cells','tablesCompared':tables,'listItemsCompared':lists,'sectionPages':len(ids),'uniqueAnchors':len(ids),'sourceSha256':g['sourceSha256']}
    (ROOT/'reports/published-concordance.json').write_text(json.dumps(result,ensure_ascii=False,indent=2)+'\n',encoding='utf-8');print(json.dumps(result))
if __name__=='__main__': main()
