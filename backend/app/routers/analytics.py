import csv
import io
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from fastapi import APIRouter, Depends, Query, Response, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func

from app.database import get_db
from app.models.conversation import Conversation, Message
from app.models.reservation import ReservationRequest
from app.models.lead import Lead
from app.models.knowledge import KnowledgeDocument
from app.models.outlet import Outlet
from app.models.audit import EnvironmentSetting
from app.models.user import User
from app.schemas.analytics import DashboardKPIs, FrequentQueryItem, UnansweredItem
from app.utils.security import require_roles, get_current_user_optional

router = APIRouter(prefix="/api/v1/analytics", tags=["Analytics & Reporting"])

def get_current_env(db: Session) -> str:
    setting = db.query(EnvironmentSetting).order_by(EnvironmentSetting.id.desc()).first()
    return setting.active_environment if setting else "DEMO"

def get_date_cutoff(date_range: Optional[str]) -> Optional[datetime]:
    if not date_range or date_range == "ALL":
        return None
    now = datetime.utcnow()
    if date_range == "24H":
        return now - timedelta(hours=24)
    if date_range == "7D":
        return now - timedelta(days=7)
    if date_range == "30D":
        return now - timedelta(days=30)
    return None

@router.get("/dashboard", response_model=DashboardKPIs)
def get_dashboard_kpis(
    date_range: Optional[str] = Query("7D", description="24H, 7D, 30D, ALL"),
    outlet_id: Optional[int] = Query(None, description="Optional outlet filter"),
    environment: Optional[str] = Query(None, description="DEMO or REAL"),
    current_user: Optional[User] = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
):
    """
    Compute live operational KPIs and analytics directly from PostgreSQL/SQLite database.
    Strictly isolated by active environment, user outlet authorization, and date-range cutoff.
    """
    # Normalize params if function is called directly in test suites without FastAPI DI
    if not isinstance(date_range, str):
        date_range = getattr(date_range, "default", "7D")
    if not isinstance(outlet_id, int):
        outlet_id = getattr(outlet_id, "default", None)
    if not isinstance(environment, str):
        environment = getattr(environment, "default", None)

    # Multi-outlet tenant isolation:
    if current_user and getattr(current_user, "role", None) in ("STAFF", "MANAGER") and getattr(current_user, "outlet_id", None):
        if outlet_id is not None and outlet_id != current_user.outlet_id:
            raise HTTPException(
                status_code=403,
                detail=f"Cross-outlet access forbidden: You are assigned to outlet {current_user.outlet_id} and cannot view analytics for outlet {outlet_id}.",
            )
        outlet_id = current_user.outlet_id

    target_env = environment if isinstance(environment, str) and environment else get_current_env(db)
    cutoff = get_date_cutoff(date_range)

    # 1. Outlet Name Resolution
    outlet_name = None
    if outlet_id:
        out = db.query(Outlet).filter(Outlet.id == outlet_id).first()
        if out:
            outlet_name = out.name

    # 2. Conversation Inquiries Analytics
    conv_query = db.query(Conversation).filter(Conversation.environment == target_env)
    if outlet_id:
        conv_query = conv_query.filter(Conversation.outlet_id == outlet_id)
    if cutoff:
        conv_query = conv_query.filter(Conversation.created_at >= cutoff)
    total_convs = conv_query.count()

    # 3. Reservation Requests Analytics
    res_query = db.query(ReservationRequest).filter(ReservationRequest.environment == target_env)
    if outlet_id:
        res_query = res_query.filter(ReservationRequest.outlet_id == outlet_id)
    if cutoff:
        res_query = res_query.filter(ReservationRequest.created_at >= cutoff)

    all_reservations = res_query.all()
    total_res_count = len(all_reservations)

    res_status_breakdown: Dict[str, int] = {}
    pending_res = 0
    accepted_res = 0
    total_covers = 0

    for r in all_reservations:
        status_key = r.status or "NEW"
        res_status_breakdown[status_key] = res_status_breakdown.get(status_key, 0) + 1
        total_covers += (r.guest_count or 0)
        if status_key in ["NEW", "PENDING", "UNDER_REVIEW"]:
            pending_res += 1
        elif status_key == "ACCEPTED":
            accepted_res += 1

    # 4. Lead & Event Inquiries Analytics
    lead_query = db.query(Lead).filter(Lead.environment == target_env)
    if outlet_id:
        lead_query = lead_query.filter(Lead.outlet_id == outlet_id)
    if cutoff:
        lead_query = lead_query.filter(Lead.created_at >= cutoff)

    all_leads = lead_query.all()
    total_leads = len(all_leads)

    lead_status_breakdown: Dict[str, int] = {}
    lead_type_breakdown: Dict[str, int] = {}

    for l in all_leads:
        st = l.status or "NEW"
        lead_status_breakdown[st] = lead_status_breakdown.get(st, 0) + 1
        et = l.enquiry_type or "GENERAL_ENQUIRY"
        lead_type_breakdown[et] = lead_type_breakdown.get(et, 0) + 1

    # 5. Active Knowledge Documents
    doc_query = db.query(KnowledgeDocument).filter(
        KnowledgeDocument.environment == target_env,
        KnowledgeDocument.is_active == True,
    )
    if outlet_id:
        doc_query = doc_query.filter(KnowledgeDocument.outlet_id == outlet_id)
    active_docs = doc_query.count()

    # 6. Frequent Guest Queries (Extracted dynamically from Messages)
    frequent_queries: List[FrequentQueryItem] = []
    msg_query = (
        db.query(Message.content, func.count(Message.id).label("freq"))
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(Conversation.environment == target_env, Message.sender_type == "USER")
    )
    if outlet_id:
        msg_query = msg_query.filter(Conversation.outlet_id == outlet_id)
    if cutoff:
        msg_query = msg_query.filter(Message.created_at >= cutoff)

    top_msgs = msg_query.group_by(Message.content).order_by(func.count(Message.id).desc()).limit(8).all()

    for content, freq in top_msgs:
        # Determine query category
        lower_c = content.lower()
        cat = "GENERAL"
        if any(w in lower_c for w in ["menu", "dish", "food", "truffle", "price", "rate"]):
            cat = "MENU"
        elif any(w in lower_c for w in ["time", "hours", "open", "close", "timing"]):
            cat = "TIMING"
        elif any(w in lower_c for w in ["dress", "attire", "policy", "valet", "park"]):
            cat = "POLICY"
        elif any(w in lower_c for w in ["book", "reserve", "table"]):
            cat = "BOOKING"
        elif any(w in lower_c for w in ["party", "corporate", "event", "wedding", "banquet"]):
            cat = "LEAD"
        elif any(w in lower_c for w in ["jain", "vegan", "veg", "gluten", "diet"]):
            cat = "DIETARY"

        frequent_queries.append(FrequentQueryItem(
            query=content,
            count=freq,
            category=cat,
        ))

    # Fallback to representative curated frequent queries if no user messages recorded yet in current scope
    if not frequent_queries and target_env == "DEMO":
        frequent_queries = [
            FrequentQueryItem(query="Show me the signature chef tasting menu & prices", count=max(1, total_convs // 4), category="MENU"),
            FrequentQueryItem(query="What are dinner operating hours & valet parking policy?", count=max(1, total_convs // 5), category="TIMING"),
            FrequentQueryItem(query="Do you offer strictly Jain or vegan preparations?", count=max(1, total_convs // 6), category="DIETARY"),
            FrequentQueryItem(query="What is the dress code for dinner & weekend lounge?", count=max(1, total_convs // 7), category="POLICY"),
            FrequentQueryItem(query="Table reservation for wedding anniversary with skyline view", count=max(1, total_convs // 8), category="BOOKING"),
        ]

    # 7. Unanswered Questions / Missing Knowledge Gaps
    unanswered_questions: List[UnansweredItem] = []
    # Identify assistant messages that indicated lack of verified information
    unanswered_msgs = (
        db.query(Message.content, Conversation.outlet_id)
        .join(Conversation, Conversation.id == Message.conversation_id)
        .filter(
            Conversation.environment == target_env,
            Message.sender_type == "ASSISTANT",
            Message.content.contains("verified corporate documentation"),
        )
        .limit(5)
        .all()
    )

    outlet_name_lookup = {o.id: o.name for o in db.query(Outlet).all()}

    for content, out_id in unanswered_msgs:
        outlet_str = outlet_name_lookup.get(out_id, "All Outlets")
        unanswered_questions.append(UnansweredItem(
            question="Unindexed guest inquiry awaiting verified documentation",
            frequency=1,
            outlet=outlet_str,
            suggestion="Upload verified corporate policy or menu document",
        ))

    # If empty in demo mode, provide standard operational guidance items
    if not unanswered_questions and target_env == "DEMO":
        unanswered_questions = [
            UnansweredItem(
                question="Do you allow outside birthday cakes and what is the plating fee?",
                frequency=28,
                outlet=outlet_name or "Amber Terrace Rooftop",
                suggestion="Upload Cake & External Food Policy doc",
            ),
            UnansweredItem(
                question="Are pets allowed in the outdoor garden terrace seating?",
                frequency=19,
                outlet=outlet_name or "Saffron & Silk",
                suggestion="Add Pet Policy FAQ",
            ),
            UnansweredItem(
                question="What is the corkage fee for vintage wine bottles brought by guests?",
                frequency=14,
                outlet=outlet_name or "The Velvet Cellar",
                suggestion="Index Sommelier Corkage Guidelines",
            ),
        ]

    return DashboardKPIs(
        total_conversations=total_convs,
        pending_reservations=pending_res,
        total_leads=total_leads,
        active_documents=active_docs,
        active_environment=target_env,
        total_covers=total_covers,
        accepted_reservations=accepted_res,
        reservation_status_breakdown=res_status_breakdown,
        lead_status_breakdown=lead_status_breakdown,
        lead_type_breakdown=lead_type_breakdown,
        date_range=date_range or "7D",
        outlet_id=outlet_id,
        outlet_name=outlet_name,
        frequent_queries=frequent_queries,
        unanswered_questions=unanswered_questions,
    )

@router.get("/export")
def export_analytics_summary_csv(
    date_range: Optional[str] = Query("7D"),
    outlet_id: Optional[int] = Query(None),
    environment: Optional[str] = Query(None),
    current_user: User = Depends(require_roles("SUPER_ADMIN", "ADMIN", "MANAGER", "STAFF")),
    db: Session = Depends(get_db),
):
    """
    Export comprehensive executive analytics report to CSV with live database figures.
    """
    if not isinstance(date_range, str):
        date_range = getattr(date_range, "default", "7D")
    if not isinstance(outlet_id, int):
        outlet_id = getattr(outlet_id, "default", None)
    if not isinstance(environment, str):
        environment = getattr(environment, "default", None)

    target_env = environment if isinstance(environment, str) and environment else get_current_env(db)
    kpis = get_dashboard_kpis(
        date_range=date_range,
        outlet_id=outlet_id,
        environment=target_env,
        current_user=current_user,
        db=db,
    )

    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["AMIT AI CONCIERGE — EXECUTIVE ANALYTICS REPORT"])
    writer.writerow(["Active Environment", kpis.active_environment])
    writer.writerow(["Date Range Filter", kpis.date_range])
    writer.writerow(["Outlet Filter", kpis.outlet_name or "All Outlets"])
    writer.writerow(["Report Generated At (UTC)", datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")])
    writer.writerow([])

    # Core Metrics
    writer.writerow(["KEY PERFORMANCE INDICATORS", "VALUE"])
    writer.writerow(["Total Concierge Conversations", kpis.total_conversations])
    writer.writerow(["Pending Table Reservations", kpis.pending_reservations])
    writer.writerow(["Accepted Table Reservations", kpis.accepted_reservations])
    writer.writerow(["Total Expected Covers", kpis.total_covers])
    writer.writerow(["Total Event & Banquet Leads", kpis.total_leads])
    writer.writerow(["Active Knowledge Documents", kpis.active_documents])
    writer.writerow([])

    # Reservation Status Breakdown
    writer.writerow(["RESERVATION STATUS BREAKDOWN", "COUNT"])
    for status, count in kpis.reservation_status_breakdown.items():
        writer.writerow([status, count])
    writer.writerow([])

    # Lead Pipeline Breakdown
    writer.writerow(["LEAD PIPELINE STAGE", "COUNT"])
    for stage, count in kpis.lead_status_breakdown.items():
        writer.writerow([stage, count])
    writer.writerow([])

    # Lead Type Breakdown
    writer.writerow(["EVENT INQUIRY TYPE", "COUNT"])
    for etype, count in kpis.lead_type_breakdown.items():
        writer.writerow([etype, count])
    writer.writerow([])

    # Top Inquiries
    writer.writerow(["TOP FREQUENT GUEST INQUIRIES"])
    writer.writerow(["Rank", "Category", "Inquiry", "Query Count"])
    for idx, item in enumerate(kpis.frequent_queries, start=1):
        writer.writerow([idx, item.category, item.query, item.count])
    writer.writerow([])

    # Knowledge Gaps
    writer.writerow(["KNOWLEDGE GAPS & UNANSWERED QUESTIONS"])
    writer.writerow(["Question", "Frequency", "Outlet", "Recommended Action"])
    for u in kpis.unanswered_questions:
        writer.writerow([u.question, u.frequency, u.outlet, u.suggestion])

    filename = f"amit_analytics_{kpis.active_environment.lower()}_{kpis.date_range.lower()}.csv"
    return Response(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": f"attachment; filename={filename}"},
    )
