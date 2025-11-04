"""Knowledge Base API Endpoints - Rule Retrieval and Search"""

from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.services.rule_retrieval import rule_retrieval_service
from app.services.knowledge_base import knowledge_base_service

router = APIRouter()


# Request/Response Models
class RuleRetrievalRequest(BaseModel):
    """Request for retrieving relevant rules"""
    chart_data: Dict[str, Any] = Field(..., description="Birth chart planetary positions")
    query: Optional[str] = Field(None, description="Optional natural language query")
    domain: Optional[str] = Field(None, description="Domain filter (career, wealth, etc.)")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum number of rules to return")
    min_weight: float = Field(default=0.3, ge=0.0, le=1.0, description="Minimum rule weight threshold")

    class Config:
        json_schema_extra = {
            "example": {
                "chart_data": {
                    "planets": {
                        "Sun": {"sign": "Capricorn", "house": 11, "degree": 15.5},
                        "Moon": {"sign": "Leo", "house": 6, "degree": 22.3},
                        "Mars": {"sign": "Scorpio", "house": 9, "degree": 8.7}
                    },
                    "ascendant": {"sign": "Pisces", "degree": 1.27}
                },
                "query": "Tell me about career prospects",
                "domain": "career",
                "limit": 10,
                "min_weight": 0.5
            }
        }


class RuleResponse(BaseModel):
    """Individual rule response"""
    rule_id: str
    domain: str
    condition: str
    effect: str
    weight: float
    anchor: str
    commentary: Optional[str] = None
    relevance_score: Optional[float] = None
    semantic_score: Optional[float] = None
    symbolic_match: Optional[bool] = None


class RuleRetrievalResponse(BaseModel):
    """Response from rule retrieval"""
    rules: List[RuleResponse]
    retrieval_method: str
    total_matches: int
    query_time_ms: float
    symbolic_keys_used: List[str]


class KnowledgeBaseStats(BaseModel):
    """Knowledge base statistics"""
    total_rules: int
    rules_with_embeddings: int
    total_symbolic_keys: int
    rules_by_domain: Dict[str, int]
    coverage_percentage: float


# Endpoints

@router.post("/retrieve", response_model=RuleRetrievalResponse)
async def retrieve_rules(request: RuleRetrievalRequest):
    """
    Retrieve relevant astrological rules based on birth chart and optional query

    Uses hybrid RAG approach combining:
    - Symbolic key matching (fast exact matches)
    - Semantic similarity search (contextual understanding)
    - Rule weight prioritization

    Returns rules sorted by relevance with metadata about retrieval method and performance
    """
    try:
        result = await rule_retrieval_service.retrieve_rules(
            chart_data=request.chart_data,
            query=request.query,
            domain=request.domain,
            limit=request.limit,
            min_weight=request.min_weight
        )

        # Format rules for response
        formatted_rules = []
        for rule in result['rules']:
            formatted_rules.append(RuleResponse(
                rule_id=rule['rule_id'],
                domain=rule['domain'],
                condition=rule['condition'],
                effect=rule['effect'],
                weight=rule['weight'],
                anchor=rule['anchor'],
                commentary=rule.get('commentary'),
                relevance_score=rule.get('relevance_score'),
                semantic_score=rule.get('semantic_score'),
                symbolic_match=rule.get('symbolic_match')
            ))

        return RuleRetrievalResponse(
            rules=formatted_rules,
            retrieval_method=result['retrieval_method'],
            total_matches=result['total_matches'],
            query_time_ms=result['query_time_ms'],
            symbolic_keys_used=result.get('symbolic_keys_used', [])
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Rule retrieval failed: {str(e)}"
        )


@router.get("/rules/{rule_id}", response_model=Dict[str, Any])
async def get_rule(rule_id: str):
    """
    Get detailed information about a specific rule

    Returns complete rule data including Sanskrit text, translations, modifiers, and metadata
    """
    try:
        # Query rule by rule_id
        query = knowledge_base_service.db.client.from_("kb_rules")\
            .select("*")\
            .eq("rule_id", rule_id)\
            .eq("status", "active")\
            .execute()

        if not query.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rule {rule_id} not found"
            )

        return query.data[0]

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve rule: {str(e)}"
        )


@router.get("/stats", response_model=KnowledgeBaseStats)
async def get_knowledge_base_stats():
    """
    Get comprehensive knowledge base statistics

    Returns information about total rules, embeddings, symbolic keys,
    and breakdown by domain
    """
    try:
        # Get total counts via count_rules() which returns a dict
        counts = await knowledge_base_service.count_rules()
        total_rules = counts.get("total_rules", 0)
        rules_with_embeddings = counts.get("rules_with_embeddings", 0)
        symbolic_keys = counts.get("symbolic_keys", 0)

        # Get rules by domain
        domains = ["career", "wealth", "relationships", "health", "education", "spirituality", "general"]
        rules_by_domain = {}

        for domain in domains:
            domain_rules = await knowledge_base_service.get_rules_by_domain(domain, limit=1000)
            rules_by_domain[domain] = len(domain_rules)

        # Calculate coverage (assuming target of 120 rules)
        target_rules = 120
        coverage_percentage = (total_rules / target_rules) * 100 if total_rules else 0

        return KnowledgeBaseStats(
            total_rules=total_rules,
            rules_with_embeddings=rules_with_embeddings,
            total_symbolic_keys=symbolic_keys,
            rules_by_domain=rules_by_domain,
            coverage_percentage=round(coverage_percentage, 2)
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve statistics: {str(e)}"
        )


@router.get("/domains", response_model=List[str])
async def get_domains():
    """
    Get list of available rule domains

    Returns all domains that have rules in the knowledge base
    """
    return ["career", "wealth", "relationships", "health", "education", "spirituality", "general"]


@router.get("/rules/domain/{domain}", response_model=List[RuleResponse])
async def get_rules_by_domain(
    domain: str,
    limit: int = 50,
    min_weight: float = 0.0
):
    """
    Get all rules for a specific domain

    Returns rules filtered by domain and optionally by minimum weight,
    sorted by weight in descending order
    """
    try:
        rules = await knowledge_base_service.get_rules_by_domain(domain, limit=limit)

        # Filter by weight
        rules = [r for r in rules if r.get('weight', 0) >= min_weight]

        # Format response
        formatted_rules = []
        for rule in rules:
            formatted_rules.append(RuleResponse(
                rule_id=rule['rule_id'],
                domain=rule['domain'],
                condition=rule['condition'],
                effect=rule['effect'],
                weight=rule['weight'],
                anchor=rule['anchor'],
                commentary=rule.get('commentary')
            ))

        return formatted_rules

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to retrieve domain rules: {str(e)}"
        )
