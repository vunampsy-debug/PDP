
import os,json,copy,sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
os.environ['PDP_REVIEW_CODE']='test-only-code'
import pytest
from fastapi.testclient import TestClient
import app as module
from core.storage import Store
from core.models import Inputs,Generated
from core.knowledge import validate,RUBRICS
@pytest.fixture
def client(tmp_path,monkeypatch):
    storage=Store();storage.token=None;storage.local=tmp_path
    monkeypatch.setattr(module,'store',storage)
    module.RATE.clear()
    return TestClient(module.app)
def test_samples_private_storage_and_unicode_exports(client):
    d=client.get('/api/sample').json()
    assert d['origin']=='sample' and not d['validation']['errors']
    assert client.get('/api/documents').json()[0]['id']==d['id']
    for kind in ['docx','xlsx','pdf']:
        r=client.get(f'/api/documents/{d["id"]}/export/{kind}')
        assert r.status_code==200 and len(r.content)>2000
        if kind=='pdf':
            from pypdf import PdfReader
            from io import BytesIO
            text=''.join(p.extract_text() for p in PdfReader(BytesIO(r.content)).pages)
            assert 'Góc đọc sách' in text and 'Nguồn YCCĐ' in text and 'Sau khi làm' in text
    client.cookies.clear()
    assert client.get('/api/documents/'+d['id']).status_code==404
def test_regression_empty_unknown_and_single_evidence(client):
    d=client.get('/api/sample').json();i=Inputs.model_validate(d['inputs']);c=Generated.model_validate(d['content'])
    c.sections=[];c.evidence=[]
    assert validate(i,c)['errors']
    i.mode='V1';assert 'Bảng tham chiếu chưa có dòng nội dung.' in validate(i,c)['errors']
    i.indicators=['5.INI&SED-99.9'];assert validate(i,c)['errors']
    c=Generated.model_validate(d['content']);c.evidence=c.evidence[:1]
    assert validate(Inputs.model_validate(d['inputs']),c)['errors']
def test_review_and_v2_linkage(client,monkeypatch):
    sample=client.get('/api/sample').json()
    review={'code':'test-only-code','reviewer':'Người kiểm tra','note':'Đã đối chiếu nguồn và kiểm tra dữ kiện Toán.','source_confirmed':True}
    assert client.post(f'/api/documents/{sample["id"]}/approve',json=review).status_code==422
    inp=sample['inputs'];inp['mode']='V1'
    content=sample['content'];content['reference_rows']=[{'topic':'Số thập phân','lesson':inp['lesson'],'subject_goal':inp['subject_goal'],'indicators':inp['indicators'],'touchpoint':content['rationale'],'pedagogy':'Học qua tình huống và kiểm tra chéo.','evidence':'Kế hoạch cá nhân và ghi chú quan sát.','assessment':'Đối chiếu rubric gốc và quan sát quá trình.'}]
    d=client.post('/api/save',json={'inputs':inp,'content':content}).json()
    module.RATE.clear();review['code']='incorrect'
    assert client.post(f'/api/documents/{d["id"]}/approve',json=review).status_code==403
    module.RATE.clear();review['code']='test-only-code';review['source_confirmed']=False
    assert client.post(f'/api/documents/{d["id"]}/approve',json=review).status_code==422
    module.RATE.clear();review['source_confirmed']=True
    approved=client.post(f'/api/documents/{d["id"]}/approve',json=review).json()
    assert approved['status']=='approved' and approved['parent_id']==d['id']
    assert client.get('/api/documents/'+d['id']).json()['status']=='draft'
    v2=copy.deepcopy(inp);v2['mode']='V2'
    assert client.post('/api/generate',json=v2).status_code==422
    v2['reference_id']=d['id'];assert client.post('/api/generate',json=v2).status_code==422
    v2['reference_id']=approved['id'];v2['subject_goal']='Một YCCĐ khác không đúng với bản tham chiếu.'
    assert client.post('/api/generate',json=v2).status_code==422
    v2['subject_goal']=inp['subject_goal']
    async def fake_generate(inputs,ref):
        assert ref['status']=='approved'
        return Generated.model_validate(content),[], 'test_response'
    monkeypatch.setattr(module.ai,'generate',fake_generate)
    out=client.post('/api/generate',json=v2)
    assert out.status_code==200 and out.json()['status']=='draft'
def test_missing_key_is_honest_and_csrf(client,monkeypatch):
    d=client.get('/api/sample').json()
    monkeypatch.delenv('OPENAI_API_KEY',raising=False)
    r=client.post('/api/generate',json=d['inputs'])
    assert r.status_code==503 and 'OpenAI' in r.json()['detail']
    assert client.post('/api/save',json={'inputs':d['inputs'],'content':d['content']},headers={'Origin':'https://other.example'}).status_code==403
def test_source_upload_and_framework(client):
    assert len(RUBRICS)==9 and all(len(r['levels'])==4 for r in RUBRICS.values())
    r=client.post('/api/extract',files={'file':('source.txt','Nội dung nguồn tham khảo được giáo viên bổ sung để đối chiếu yêu cầu cần đạt.'.encode(),'text/plain')})
    assert r.status_code==200 and 'đối chiếu' in r.json()['text']
    assert client.post('/api/extract',files={'file':('empty.txt',b'','text/plain')}).status_code==422
    assert client.post('/api/extract',files={'file':('large.txt',b'x'*3000001,'text/plain')}).status_code==413
