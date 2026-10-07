
import json,os,uuid
from pathlib import Path
from fastapi import HTTPException
def valid_id(value):
    try:return str(uuid.UUID(value))
    except (ValueError,TypeError):raise HTTPException(404,'Không tìm thấy tài liệu.')
class Store:
    def __init__(self):
        self.token=os.getenv('BLOB_READ_WRITE_TOKEN')
        self.local=Path(os.getenv('PDP_LOCAL_STORE',str(Path(__file__).resolve().parents[1]/'.local-data')))
    def path(self,owner,id):return f'workspaces/{valid_id(owner)}/documents/{valid_id(id)}.json'
    async def put(self,owner,doc):
        path=self.path(owner,doc['id']);raw=json.dumps(doc,ensure_ascii=False).encode()
        if self.token:
            from vercel.blob import AsyncBlobClient
            try:await AsyncBlobClient(token=self.token).put(path,raw,access='private',content_type='application/json',overwrite=False)
            except Exception:raise HTTPException(503,'Chưa lưu được vào kho dữ liệu. Nội dung vẫn còn trên màn hình; hãy thử lại.')
        elif os.getenv('VERCEL'):raise HTTPException(503,'Kho lưu trữ chưa được cấu hình.')
        else:
            target=self.local/path;target.parent.mkdir(parents=True,exist_ok=True)
            with target.open('xb') as f:f.write(raw)
    async def get(self,owner,id):
        path=self.path(owner,id)
        if self.token:
            from vercel.blob import AsyncBlobClient
            try:
                result=await AsyncBlobClient(token=self.token).get(path,access='private',use_cache=False)
                if result is None or result.status_code!=200:raise HTTPException(404,'Không tìm thấy tài liệu trong không gian của bạn.')
                return json.loads(result.content)
            except HTTPException:raise
            except Exception:raise HTTPException(503,'Không đọc được kho dữ liệu. Hãy thử lại.')
        elif os.getenv('VERCEL'):raise HTTPException(503,'Kho lưu trữ chưa được cấu hình.')
        try:return json.loads((self.local/path).read_text(encoding='utf8'))
        except FileNotFoundError:raise HTTPException(404,'Không tìm thấy tài liệu trong không gian của bạn.')
    async def list(self,owner):
        prefix=f'workspaces/{valid_id(owner)}/documents/'
        if self.token:
            from vercel.blob import AsyncBlobClient
            paths=[];cursor=None
            try:
                client=AsyncBlobClient(token=self.token)
                while True:
                    page=await client.list_objects(prefix=prefix,limit=100,cursor=cursor)
                    paths.extend(b.pathname for b in page.blobs)
                    if not page.has_more:break
                    cursor=page.cursor
                    if len(paths)>1000:break
            except Exception:raise HTTPException(503,'Không đọc được danh sách tài liệu.')
            docs=[await self.get(owner,Path(p).stem) for p in paths]
        elif os.getenv('VERCEL'):raise HTTPException(503,'Kho lưu trữ chưa được cấu hình.')
        else:docs=[json.loads(p.read_text(encoding='utf8')) for p in (self.local/prefix).glob('*.json')]
        return sorted(docs,key=lambda d:d['created_at'],reverse=True)
