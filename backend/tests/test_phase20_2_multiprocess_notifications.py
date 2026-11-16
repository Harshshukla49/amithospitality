"""
Phase 20.2: Multi-Process Concurrency & Worker Crash Recovery Test.
Spawns independent OS processes to test database-level atomic claiming and crash recovery.
"""

import multiprocessing
import os
import sys
import time
import secrets
from datetime import datetime, timedelta

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app.database import SessionLocal, Base, engine
from app.models.notification import NotificationLog
from app.services.notification_service import notification_service

def worker_claim_task(idemp_key, worker_id, result_queue):
    """Independent process attempting atomic claim."""
    claimed = notification_service.atomic_claim_notification(
        idempotency_key=idemp_key,
        entity_type="RESERVATION",
        entity_id=100 + worker_id,
        reference_id=f"REF-MP-{worker_id}",
        channel="EMAIL",
        recipient=f"worker{worker_id}@example.com",
        event_type="CREATED",
        environment="DEMO",
        outlet_id=1,
    )
    result_queue.put((worker_id, claimed))

def test_multiprocess_atomic_claim():
    print(">>> 1. Testing True Multi-Process Atomic Notification Claiming...")
    idemp_key = f"mp_claim_{secrets.token_hex(4)}"
    queue = multiprocessing.Queue()
    num_processes = 4

    processes = [
        multiprocessing.Process(target=worker_claim_task, args=(idemp_key, i, queue))
        for i in range(num_processes)
    ]

    for p in processes:
        p.start()
    for p in processes:
        p.join()

    results = []
    while not queue.empty():
        results.append(queue.get())

    claimed_winners = [r for r in results if r[1] is True]
    suppressed = [r for r in results if r[1] is False]

    print(f"  [OK] Process results: {len(claimed_winners)} winners, {len(suppressed)} suppressed.")
    assert len(claimed_winners) == 1, f"Exactly 1 process must win claim (got {len(claimed_winners)})"
    assert len(suppressed) == num_processes - 1, f"Remaining processes must be suppressed"

def test_worker_crash_simulation_and_recovery():
    print(">>> 2. Testing Worker Crash Simulation & Stale Claim Recovery...")
    db = SessionLocal()
    crash_key = f"crash_claim_{secrets.token_hex(4)}"
    try:
        # Step A: Worker claims the notification
        claimed = notification_service.atomic_claim_notification(
            idempotency_key=crash_key,
            entity_type="RESERVATION",
            entity_id=888,
            reference_id="REF-CRASH-TEST",
            channel="SMS",
            recipient="+919876543210",
            event_type="CREATED",
            environment="DEMO",
            outlet_id=1,
        )
        assert claimed is True
        
        # Step B: Worker crashes before calling update_claimed_notification!
        # Status remains 'CLAIMED' in database.
        rec = db.query(NotificationLog).filter(NotificationLog.idempotency_key == crash_key).first()
        assert rec.status == "CLAIMED"
        
        # Immediate attempt by another worker within lease window (e.g. 10s) must be refused
        second_attempt = notification_service.atomic_claim_notification(
            idempotency_key=crash_key,
            entity_type="RESERVATION",
            entity_id=888,
            reference_id="REF-CRASH-TEST",
            channel="SMS",
            recipient="+919876543210",
            event_type="CREATED",
            environment="DEMO",
            outlet_id=1,
        )
        assert second_attempt is False, "Active lease window must prevent duplicate claim"

        # Step C: Time passes (>180s) representing dead worker node
        rec.created_at = datetime.utcnow() - timedelta(seconds=250)
        db.commit()

        # Step D: Background supervisor runs recover_stale_claims
        recovered = notification_service.recover_stale_claims(max_age_seconds=180)
        assert recovered >= 1

        db.refresh(rec)
        assert rec.status == "FAILED", "Abandoned worker claim must transition to FAILED for safe retry"
        print(f"  [OK] Stale claim recovered successfully. Status reset to: {rec.status}")

        # Step E: Safe retry by another worker now succeeds
        retry_claimed = notification_service.atomic_claim_notification(
            idempotency_key=crash_key,
            entity_type="RESERVATION",
            entity_id=888,
            reference_id="REF-CRASH-TEST",
            channel="SMS",
            recipient="+919876543210",
            event_type="CREATED",
            environment="DEMO",
            outlet_id=1,
        )
        assert retry_claimed is True, "Recovered notification must be re-claimable by healthy worker"

        # Complete delivery as SIMULATED in DEMO mode
        notification_service.update_claimed_notification(
            idempotency_key=crash_key,
            final_status="SIMULATED",
        )
        db.refresh(rec)
        assert rec.status == "SIMULATED"
        print("  [OK] Re-claimed job safely delivered as SIMULATED without duplication.")
    finally:
        db.close()

if __name__ == "__main__":
    multiprocessing.freeze_support()
    print("=" * 80)
    print("   AMIT AI CONCIERGE — PHASE 20.2 MULTI-PROCESS NOTIFICATION RELIABILITY")
    print("=" * 80)
    test_multiprocess_atomic_claim()
    test_worker_crash_simulation_and_recovery()
    print("=" * 80)
    print("   MULTI-PROCESS & CRASH RECOVERY VERIFICATION PASSED (100%)")
    print("=" * 80)
