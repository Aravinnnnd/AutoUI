"""Tool input schemas using pydantic (partial translation of Zod schemas)."""
from __future__ import annotations
from typing import Any, Dict, List, Optional, Union
from pydantic import BaseModel, Field, root_validator
from ..data.design_guides_loader import DESIGN_GUIDES


class CreateOp(BaseModel):
    op: str = Field("create", const=True)
    type: str
    x: float
    y: Union[float, str]
    width: Optional[float]
    height: Optional[float]
    ref: Optional[str]
    props: Optional[Dict[str, Any]]


class UpdateOp(BaseModel):
    op: str = Field("update", const=True)
    id: str
    x: Optional[float]
    y: Optional[float]
    width: Optional[float]
    height: Optional[float]
    props: Optional[Dict[str, Any]]


class DeleteOp(BaseModel):
    op: str = Field("delete", const=True)
    ids: List[str]


BatchOperation = Union[CreateOp, UpdateOp, DeleteOp]


class BatchDesignInput(BaseModel):
    operations: List[BatchOperation]
    clearFirst: Optional[bool] = False


class BatchGetInput(BaseModel):
    ids: Optional[List[str]]
    types: Optional[List[str]]
    name: Optional[str]


class ScreenshotInput(BaseModel):
    sectionName: Optional[str]
    shapeIds: Optional[List[str]]
    mode: Optional[str]


class ClearCanvasInput(BaseModel):
    pass


class ZoomToFitInput(BaseModel):
    pass


class DesignGuideInput(BaseModel):
    topic: str

    @root_validator
    def validate_topic(cls, values):
        topic = values.get("topic")
        topics = list(DESIGN_GUIDES.keys())
        if topic not in topics:
            raise ValueError(f"Unknown topic: {topic}. Available: {', '.join(topics)}")
        return values


class ListComponentsInput(BaseModel):
    pass


class ListIconsInput(BaseModel):
    pass
