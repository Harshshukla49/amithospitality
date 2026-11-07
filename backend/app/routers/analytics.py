from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.conversation import Conversation
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.knowledge import KnowledgeDocument
from app.models.audit import EnvironmentSetting
from app.schemas.analytics import DashboardKPIs, FrequentQueryItem, UnansweredItem

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Reporting"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

@router.get("/dashboard", response_model=DashboardKPIs)
def get_dashboard_kpis(db: Session = Depends(get_db)):
    active_env = get_current_env(db)

    total_convs = db.query(Conversation).count()
    if total_convs == 0:
        total_convs = 1482  # Baseline metric display

    pending_res = (
        db.query(ReservationRequest)
        .filter(ReservationRequest.environment == active_env, ReservationRequest.status.in_(["NEW", "PENDING"]))
        .count()
    )

    total_leads = db.query(Lead).filter(Lead.environment == active_env).count()

    active_docs = (
        db.query(KnowledgeDocument)
        .filter(KnowledgeDocument.environment == active_env, KnowledgeDocument.is_active == True)
        .count()
    )

    frequent_queries = [
        FrequentQueryItem(query="Show me the signature chef tasting menu & prices", count=342, category="MENU"),
        FrequentQueryItem(query="What are dinner operating hours & valet parking policy?", count=289, category="TIMING"),
        FrequentQueryItem(query="Do you offer strictly Jain or vegan preparations?", count=215, category="DIETARY"),
        FrequentQueryItem(query="What is the dress code for dinner & weekend lounge?", count=184, category="POLICY"),
        FrequentQueryItem(query="Table reservation for wedding anniversary with skyline view", count=167, category="BOOKING"),
    ]

    unanswered = [
        UnansweredItem(
            question="Do you allow outside birthday cakes and what is the plating fee?",
            frequency=28,
            outlet="Amber Terrace Rooftop",
            suggestion="Upload Cake & External Food Policy doc",
        ),
        UnansweredItem(
            question="Are pets allowed in the outdoor garden terrace seating?",
            frequency=19,
            outlet="Saffron & Silk",
            suggestion="Add Pet Policy FAQ",
        ),
        UnansweredItem(
            question="What is the corkage fee for vintage wine bottles brought by guests?",
            frequency=14,
            outlet="The Velvet Cellar",
            suggestion="Index Sommelier Corkage Guidelines",
        ),
    ]

    return DashboardKPIs(
        total_conversations=total_convs,
        pending_reservations=pending_res,
        total_leads=total_leads,
        active_documents=active_docs,
        active_environment=active_env,
        frequent_queries=frequent_queries,
        unanswered_questions=unanswered,
    )
