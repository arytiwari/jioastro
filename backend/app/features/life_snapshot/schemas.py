"""
Pydantic schemas for Life Snapshot feature.
"""

from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional, List
from uuid import UUID


class LifeTheme(BaseModel):
    """A life theme (e.g., Career Growth, Relationship Harmony)."""

    title: str = Field(..., description="Theme title")
    description: str = Field(..., description="Brief description of the theme")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    planetary_basis: List[str] = Field(default_factory=list, description="Planetary factors")


class LifeRisk(BaseModel):
    """A potential risk or challenge."""

    title: str = Field(..., description="Risk title")
    description: str = Field(..., description="Description of the risk")
    severity: str = Field(..., description="Severity level: low/medium/high")
    date_range: Optional[str] = Field(None, description="When this risk applies")
    mitigation: Optional[str] = Field(None, description="How to mitigate this risk")


class LifeOpportunity(BaseModel):
    """An opportunity or favorable period."""

    title: str = Field(..., description="Opportunity title")
    description: str = Field(..., description="Description of the opportunity")
    window: str = Field(..., description="Time window for this opportunity")
    confidence: float = Field(..., ge=0.0, le=1.0, description="Confidence score 0-1")
    planetary_support: List[str] = Field(default_factory=list, description="Supporting planets")


class LifeAction(BaseModel):
    """An actionable recommendation."""

    action: str = Field(..., description="The action to take")
    priority: str = Field(..., description="Priority: high/medium/low")
    reason: str = Field(..., description="Why this action is recommended")
    when: Optional[str] = Field(None, description="When to take this action")


class SnapshotInsights(BaseModel):
    """Insights from the snapshot."""

    top_themes: List[LifeTheme] = Field(..., description="Top 3 life themes")
    risks: List[LifeRisk] = Field(..., description="3 risks this month")
    opportunities: List[LifeOpportunity] = Field(..., description="3 opportunities")
    actions: List[LifeAction] = Field(..., description="3 recommended actions")
    life_phase: str = Field(..., description="Overall life phase assessment")
    read_time_seconds: int = Field(default=60, description="Estimated read time")


class ProfileSummary(BaseModel):
    """Summary of profile information."""

    id: UUID
    name: str


class SnapshotGenerateRequest(BaseModel):
    """Request to generate a new snapshot."""

    profile_id: UUID = Field(..., description="Profile ID to generate snapshot for")
    force_refresh: bool = Field(default=False, description="Force regeneration even if cached")


class SnapshotResponse(BaseModel):
    """Response containing snapshot data."""

    snapshot_id: UUID
    profile: ProfileSummary
    generated_at: datetime
    expires_at: datetime
    insights: SnapshotInsights
    transits: Optional[List[dict]] = Field(None, description="Current transits")

    class Config:
        from_attributes = True


class SnapshotListItem(BaseModel):
    """Summary item for list of snapshots."""

    id: UUID
    profile_id: UUID
    profile_name: str
    generated_at: datetime
    expires_at: datetime
    is_expired: bool
    themes_count: int

    class Config:
        from_attributes = True


class SnapshotListResponse(BaseModel):
    """Response for list of snapshots."""

    snapshots: List[SnapshotListItem]
    total: int
    limit: int
    offset: int
