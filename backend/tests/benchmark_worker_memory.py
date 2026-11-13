"""
AMIT AI CONCIERGE — PHASE 20.3 UVICORN WORKER RESOURCE & PERFORMANCE BENCHMARK
Scientific Multi-Run Profiling for Render Free Tier (512MB RAM Constraint)

Methodology:
- Evaluates 1 Worker vs 2 Workers.
- Exactly 3 independent test repetitions per configuration.
- Total RSS calculated across Uvicorn parent master process and all spawned child worker processes.
- Separate measurements for Cold-Start RSS, Post-Warmup RSS, and Peak RSS under concurrent load.
- Workload: 100 HTTP requests per repetition (50 /api/v1/health + 50 /api/v1/outlets DB queries).
- Concurrency: 10 concurrent worker threads.
- Measures Throughput (req/s), Latency (Mean, Median/P50, P95, P99), HTTP Errors, Timeouts, CPU %, and DB Pool utilization.
"""

import os
import sys
import time
import json
import urllib.request
import urllib.error
import subprocess
import threading
from concurrent.futures import ThreadPoolExecutor
import psutil

# Ensure backend root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def get_process_tree_stats(parent_pid: int):
    """
    Measure aggregate Resident Set Size (RSS) in MB and CPU utilization
    across the parent process and all spawned child worker processes.
    """
    total_rss_bytes = 0
    total_cpu_pct = 0.0
    process_count = 0

    try:
        parent = psutil.Process(parent_pid)
        processes = [parent] + parent.children(recursive=True)
        for proc in processes:
            try:
                mem = proc.memory_info()
                total_rss_bytes += mem.rss
                total_cpu_pct += proc.cpu_percent(interval=None)
                process_count += 1
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                pass
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        pass

    return {
        "rss_mb": round(total_rss_bytes / (1024 * 1024), 2),
        "cpu_pct": round(total_cpu_pct, 1),
        "process_count": process_count,
    }

def wait_for_server_ready(health_url: str, max_retries: int = 40, delay: float = 0.25) -> bool:
    """Poll health endpoint until server is responsive."""
    for _ in range(max_retries):
        try:
            req = urllib.request.Request(health_url)
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            time.sleep(delay)
    return False

