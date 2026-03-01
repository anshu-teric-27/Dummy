import argparse
import json
import sys
from datetime import date
from pathlib import Path
from typing import Set, Tuple, Dict, Any, Iterable

from fastapi import FastAPI


# ==============================
# Application Loader
# ==============================

def load_fastapi_application() -> FastAPI:
    """
    Imports and returns the FastAPI app instance.
    This requires the project to be a proper Python package.
    """
    # Make `python_demo_api` importable so `import app.*` works regardless of CWD.
    script_path = Path(__file__).resolve()
    python_demo_api_dir = script_path.parents[2]
    if str(python_demo_api_dir) not in sys.path:
        sys.path.insert(0, str(python_demo_api_dir))

    from app.main import app  # type: ignore
    return app


# ==============================
# Route Extraction
# ==============================

def extract_registered_routes(application: FastAPI) -> Set[Tuple[str, str]]:
    """
    Extracts (HTTP_METHOD, PATH) tuples from FastAPI.
    """
    allowed_methods = {"GET", "POST", "PUT", "DELETE", "PATCH"}
    discovered_routes: Set[Tuple[str, str]] = set()

    for route in application.routes:
        if hasattr(route, "methods") and hasattr(route, "path"):
            for method in route.methods:
                if method in allowed_methods:
                    discovered_routes.add((method, route.path))

    return discovered_routes


# ==============================
# Roam Contract Loader (formatted JSON)
# ==============================

def iter_documented_endpoints(formatted_roam_json: dict) -> Iterable[dict]:
    for ep in formatted_roam_json.get("endpoints", []) or []:
        if isinstance(ep, dict):
            yield ep


def load_roam_formatted(formatted_path: Path) -> dict:
    return json.loads(formatted_path.read_text())


def load_documented_routes(formatted_roam_json: dict) -> Set[Tuple[str, str]]:
    """
    Reads documented routes from formatted Roam JSON.
    """
    documented_routes: Set[Tuple[str, str]] = set()

    for endpoint in iter_documented_endpoints(formatted_roam_json):
        method = (endpoint.get("method") or "").upper().strip()
        path = (endpoint.get("path") or "").strip()
        if method and path:
            documented_routes.add((method, path))

    return documented_routes


# ==============================
# Comparison Engine
# ==============================

def generate_comparison_report(
    implemented_routes: Set[Tuple[str, str]],
    documented_routes: Set[Tuple[str, str]],
) -> Dict[str, Any]:
    """
    Generates structured comparison report.
    """

    matching_routes = implemented_routes & documented_routes
    undocumented_routes = implemented_routes - documented_routes
    missing_implementations = documented_routes - implemented_routes

    total_documented = len(documented_routes)
    total_implemented = len(implemented_routes)

    match_percentage = (
        (len(matching_routes) / total_documented) * 100
        if total_documented > 0
        else 100.0
    )

    return {
        "summary": {
            "total_documented": total_documented,
            "total_implemented": total_implemented,
            "matching_count": len(matching_routes),
            "undocumented_count": len(undocumented_routes),
            "missing_count": len(missing_implementations),
            "match_percentage_against_documented": round(match_percentage, 2),
        },
        "matching_routes": sorted(list(matching_routes)),
        "undocumented_routes": sorted(list(undocumented_routes)),
        "missing_implementations": sorted(list(missing_implementations)),
    }


# ==============================
# Enriched Report (status/deadlines)
# ==============================

def _bucket_status(status: str) -> str:
    s = (status or "").strip().lower()
    if s in {"complete", "completed", "done"}:
        return "completed"
    if s in {"todo", "pending"}:
        return "todo"
    if s in {"inprogress", "in_progress", "doing"}:
        return "inprogress"
    if s in {"updated", "changed"}:
        return "updated"
    return s or "unknown"


