#!/usr/bin/env python3
"""
ERP03 v1.0.0 — Production Bootstrap Orchestrator (Final)
Pure stdlib. Zero placeholders. Cross-platform. Safe rollback.

Usage:
    python scripts/bootstrap.py [--force] [--reset-env] [--repair-packages]
"""
from __future__ import annotations

import json
import os
import platform
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
RUNNING_LOCK = REPO_ROOT / ".bootstrap.running.lock"
COMPLETED_MARKER = REPO_ROOT / ".bootstrap.completed"
LOG_DIR = REPO_ROOT / "logs"

REQUIRED_ARTIFACTS = [
    ".env.example",
    "docker-compose.yml",
    "Makefile",
    "apps/erp/core/modules/accounting/__init__.py",
    "apps/erp/engine/commands/__init__.py",
    "apps/erp/framework/config/settings.py",
    "infrastructure/postgres/init.sql",
]

INFRA_SERVICES = ["postgres", "redis", "rabbitmq"]
EXPECTED_SCHEMAS = (
    "accounting", "sales", "inventory", "hr",
    "crm", "warehouse", "logistics", "reporting",
)


class BootstrapError(Exception):
    """Irrecoverable bootstrap failure."""


# ---------------------------------------------------------------------------
# Cross-platform execution lock
# ---------------------------------------------------------------------------
class ExecutionLock:
    def __init__(self, path: Path) -> None:
        self._path = path
        self._fh = None
        self._is_windows = platform.system() == "Windows"

    def acquire(self) -> bool:
        try:
            self._fh = open(self._path, "w", encoding="utf-8")  # noqa: SIM115
            if self._is_windows:
                import msvcrt
                msvcrt.locking(self._fh.fileno(), msvcrt.LK_NBLCK, 1)
            else:
                import fcntl
                fcntl.flock(self._fh.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
            self._fh.write(f"{os.getpid()}\n{datetime.now(timezone.utc).isoformat()}\n")
            self._fh.flush()
            return True
        except (OSError, IOError):
            if self._fh is not None:
                self._fh.close()
                self._fh = None
            return False

    def release(self) -> None:
        if self._fh is not None:
            try:
                if self._is_windows:
                    import msvcrt
                    msvcrt.locking(self._fh.fileno(), msvcrt.LK_UNLCK, 1)
                else:
                    import fcntl
                    fcntl.flock(self._fh.fileno(), fcntl.LOCK_UN)
            except (OSError, IOError):
                pass
            self._fh.close()
            self._fh = None
            try:
                self._path.unlink(missing_ok=True)
            except OSError:
                pass


# ---------------------------------------------------------------------------
# Logger
# ---------------------------------------------------------------------------
class Logger:
    def __init__(self, log_file: Path) -> None:
        self._fh = open(log_file, "a", encoding="utf-8")  # noqa: SIM115

    def _ts(self) -> str:
        return datetime.now().strftime("%H:%M:%S")

    def info(self, msg: str) -> None:
        line = f"[{self._ts()}] {msg}"
        print(line, flush=True)
        self._fh.write(line + "\n")
        self._fh.flush()

    def warn(self, msg: str) -> None:
        line = f"[{self._ts()}] WARN: {msg}"
        print(line, flush=True)
        self._fh.write(line + "\n")
        self._fh.flush()

    def fatal(self, msg: str) -> None:
        line = f"[{self._ts()}] FATAL: {msg}"
        print(line, file=sys.stderr, flush=True)
        self._fh.write(line + "\n")
        self._fh.flush()

    def close(self) -> None:
        self._fh.close()


# ---------------------------------------------------------------------------
# Command execution with full diagnostics
# ---------------------------------------------------------------------------
def run_cmd(
    cmd: list[str],
    cwd: Path | None = None,
    capture: bool = True,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        cmd, cwd=cwd or REPO_ROOT, text=True,
        capture_output=capture, check=False,
    )
    if result.returncode != 0:
        stderr_tail = (result.stderr or "").strip()[-2000:]
        stdout_tail = (result.stdout or "").strip()[-1000:]
        detail = f"exit={result.returncode}"
        if stderr_tail:
            detail += f"\nSTDERR:\n{stderr_tail}"
        elif stdout_tail:
            detail += f"\nSTDOUT:\n{stdout_tail}"
        raise BootstrapError(f"Command failed: {' '.join(cmd)}\n{detail}")
    return result


def http_get(url: str, timeout: int = 5) -> tuple[int, str]:
    try:
        req = urllib.request.Request(url, method="GET")
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.status, resp.read().decode("utf-8", errors="replace")
    except urllib.error.HTTPError as exc:
        body = ""
        try:
            body = exc.read().decode("utf-8", errors="replace")
        except Exception:
            pass
        return exc.code, body
    except (urllib.error.URLError, OSError):
        return 0, ""


# ---------------------------------------------------------------------------
# Authoritative config resolution via docker compose config
# ---------------------------------------------------------------------------
def resolve_compose_config(compose_cmd: list[str]) -> dict:
    result = run_cmd(compose_cmd + ["config", "--format", "json"])
    return json.loads(result.stdout)


def get_service_port(compose_config: dict, service_name: str, default: int) -> int:
    svc = compose_config.get("services", {}).get(service_name, {})
    ports = svc.get("ports", [])
    for port_def in ports:
        if isinstance(port_def, dict):
            published = port_def.get("published")
            if published is not None:
                return int(published)
        elif isinstance(port_def, str) and ":" in port_def:
            host_part = port_def.split(":")[0]
            try:
                return int(host_part)
            except ValueError:
                continue
    return default


def get_db_credentials_from_compose(compose_config: dict) -> dict[str, str]:
    pg_env = compose_config.get("services", {}).get("postgres", {}).get("environment", {})
    return {
        "user": pg_env.get("POSTGRES_USER", "erp"),
        "db": pg_env.get("POSTGRES_DB", "erp_core"),
    }


def build_endpoints(compose_config: dict) -> dict[str, dict]:
    erp_port = get_service_port(compose_config, "erp-backend", 8000)
    ai_port = get_service_port(compose_config, "ai-platform", 8001)
    admin_port = get_service_port(compose_config, "frontend-admin", 3000)
    client_port = get_service_port(compose_config, "frontend-client", 3001)

    return {
        "erp-backend": {
            "url": f"http://localhost:{erp_port}/healthz",
            "expect_status": 200,
            "expect_json_keys": ("status", "db", "redis", "rabbitmq"),
        },
        "ai-platform": {
            "url": f"http://localhost:{ai_port}/healthz",
            "expect_status": 200,
            "expect_json_keys": ("status",),
        },
        "frontend-admin": {
            "url": f"http://localhost:{admin_port}",
            "expect_status": 200,
            "expect_json_keys": None,
        },
        "frontend-client": {
            "url": f"http://localhost:{client_port}",
            "expect_status": 200,
            "expect_json_keys": None,
        },
    }


# ---------------------------------------------------------------------------
# Pre-existing service tracking for safe rollback
# ---------------------------------------------------------------------------
def get_running_services(compose_cmd: list[str]) -> set[str]:
    result = subprocess.run(
        compose_cmd + ["ps", "--format", "json"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0 or not result.stdout.strip():
        return set()
    try:
        data = json.loads(result.stdout)
        if isinstance(data, list):
            return {
                s.get("Name", s.get("name", ""))
                for s in data
                if s.get("State", s.get("state", "")) in ("running", "healthy")
            }
        return set()
    except (json.JSONDecodeError, TypeError):
        return set()


def safe_rollback(compose_cmd: list[str], pre_existing: set[str], log: Logger) -> None:
    current = get_running_services(compose_cmd)
    to_stop = current - pre_existing
    if not to_stop:
        log.info("No services to roll back (all were pre-existing).")
        return
    log.info(f"Rolling back services started by this run: {', '.join(sorted(to_stop))}")
    subprocess.run(
        compose_cmd + ["stop"] + sorted(to_stop),
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    subprocess.run(
        compose_cmd + ["rm", "-sf"] + sorted(to_stop),
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )


# ---------------------------------------------------------------------------
# Step functions
# ---------------------------------------------------------------------------
def validate_artifacts(log: Logger) -> None:
    log.info("Validating required repository artifacts...")
    missing = [f for f in REQUIRED_ARTIFACTS if not (REPO_ROOT / f).is_file()]
    if missing:
        raise BootstrapError("Required artifacts missing:\n  " + "\n  ".join(missing))
    log.info(f"All {len(REQUIRED_ARTIFACTS)} required artifacts present.")


def resolve_env(log: Logger, reset_env: bool) -> None:
    env_file = REPO_ROOT / ".env"
    env_example = REPO_ROOT / ".env.example"

    if not env_file.is_file():
        shutil.copy2(env_example, env_file)
        log.info(".env materialized from .env.example")
    elif reset_env:
        backup = REPO_ROOT / f".env.backup.{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        shutil.copy2(env_file, backup)
        log.warn(f".env backed up to {backup.name}")
        shutil.copy2(env_example, env_file)
        log.warn(".env OVERWRITTEN from .env.example (--reset-env)")
    else:
        log.info(".env exists, preserving existing configuration")


def validate_packages(log: Logger, repair: bool) -> None:
    log.info("Verifying Python package structure...")
    apps_dir = REPO_ROOT / "apps"
    if not apps_dir.is_dir():
        log.info("No apps/ directory found. Skipping.")
        return

    broken: list[Path] = []
    for py_file in apps_dir.rglob("*.py"):
        parts_str = str(py_file)
        if "__pycache__" in parts_str or "node_modules" in parts_str:
            continue
        current = py_file.parent
        while current != REPO_ROOT and current != apps_dir.parent:
            init_path = current / "__init__.py"
            has_py_siblings = any(p.suffix == ".py" for p in current.iterdir() if p.is_file())
            if has_py_siblings and not init_path.is_file():
                broken.append(current)
            current = current.parent

    unique_broken = sorted(set(broken))
    if unique_broken:
        if repair:
            log.info(f"Repairing {len(unique_broken)} missing __init__.py files...")
            for d in unique_broken:
                (d / "__init__.py").touch()
                log.info(f"  Created: {d.relative_to(REPO_ROOT)}/__init__.py")
        else:
            paths = "\n  ".join(str(d.relative_to(REPO_ROOT)) for d in unique_broken)
            raise BootstrapError(
                f"Missing __init__.py in {len(unique_broken)} directories:\n  {paths}\n"
                "Re-run with --repair-packages to fix."
            )
    else:
        log.info("Package structure intact.")


def detect_compose_cmd() -> list[str]:
    for cmd in [["docker", "compose"], ["docker-compose"]]:
        r = subprocess.run(cmd + ["version"], capture_output=True, text=True, check=False)
        if r.returncode == 0:
            return cmd
    raise BootstrapError("Neither 'docker compose' nor 'docker-compose' available.")


def build_images(log: Logger, compose_cmd: list[str]) -> None:
    log.info("Building container images...")
    run_cmd(compose_cmd + ["build", "--parallel"])
    log.info("Images built.")


def start_infrastructure(log: Logger, compose_cmd: list[str]) -> None:
    log.info(f"Starting infrastructure: {', '.join(INFRA_SERVICES)}...")
    run_cmd(compose_cmd + ["up", "-d"] + INFRA_SERVICES)


def wait_for_infrastructure(log: Logger, compose_cmd: list[str], max_wait: int = 90) -> None:
    log.info(f"Waiting for infrastructure readiness (max {max_wait}s)...")
    elapsed = 0

    while elapsed < max_wait:
        all_ready = True
        statuses: list[str] = []

        pg_r = subprocess.run(
            compose_cmd + ["exec", "-T", "postgres", "pg_isready", "-U", "erp"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        pg_ok = pg_r.returncode == 0
        statuses.append(f"pg={'✅' if pg_ok else '❌'}")
        if not pg_ok:
            all_ready = False

        redis_r = subprocess.run(
            compose_cmd + ["exec", "-T", "redis", "redis-cli", "ping"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        redis_ok = redis_r.returncode == 0 and "PONG" in (redis_r.stdout or "")
        statuses.append(f"redis={'✅' if redis_ok else '❌'}")
        if not redis_ok:
            all_ready = False

        rmq_r = subprocess.run(
            compose_cmd + ["exec", "-T", "rabbitmq",
                           "rabbitmq-diagnostics", "check_running", "--quiet"],
            cwd=REPO_ROOT, capture_output=True, text=True, check=False,
        )
        rmq_ok = rmq_r.returncode == 0
        statuses.append(f"rmq={'✅' if rmq_ok else '❌'}")
        if not rmq_ok:
            all_ready = False

        if all_ready:
            log.info(f"Infrastructure ready within {elapsed}s.")
            return

        time.sleep(3)
        elapsed += 3
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\r[{ts}] Infra... ({elapsed}s/{max_wait}s) {' '.join(statuses)}", end="", flush=True)

    print()
    raise BootstrapError(
        f"Infrastructure not ready within {max_wait}s. Run: docker compose logs postgres redis rabbitmq"
    )


def apply_migrations(log: Logger, compose_cmd: list[str]) -> None:
    alembic_ini = REPO_ROOT / "apps" / "erp" / "alembic.ini"
    if not alembic_ini.is_file():
        log.info("No alembic.ini found. Migration deferred.")
        return

    log.info("Applying database migrations (via docker compose run --rm)...")
    run_cmd(compose_cmd + [
        "run", "--rm", "--no-deps", "erp-backend",
        "python", "-m", "alembic", "-c", "apps/erp/alembic.ini", "upgrade", "head",
    ])
    log.info("Migrations applied.")


def start_application_services(log: Logger, compose_cmd: list[str]) -> None:
    log.info("Starting application services...")
    run_cmd(compose_cmd + ["up", "-d"])
    log.info("All services started.")


def wait_for_app_readiness(log: Logger, endpoints: dict[str, dict], max_wait: int = 120) -> None:
    log.info(f"Waiting for application readiness (max {max_wait}s)...")
    elapsed = 0

    while elapsed < max_wait:
        all_ready = True
        statuses: list[str] = []

        for svc, spec in endpoints.items():
            status, body = http_get(spec["url"])
            ok = status == spec["expect_status"]

            if ok and spec["expect_json_keys"]:
                try:
                    data = json.loads(body)
                    ok = all(k in data for k in spec["expect_json_keys"])
                except (json.JSONDecodeError, TypeError):
                    ok = False

            statuses.append(f"{svc}={'✅' if ok else '❌'}({status})")
            if not ok:
                all_ready = False

        if all_ready:
            log.info(f"All applications ready within {elapsed}s.")
            return

        time.sleep(3)
        elapsed += 3
        ts = datetime.now().strftime("%H:%M:%S")
        print(f"\r[{ts}] Apps... ({elapsed}s/{max_wait}s) {' '.join(statuses)}", end="", flush=True)

    print()
    raise BootstrapError(f"Applications not ready within {max_wait}s. Run: docker compose logs")


def load_seed_data(log: Logger, compose_cmd: list[str]) -> None:
    log.info("Checking for seed data loader...")

    probe = subprocess.run(
        compose_cmd + ["run", "--rm", "--no-deps", "erp-backend", "python", "-c",
                        "from apps.erp.engine.commands.seed import seed_database"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if probe.returncode != 0:
        stderr = (probe.stderr or "").strip()
        if "ModuleNotFoundError: No module named 'apps.erp.engine.commands.seed'" in stderr:
            log.info("Seed module not implemented. Deferring.")
            return
        elif "ImportError" in stderr and "seed" in stderr.lower():
            raise BootstrapError(f"Seed module exists but import failed:\n{stderr}")
        else:
            raise BootstrapError(f"Seed probe failed unexpectedly:\n{stderr}")

    log.info("Loading seed data...")
    run_cmd(compose_cmd + [
        "run", "--rm", "--no-deps", "erp-backend", "python", "-c",
        "from apps.erp.engine.commands.seed import seed_database; seed_database()",
    ])
    log.info("Seed data loaded.")


def verify_full_integrity(
    log: Logger,
    compose_cmd: list[str],
    compose_config: dict,
    endpoints: dict[str, dict],
    is_fresh_install: bool,
) -> None:
    log.info("Running full integrity verification...")
    db_creds = get_db_credentials_from_compose(compose_config)

    status, body = http_get(endpoints["erp-backend"]["url"])
    if status != 200:
        raise BootstrapError(f"ERP /healthz HTTP {status}")
    health = json.loads(body)
    if health.get("status") != "ok":
        raise BootstrapError(f"ERP health: {health.get('status')}")
    for dep in ("db", "redis", "rabbitmq"):
        if health.get(dep) != "connected":
            raise BootstrapError(f"ERP dep {dep}: {health.get(dep)}")
    log.info("  ✅ ERP backend")

    ai_status, ai_body = http_get(endpoints["ai-platform"]["url"])
    if ai_status != 200:
        raise BootstrapError(f"AI /healthz HTTP {ai_status}")
    ai_health = json.loads(ai_body)
    if ai_health.get("status") != "ok":
        raise BootstrapError(f"AI health: {ai_health.get('status')}")
    log.info("  ✅ AI platform")

    schema_list = ",".join(f"'{s}'" for s in EXPECTED_SCHEMAS)
    result = subprocess.run(
        compose_cmd + ["exec", "-T", "postgres", "psql",
                       "-U", db_creds["user"], "-d", db_creds["db"], "-tAc",
                       f"SELECT COUNT(*) FROM information_schema.schemata WHERE schema_name IN ({schema_list});"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if result.returncode != 0:
        raise BootstrapError(f"Schema query failed: {result.stderr.strip()}")

    count = int(result.stdout.strip())
    expected = len(EXPECTED_SCHEMAS)
    if count < expected:
        if is_fresh_install:
            raise BootstrapError(
                f"Fresh install requires {expected} schemas, found {count}. "
                "Check infrastructure/postgres/init.sql and migration state."
            )
        else:
            log.warn(f"Pre-existing volume: {count}/{expected} schemas found (may require manual migration)")
    else:
        log.info(f"  ✅ Database schemas ({count}/{expected})")

    fe_status, fe_body = http_get(endpoints["frontend-admin"]["url"])
    if fe_status != 200:
        raise BootstrapError(f"Frontend admin HTTP {fe_status}")
    lower = fe_body.lower()
    if any(m in lower for m in ("502 bad gateway", "503 service unavailable")):
        raise BootstrapError("Frontend admin returning proxy error")
    log.info("  ✅ Frontend admin")

    cl_status, _ = http_get(endpoints["frontend-client"]["url"])
    if cl_status != 200:
        raise BootstrapError(f"Frontend client HTTP {cl_status}")
    log.info("  ✅ Frontend client")

    redis_r = subprocess.run(
        compose_cmd + ["exec", "-T", "redis", "redis-cli", "ping"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if redis_r.returncode != 0 or "PONG" not in (redis_r.stdout or ""):
        raise BootstrapError("Direct Redis PING failed")
    log.info("  ✅ Redis (direct)")

    rmq_r = subprocess.run(
        compose_cmd + ["exec", "-T", "rabbitmq",
                       "rabbitmq-diagnostics", "check_running", "--quiet"],
        cwd=REPO_ROOT, capture_output=True, text=True, check=False,
    )
    if rmq_r.returncode != 0:
        raise BootstrapError("Direct RabbitMQ diagnostics failed")
    log.info("  ✅ RabbitMQ (direct)")


# ---------------------------------------------------------------------------
# Main orchestrator
# ---------------------------------------------------------------------------
def main() -> int:
    force = "--force" in sys.argv
    reset_env = "--reset-env" in sys.argv
    repair_packages = "--repair-packages" in sys.argv

    LOG_DIR.mkdir(parents=True, exist_ok=True)
    log_file = LOG_DIR / f"bootstrap-{datetime.now().strftime('%Y%m%d-%H%M%S')}.log"
    log = Logger(log_file)

    lock = ExecutionLock(RUNNING_LOCK)
    pre_existing_services: set[str] = set()
    started_this_run = False

    try:
        if COMPLETED_MARKER.is_file() and not force:
            completed_at = COMPLETED_MARKER.read_text(encoding="utf-8").strip()
            log.info(f"Bootstrap already completed at {completed_at}. Use --force to re-run.")
            return 0

        if not lock.acquire():
            log.fatal("Another bootstrap instance is running. Exiting.")
            return 1

        compose_cmd = detect_compose_cmd()
        log.info(f"Compose: {' '.join(compose_cmd)}")

        pre_existing_services = get_running_services(compose_cmd)
        if pre_existing_services:
            log.info(f"Pre-existing running services: {', '.join(sorted(pre_existing_services))}")

        is_fresh_install = not COMPLETED_MARKER.is_file()

        validate_artifacts(log)
        resolve_env(log, reset_env)

        log.info("Validating environment via docker compose config...")
        compose_config = resolve_compose_config(compose_cmd)
        log.info("Environment validated by Compose.")

        validate_packages(log, repair_packages)
        build_images(log, compose_cmd)

        start_infrastructure(log, compose_cmd)
        started_this_run = True

        wait_for_infrastructure(log, compose_cmd)
        apply_migrations(log, compose_cmd)
        start_application_services(log, compose_cmd)

        endpoints = build_endpoints(compose_config)
        wait_for_app_readiness(log, endpoints)
        load_seed_data(log, compose_cmd)
        verify_full_integrity(log, compose_cmd, compose_config, endpoints, is_fresh_install)

        COMPLETED_MARKER.write_text(datetime.now(timezone.utc).isoformat(), encoding="utf-8")

        log.info("=============================================")
        log.info("  ERP03 BOOTSTRAP COMPLETE")
        log.info(f"  Log: {log_file.relative_to(REPO_ROOT)}")
        erp_port = get_service_port(compose_config, "erp-backend", 8000)
        admin_port = get_service_port(compose_config, "frontend-admin", 3000)
        client_port = get_service_port(compose_config, "frontend-client", 3001)
        log.info(f"  ERP API:     http://localhost:{erp_port}")
        log.info(f"  API Docs:    http://localhost:{erp_port}/docs")
        log.info(f"  Admin UI:    http://localhost:{admin_port}")
        log.info(f"  Client UI:   http://localhost:{client_port}")
        log.info("=============================================")
        return 0

    except BootstrapError as exc:
        log.fatal(str(exc))
        if started_this_run:
            safe_rollback(compose_cmd, pre_existing_services, log)
        else:
            log.info("No services were started by this run. Skipping rollback.")
        return 1

    except KeyboardInterrupt:
        log.fatal("Interrupted by user.")
        if started_this_run:
            safe_rollback(compose_cmd, pre_existing_services, log)
        return 130

    finally:
        lock.release()
        log.close()


if __name__ == "__main__":
    sys.exit(main())
