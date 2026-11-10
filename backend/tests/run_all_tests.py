import os
import sys
import time
import subprocess

if sys.stdout and hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')
if sys.stderr and hasattr(sys.stderr, 'reconfigure'):
    sys.stderr.reconfigure(encoding='utf-8')

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

TEST_SUITES = [
    ("Phase 2 — Direct Auth & Database Verification", "test_direct.py"),
    ("Phase 3 — Knowledge Base Management & Document Pipeline", "test_phase3_knowledge.py"),
    ("Phase 4 — AI Chatbot, Intent Detection & Grounded RAG", "test_phase4_rag.py"),
    ("Phase 5 — Reservation & Lead Management Workflows", "test_phase5_workflows.py"),
    ("Phase 5 — Comprehensive Reservation & Lead Pipeline", "test_phase5_comprehensive.py"),
    ("Phase 6 — Analytics, BI Reporting & Audit Trail Compliance", "test_phase6_analytics.py"),
    ("Phase 7 — Multi-Outlet & Multilingual Concierge", "test_phase7_multilingual.py"),
    ("Phase 8 — Security Hardening, Prompt Injection & Rate Limiting", "test_phase8_security.py"),
    ("Phase 9 — Production Infrastructure & Database Migration", "test_phase9_postgres_migration.py"),
    ("Phase 10 — Real AI, WhatsApp, Voice, Email & Enterprise Integrations", "test_phase10_integrations.py"),
    ("Phase 11 — Enterprise QA, Security Validation & Reliability", "test_phase11_enterprise_qa.py"),
    ("Phase 12 — Cloud Deployment, Infrastructure & Production Smoke", "test_phase12_deployment_smoke.py"),
    ("Phase 14 — Real HTTP Integration, RBAC, Multi-Outlet Isolation & Streaming CSV", "test_phase14_http_integration.py"),
    ("Phase 15 — Database Reliability, Atomic Transactions & 20-Worker Concurrency", "test_phase15_concurrency.py"),
    ("Phase 17 — External Enterprise Integrations (Gemini, WhatsApp, Twilio, SendGrid, Redis, Sentry)", "test_phase17_external_integrations.py"),
    ("Phase 19 — Live Outlets API, Multi-Outlet RBAC & Reservation Notification System", "test_phase19_notifications_outlets.py"),
    ("Phase 20 — Unified Guest CRM & Secure Self-Service Experience", "test_phase20_guest_crm_self_service.py"),
    ("Phase 20.1 — Security, Data Integrity & Reliability Audit", "test_phase20_1_security_audit.py"),
]

def run_master_regression_suite():
    print("=" * 80, flush=True)
    print("   AMIT AI CONCIERGE — MASTER END-TO-END REGRESSION VERIFICATION", flush=True)
    print("   Enterprise Hospitality Platform for Amit Hospitality", flush=True)
    print("=" * 80, flush=True)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}", flush=True)
    print(f"Python Executable: {sys.executable}\n", flush=True)

    results = []
    total_start = time.time()

    tests_dir = os.path.dirname(__file__)

    for title, script_name in TEST_SUITES:
        script_path = os.path.join(tests_dir, script_name)
        print(f"\n>>> Running: {title} ({script_name})", flush=True)
        start_t = time.time()
        
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            cwd=os.path.abspath(os.path.join(tests_dir, "..")),
        )
        duration = time.time() - start_t

        if proc.returncode == 0:
            print(f"    STATUS: PASSED ({duration:.2f}s)", flush=True)
            results.append((title, True, duration, proc.stdout))
        else:
            print(f"    STATUS: FAILED ({duration:.2f}s)", flush=True)
            print("\n    --- ERROR LOG ---", flush=True)
            if proc.stderr:
                print("STDERR:\n" + proc.stderr, flush=True)
            if proc.stdout:
                print("STDOUT:\n" + proc.stdout, flush=True)
            print("    -----------------\n", flush=True)
            results.append((title, False, duration, proc.stderr or proc.stdout))

    total_duration = time.time() - total_start
    all_passed = all(r[1] for r in results)

    print("\n" + "=" * 80)
    print("   MASTER REGRESSION TEST RESULTS SUMMARY")
    print("=" * 80)
    for title, passed, dur, _ in results:
        status_str = "[PASS]" if passed else "[FAIL]"
        print(f"  {status_str:7s} | {dur:5.2f}s | {title}")
    print("-" * 80)
    print(f"  TOTAL DURATION: {total_duration:.2f}s")
    print(f"  OVERALL RESULT: {'ALL TEST SUITES PASSED (100%)' if all_passed else 'SOME TESTS FAILED'}")
    print("=" * 80 + "\n")

    if not all_passed:
        sys.exit(1)

if __name__ == "__main__":
    run_master_regression_suite()