def enrich_report_with_roam(
    base_report: Dict[str, Any],
    formatted_roam_json: dict,
    implemented_routes: Set[Tuple[str, str]],
) -> Dict[str, Any]:
    endpoints = []
    status_counts: Dict[str, int] = {}
    overdue_count = 0
    overdue_pending_count = 0
    matching_count = 0

    by_project: Dict[str, Dict[str, int]] = {}

    for ep in iter_documented_endpoints(formatted_roam_json):
        method = (ep.get("method") or "").upper().strip()
        path = (ep.get("path") or "").strip()
        key = (method, path)
        implemented = key in implemented_routes
        status_bucket = _bucket_status(ep.get("status", ""))
        is_overdue = bool(ep.get("is_overdue"))

        status_counts[status_bucket] = status_counts.get(status_bucket, 0) + 1
        if is_overdue:
            overdue_count += 1
            if status_bucket != "completed":
                overdue_pending_count += 1
        if implemented:
            matching_count += 1

        project = (ep.get("project") or "unknown").strip() or "unknown"
        by_project.setdefault(
            project,
            {
                "documented": 0,
                "matching": 0,
                "missing": 0,
                "completed": 0,
                "pending": 0,
                "updated": 0,
                "overdue": 0,
            },
        )
        by_project[project]["documented"] += 1
        if implemented:
            by_project[project]["matching"] += 1
        else:
            by_project[project]["missing"] += 1
        if status_bucket == "completed":
            by_project[project]["completed"] += 1
        elif status_bucket == "updated":
            by_project[project]["updated"] += 1
            by_project[project]["pending"] += 1
        else:
            by_project[project]["pending"] += 1
        if is_overdue:
            by_project[project]["overdue"] += 1

        endpoints.append(
            {
                "method": method,
                "path": path,
                "implemented": implemented,
                "status": ep.get("status", ""),
                "status_bucket": status_bucket,
                "deadline": ep.get("deadline", ""),
                "is_overdue": is_overdue,
                "project": ep.get("project", "") or "unknown",
                "module": ep.get("module", "") or "",
                "owner": ep.get("owner", "") or "unknown",
                "endpoint_name": ep.get("endpoint_name", "") or "",
                "api_version": ep.get("api_version", "") or "",
                "source": ep.get("source", {}) or {},
            }
        )

    base_report = dict(base_report)
    base_report["roam_summary"] = {
        "status_counts": status_counts,
        "overdue_count": overdue_count,
        "overdue_pending_count": overdue_pending_count,
        "matching_count_against_roam_endpoints": matching_count,
        "by_project": by_project,
    }
    base_report["documented_endpoints"] = endpoints
    base_report["meta"] = {
        "generated_at": date.today().isoformat(),
        "roam_source": formatted_roam_json.get("meta", {}),
    }
    return base_report


# ==============================
# Report Writer
# ==============================

def write_report_to_json(report_data: Dict[str, Any], output_path: Path) -> None:
    """
    Writes comparison report to JSON file.
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report_data, indent=4))


# ==============================
# Orchestrator
# ==============================

def execute_validation(roam_formatted_path: Path, output_report_path: Path) -> None:
    """
    Main execution entrypoint.
    """

    application = load_fastapi_application()
    implemented_routes = extract_registered_routes(application)

    formatted_roam = load_roam_formatted(roam_formatted_path)
    documented_routes = load_documented_routes(formatted_roam)

    report = generate_comparison_report(
        implemented_routes,
        documented_routes,
    )
    report = enrich_report_with_roam(report, formatted_roam, implemented_routes)

    write_report_to_json(report, output_report_path)

    print("API contract comparison report generated.")
    print(json.dumps(report["summary"], indent=4))


if __name__ == "__main__":
    script_dir = Path(__file__).resolve().parent
    # scripts/ -> app/ -> python_demo_api/ -> roam_test/
    default_roam_formatted = (script_dir.parents[2] / "roam_data" / "block_7p3IykGtW_formatted.json").resolve()
    # Write the report outside the git repo (into roam_data) so pre-commit
    # can generate it freely without causing commit failures.
    default_output = (script_dir.parents[2] / "roam_data" / "api_contract_report.json").resolve()

    parser = argparse.ArgumentParser(description="Validate implemented FastAPI routes against formatted Roam endpoints.")
    parser.add_argument("--roam-formatted", type=Path, default=default_roam_formatted, help="Path to formatted Roam JSON")
    parser.add_argument("--output", type=Path, default=default_output, help="Where to write the report JSON")
    args = parser.parse_args()

    execute_validation(args.roam_formatted, args.output)