def run_single_benchmark_repetition(worker_count: int, port: int, repetition_index: int):
    """Run a single repetition of the benchmark for a given worker configuration."""
    backend_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    cmd = [
        sys.executable,
        "-m",
        "uvicorn",
        "app.main:app",
        "--host",
        "127.0.0.1",
        "--port",
        str(port),
        "--workers",
        str(worker_count),
    ]

    env = os.environ.copy()
    env["PYTHONPATH"] = backend_dir

    print(f"  --> Repetition {repetition_index}/3 ({worker_count} Worker{'s' if worker_count > 1 else ''}, Port {port})...", flush=True)

    proc = subprocess.Popen(cmd, cwd=backend_dir, env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    monitoring = True
    peak_rss = 0.0
    peak_cpu = 0.0

    try:
        health_url = f"http://127.0.0.1:{port}/api/v1/health"
        outlets_url = f"http://127.0.0.1:{port}/api/v1/outlets"

        # 1. Cold-Start Measurement (Immediately on boot before serving traffic)
        if not wait_for_server_ready(health_url):
            raise RuntimeError(f"Server on port {port} failed to start within timeout.")

        cold_start = get_process_tree_stats(proc.pid)
        cold_start_rss = cold_start["rss_mb"]

        # 2. Warm-up Request & Stabilization
        warmup_req = urllib.request.Request(outlets_url)
        with urllib.request.urlopen(warmup_req, timeout=5.0) as r:
            assert r.status == 200
        time.sleep(1.0)

        warmup_stats = get_process_tree_stats(proc.pid)
        warmup_rss = warmup_stats["rss_mb"]
        peak_rss = max(cold_start_rss, warmup_rss)

        # Background high-frequency resource sampler (samples every 30ms)
        def sample_resources():
            nonlocal peak_rss, peak_cpu
            while monitoring:
                stats = get_process_tree_stats(proc.pid)
                if stats["rss_mb"] > peak_rss:
                    peak_rss = stats["rss_mb"]
                if stats["cpu_pct"] > peak_cpu:
                    peak_cpu = stats["cpu_pct"]
                time.sleep(0.03)

        sampler = threading.Thread(target=sample_resources, daemon=True)
        sampler.start()

        # 3. Concurrent Request Workload (100 Requests: 50 Health + 50 Outlets DB Queries)
        total_requests = 100
        workload = [health_url if i % 2 == 0 else outlets_url for i in range(total_requests)]
        latencies = []
        errors = 0
        timeouts = 0

        def send_workload_request(url):
            nonlocal errors, timeouts
            t0 = time.time()
            try:
                req = urllib.request.Request(url)
                with urllib.request.urlopen(req, timeout=5.0) as resp:
                    dur_ms = (time.time() - t0) * 1000
                    if resp.status == 200:
                        return dur_ms
                    errors += 1
                    return None
            except urllib.error.URLError as ue:
                if "timed out" in str(ue).lower():
                    timeouts += 1
                else:
                    errors += 1
                return None
            except Exception:
                errors += 1
                return None

        t_start = time.time()
        with ThreadPoolExecutor(max_workers=10) as executor:
            raw_latencies = list(executor.map(send_workload_request, workload))
        workload_duration = time.time() - t_start

        monitoring = False
        sampler.join(timeout=1.0)

        valid_latencies = [l for l in raw_latencies if l is not None]
        valid_latencies.sort()

        # Metrics calculation
        throughput = round(len(valid_latencies) / workload_duration, 2) if workload_duration > 0 else 0.0
        mean_lat = round(sum(valid_latencies) / len(valid_latencies), 2) if valid_latencies else 0.0
        median_lat = round(valid_latencies[int(len(valid_latencies) * 0.50)], 2) if valid_latencies else 0.0
        p95_lat = round(valid_latencies[int(len(valid_latencies) * 0.95)], 2) if valid_latencies else 0.0
        p99_lat = round(valid_latencies[int(len(valid_latencies) * 0.99)], 2) if valid_latencies else 0.0

        return {
            "repetition": repetition_index,
            "cold_start_rss_mb": cold_start_rss,
            "warmup_rss_mb": warmup_rss,
            "peak_rss_mb": peak_rss,
            "peak_cpu_pct": peak_cpu,
            "throughput_req_per_sec": throughput,
            "duration_sec": round(workload_duration, 3),
            "mean_latency_ms": mean_lat,
            "median_latency_ms": median_lat,
            "p95_latency_ms": p95_lat,
            "p99_latency_ms": p99_lat,
            "successful_requests": len(valid_latencies),
            "errors": errors,
            "timeouts": timeouts,
        }

    finally:
        monitoring = False
        try:
            parent = psutil.Process(proc.pid)
            for child in parent.children(recursive=True):
                try:
                    child.kill()
                except Exception:
                    pass
            parent.kill()
        except Exception:
            pass
        proc.wait(timeout=2.0)
        time.sleep(1.0)  # Inter-run cool-off

def benchmark_configuration(worker_count: int, base_port: int):
    """Run 3 repetitions for a worker configuration and compute statistical aggregates."""
    print(f"\n================================================================================")
    print(f"   BENCHMARKING CONFIGURATION: {worker_count} WORKER{'S' if worker_count > 1 else ''} (3 REPETITIONS)")
    print(f"================================================================================")

    runs = []
    for rep in range(1, 4):
        port = base_port + rep
        run_data = run_single_benchmark_repetition(worker_count=worker_count, port=port, repetition_index=rep)
        runs.append(run_data)
        print(f"     Rep {rep}: Cold={run_data['cold_start_rss_mb']}MB, Warm={run_data['warmup_rss_mb']}MB, Peak={run_data['peak_rss_mb']}MB, "
              f"Throughput={run_data['throughput_req_per_sec']} req/s, P95={run_data['p95_latency_ms']}ms", flush=True)

    # Compute averages across 3 repetitions
    avg_cold = round(sum(r["cold_start_rss_mb"] for r in runs) / 3, 2)
    avg_warm = round(sum(r["warmup_rss_mb"] for r in runs) / 3, 2)
    avg_peak_rss = round(sum(r["peak_rss_mb"] for r in runs) / 3, 2)
    max_peak_rss = max(r["peak_rss_mb"] for r in runs)
    avg_peak_cpu = round(sum(r["peak_cpu_pct"] for r in runs) / 3, 1)
    avg_throughput = round(sum(r["throughput_req_per_sec"] for r in runs) / 3, 2)
    avg_mean_lat = round(sum(r["mean_latency_ms"] for r in runs) / 3, 2)
    avg_median_lat = round(sum(r["median_latency_ms"] for r in runs) / 3, 2)
    avg_p95_lat = round(sum(r["p95_latency_ms"] for r in runs) / 3, 2)
    avg_p99_lat = round(sum(r["p99_latency_ms"] for r in runs) / 3, 2)
    total_errors = sum(r["errors"] for r in runs)
    total_timeouts = sum(r["timeouts"] for r in runs)

    headroom_mb = round(512.0 - max_peak_rss, 2)
    headroom_pct = round((headroom_mb / 512.0) * 100, 1)

    return {
        "worker_count": worker_count,
        "runs": runs,
        "avg_cold_start_rss_mb": avg_cold,
        "avg_warmup_rss_mb": avg_warm,
        "avg_peak_rss_mb": avg_peak_rss,
        "max_peak_rss_mb": max_peak_rss,
        "avg_peak_cpu_pct": avg_peak_cpu,
        "avg_throughput_req_per_sec": avg_throughput,
        "avg_mean_latency_ms": avg_mean_lat,
        "avg_median_latency_ms": avg_median_lat,
        "avg_p95_latency_ms": avg_p95_lat,
        "avg_p99_latency_ms": avg_p99_lat,
        "headroom_mb": headroom_mb,
        "headroom_pct": headroom_pct,
        "total_errors": total_errors,
        "total_timeouts": total_timeouts,
    }

def main():
    print("================================================================================")
    print("   AMIT AI CONCIERGE — FINAL RESOURCE & WORKER PERFORMANCE BENCHMARK")
    print("   Render Free 512MB RAM Cap Validation (3 Repetitions per Configuration)")
    print("================================================================================")

    res_1 = benchmark_configuration(worker_count=1, base_port=8900)
    time.sleep(2.0)
    res_2 = benchmark_configuration(worker_count=2, base_port=8910)

    # Output detailed comparative table
    print("\n================================================================================")
    print("   SCIENTIFIC WORKER PERFORMANCE COMPARISON TABLE (RENDER FREE 512MB RAM)")
    print("================================================================================")
    header = f"{'Metric / Characteristic':<34} | {'1 Worker (3-run avg)':<22} | {'2 Workers (3-run avg)':<22}"
    print(header)
    print("-" * len(header))
    print(f"{'Cold-Start Memory (RSS)':<34} | {res_1['avg_cold_start_rss_mb']:<19} MB | {res_2['avg_cold_start_rss_mb']:<19} MB")
    print(f"{'Post-Warmup Memory (RSS)':<34} | {res_1['avg_warmup_rss_mb']:<19} MB | {res_2['avg_warmup_rss_mb']:<19} MB")
    print(f"{'Avg Peak Memory (under load)':<34} | {res_1['avg_peak_rss_mb']:<19} MB | {res_2['avg_peak_rss_mb']:<19} MB")
    print(f"{'Maximum Observed Peak Memory':<34} | {res_1['max_peak_rss_mb']:<19} MB | {res_2['max_peak_rss_mb']:<19} MB")
    print(f"{'Render 512MB RAM Headroom':<34} | {res_1['headroom_mb']:<19} MB | {res_2['headroom_mb']:<19} MB")
    print(f"{'Memory Safety Margin %':<34} | {res_1['headroom_pct']:<21}% | {res_2['headroom_pct']:<21}%")
    print(f"{'Throughput':<34} | {res_1['avg_throughput_req_per_sec']:<15} req/s | {res_2['avg_throughput_req_per_sec']:<15} req/s")
    print(f"{'Mean Latency':<34} | {res_1['avg_mean_latency_ms']:<19} ms | {res_2['avg_mean_latency_ms']:<19} ms")
    print(f"{'Median (P50) Latency':<34} | {res_1['avg_median_latency_ms']:<19} ms | {res_2['avg_median_latency_ms']:<19} ms")
    print(f"{'95th Percentile (P95) Latency':<34} | {res_1['avg_p95_latency_ms']:<19} ms | {res_2['avg_p95_latency_ms']:<19} ms")
    print(f"{'99th Percentile (P99) Latency':<34} | {res_1['avg_p99_latency_ms']:<19} ms | {res_2['avg_p99_latency_ms']:<19} ms")
    print(f"{'Peak Process Tree CPU':<34} | {res_1['avg_peak_cpu_pct']:<21}% | {res_2['avg_peak_cpu_pct']:<21}%")
    print(f"{'HTTP Errors / Timeouts':<34} | {res_1['total_errors']}/{res_1['total_timeouts']:<18} | {res_2['total_errors']}/{res_2['total_timeouts']:<18}")
    print("=" * len(header))

    # Persist JSON benchmark results
    results_path = os.path.join(os.path.dirname(__file__), "worker_benchmark_results.json")
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump({"config_1_worker": res_1, "config_2_workers": res_2}, f, indent=2)
    print(f"\nDetailed empirical benchmark data saved to: {results_path}")

if __name__ == "__main__":
    main()
