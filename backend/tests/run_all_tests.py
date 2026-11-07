import os
import sys
import time
import subprocess

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

TEST_SUITES = [
    ("Phase 2 — Direct Auth & Database Verification", "test_direct.py"),
    ("Phase 3 — Knowledge Base Management & Document Pipeline", "test_phase3_knowledge.py"),
    ("Phase 4 — AI Chatbot, Intent Detection & Grounded RAG", "test_phase4_rag.py"),
    ("Phase 5 — Reservation & Lead Management Workflows", "test_phase5_workflows.py"),
    ("Phase 6 — Analytics, BI Reporting & Audit Trail Compliance", "test_phase6_analytics.py"),
    ("Phase 7 — Multi-Outlet & Multilingual Concierge", "test_phase7_multilingual.py"),
    ("Phase 8 — Security Hardening, Prompt Injection & Rate Limiting", "test_phase8_security.py"),
]

def run_master_regression_suite():
    print("=" * 80)
    print("   AMIT AI CONCIERGE — MASTER END-TO-END REGRESSION VERIFICATION")
    print("   Enterprise Hospitality Platform for Amit Hospitality")
    print("=" * 80)
    print(f"Timestamp: {time.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Python Executable: {sys.executable}\n")

    results = []
    total_start = time.time()

    tests_dir = os.path.dirname(__file__)

    for title, script_name in TEST_SUITES:
        script_path = os.path.join(tests_dir, script_name)
        print(f"\n>>> Running: {title} ({script_name})")
        start_t = time.time()
        
        proc = subprocess.run(
            [sys.executable, script_path],
            capture_output=True,
            text=True,
            cwd=os.path.abspath(os.path.join(tests_dir, "..")),
        )
        duration = time.time() - start_t

        if proc.returncode == 0:
            print(f"    STATUS: PASSED ({duration:.2f}s)")
            results.append((title, True, duration, proc.stdout))
        else:
            print(f"    STATUS: FAILED ({duration:.2f}s)")
            print("\n    --- ERROR LOG ---")
            print(proc.stderr or proc.stdout)
            print("    -----------------\n")
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
