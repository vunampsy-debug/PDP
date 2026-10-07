
from typing import Literal
from pydantic import BaseModel, Field, ConfigDict
class Strict(BaseModel):
    model_config=ConfigDict(extra='forbid')
class Inputs(Strict):
    mode: Literal['V1','V2','V3','V4']='V4'
    author: str=Field(min_length=2,max_length=80)
    lesson: str=Field(min_length=3,max_length=160)
    subject_goal: str=Field(min_length=15,max_length=3000)
    source_name: str=Field(min_length=3,max_length=200)
    source_excerpt: str=Field(min_length=30,max_length=24000)
    context: str=Field(min_length=15,max_length=3000)
    minutes: int=Field(default=35,ge=15,le=240)
    indicators: list[str]=Field(min_length=1,max_length=2)
    reference_id: str=''
class Section(Strict):
    heading: str
    content: str
class Evidence(Strict):
    kind: Literal['Sản phẩm','Kế hoạch','Quan sát','Phản tư','Trao đổi']
    description: str
    method: str
class ReferenceRow(Strict):
    topic: str
    lesson: str
    subject_goal: str
    indicators: list[str]
    touchpoint: str
    pedagogy: str
    evidence: str
    assessment: str
class Generated(Strict):
    title: str
    integration: Literal['Tích hợp','Không tích hợp']
    rationale: str
    sections: list[Section]
    evidence: list[Evidence]
    reflection_before: str
    reflection_during: str
    reflection_after: str
    reference_rows: list[ReferenceRow]
class SaveRequest(Strict):
    inputs: Inputs
    content: Generated
    parent_id: str=''
class ReviewRequest(Strict):
    code: str=Field(min_length=1,max_length=100)
    reviewer: str=Field(min_length=2,max_length=80)
    note: str=Field(min_length=10,max_length=2000)
    source_confirmed: bool
