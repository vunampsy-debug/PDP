
import json,re,os
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
if os.getenv('PDP_KNOWLEDGE_JSON'):
    bundle=json.loads(os.environ['PDP_KNOWLEDGE_JSON'])
    CORPUS=bundle['corpus'];RUBRICS=bundle['rubrics'];MANIFEST=bundle['manifest']
elif not os.getenv('VERCEL'):
    CORPUS=[json.loads(x) for x in (ROOT/'data/corpus.jsonl').read_text(encoding='utf8').splitlines()]
    RUBRICS=json.loads((ROOT/'data/rubrics.json').read_text(encoding='utf8'))
    MANIFEST=json.loads((ROOT/'data/manifest.json').read_text(encoding='utf8'))
else:
    raise RuntimeError('PDP_KNOWLEDGE_JSON is required on Vercel; source documents are not committed to public GitHub.')
def retrieve(inputs):
    words=set(re.findall(r'\w+',(inputs.lesson+' '+inputs.context).lower()))
    eligible=[r for r in CORPUS if r['role']=='official_source' and r['filename']!='TH_INI&SED.xlsx']
    ranked=sorted(eligible,key=lambda r:sum(len(w)>2 and w in r['text'].lower() for w in words),reverse=True)
    return [{k:r[k] for k in ['id','filename','locator','text']} for r in ranked[:5]]
def rubric_for(codes):
    return [RUBRICS[c] for c in codes if c in RUBRICS]
def validate(inputs,content):
    errors=[]
    if len(set(inputs.indicators))!=len(inputs.indicators): errors.append('Chọn các mã chỉ báo khác nhau.')
    if any(c not in RUBRICS for c in inputs.indicators): errors.append('Mã chỉ báo không thuộc khung INI&SED lớp 5.')
    if not content.title.strip() or len(content.rationale.strip())<20: errors.append('Thiếu tên hoặc lý do tích hợp.')
    if not content.sections or any(len(s.content.strip())<20 or not s.heading.strip() for s in content.sections): errors.append('Các phần nội dung cần hướng dẫn cụ thể.')
    if content.integration=='Tích hợp':
        if len({e.kind for e in content.evidence if len(e.description.strip())>=15 and len(e.method.strip())>=10})<2: errors.append('Cần ít nhất hai loại minh chứng khác nhau, kèm cách thu thập.')
        if any(len(s.strip())<15 for s in [content.reflection_before,content.reflection_during,content.reflection_after]): errors.append('Thiếu câu hỏi phản tư trước, trong hoặc sau hoạt động.')
    if inputs.mode=='V1':
        if not content.reference_rows: errors.append('Bảng tham chiếu chưa có dòng nội dung.')
        for row in content.reference_rows:
            if not all(getattr(row,k).strip() for k in ['topic','lesson','subject_goal','touchpoint','pedagogy','evidence','assessment']): errors.append('Bảng tham chiếu còn ô trống.')
            if len(row.indicators)>2 or any(c not in inputs.indicators for c in row.indicators): errors.append('Dòng tham chiếu dùng chỉ báo ngoài lựa chọn.')
            if content.integration=='Tích hợp' and not row.indicators: errors.append('Dòng tích hợp thiếu mã chỉ báo.')
    if inputs.mode in ['V2','V3','V4'] and content.integration=='Tích hợp' and len(content.sections)<5: errors.append('Cần ít nhất 5 phần thể hiện nhiệm vụ, tiến trình và đánh giá.')
    if inputs.mode=='V2' and content.integration=='Tích hợp' and len(content.sections)<7: errors.append('V2 cần đủ 7 phần của kế hoạch bài dạy.')
    codes=re.findall(r'(?:5\.)?INI&SED-\d{2}\.\d+',json.dumps(content.model_dump(),ensure_ascii=False))
    if any((c if c.startswith('5.') else '5.'+c) not in inputs.indicators for c in codes): errors.append('Nội dung có mã chỉ báo ngoài lựa chọn.')
    return {'errors':list(dict.fromkeys(errors)),'warnings':['YCCĐ do giáo viên cung cấp; chưa tự động đối chiếu SGK/CTGDPT gốc.','Kiểm tra cấu trúc không xác nhận chất lượng sư phạm hay mức năng lực học sinh.'],'structurally_complete':not errors}
