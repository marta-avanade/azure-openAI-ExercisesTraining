import os
import json
import time
from pathlib import Path
from typing import Optional, Dict, Any, List

import requests
from dotenv import load_dotenv

# Resolve base directory (DocumentIntelligence root) and load .env from there
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(dotenv_path=BASE_DIR / ".env")


def _resolve_path(path_str: str, base_dir: Path) -> Path:
    """Return absolute path; if relative, resolve from base_dir."""
    p = Path(path_str)
    return p if p.is_absolute() else (base_dir / p).resolve()


def analyze_pdf_with_azure(pdf_path: Path, endpoint: str, api_key: str, *, model_id: str, api_version: str,
                           polling_interval_s: float = 2.0, timeout_s: Optional[float] = 120.0) -> dict:
    """
    Analyze a PDF file using Azure Document Intelligence API.

    Args:
        pdf_path: Absolute path to the input PDF file.
        endpoint: Azure endpoint for the Document Intelligence API.
        api_key: Azure API key for authentication.
        model_id: Document Intelligence model to use (e.g., 'prebuilt-layout').
        api_version: API version string (e.g., '2023-07-31').
        polling_interval_s: Seconds between status checks.
        timeout_s: Max seconds to wait before giving up (None for no timeout).

    Returns:
        dict: JSON response from the Azure API.
    """
    # Normalize endpoint (strip trailing slash)
    endpoint = endpoint.rstrip("/")

    headers = {
        "Ocp-Apim-Subscription-Key": api_key,
        "Content-Type": "application/pdf",
    }

    analyze_url = f"{endpoint}/formrecognizer/documentModels/{model_id}:analyze?api-version={api_version}"

    with open(pdf_path, "rb") as pdf_file:
        response = requests.post(analyze_url, headers=headers, data=pdf_file)

    if response.status_code != 202:
        raise Exception(f"Error: {response.status_code}, {response.text}")

    operation_location = (
        response.headers.get("Operation-Location")
        or response.headers.get("operation-location")
    )
    if not operation_location:
        raise Exception(f"Missing Operation-Location header in response: {response.text}")

    print("Processing document with Azure Document Intelligence…")

    # Poll for the result
    start = time.time()
    while True:
        result_response = requests.get(operation_location, headers={"Ocp-Apim-Subscription-Key": api_key})
        result = result_response.json()

        if result_response.status_code != 200:
            raise Exception(f"Error: {result_response.status_code}, {result_response.text}")

        status = result.get("status")
        if status == "succeeded":
            return result
        elif status == "failed":
            raise Exception("Document processing failed.")

        if timeout_s is not None and (time.time() - start) > timeout_s:
            raise TimeoutError("Timed out waiting for document analysis result.")

        time.sleep(polling_interval_s)


def simplify_layout_result(result: Dict[str, Any]) -> Dict[str, Any]:
    """Simplify Azure DI layout result to { pages: [{page_number, text}] }.

    Tries paragraphs by page, then lines by page, then falls back to global content.
    """
    pages_output: List[Dict[str, Any]] = []

    analyze_result = result.get("analyzeResult") or result.get("analyze_result") or {}

    # 1) Prefer paragraphs grouped by page
    paragraphs = analyze_result.get("paragraphs") or []
    if paragraphs:
        by_page: Dict[int, List[str]] = {}
        for p in paragraphs:
            content = p.get("content") or ""
            # Determine page number from boundingRegions (if present)
            page_num = None
            for br in p.get("boundingRegions", []) or []:
                pn = br.get("pageNumber") or br.get("page_number")
                if pn is not None:
                    page_num = pn
                    break
            # Fallback page number as 1 if unknown
            page_num = int(page_num) if page_num is not None else 1
            by_page.setdefault(page_num, []).append(content)

        for pn in sorted(by_page.keys()):
            text = "\n".join([t for t in by_page[pn] if t])
            pages_output.append({"page_number": pn, "text": text})
        return {"pages": pages_output}

    # 2) Next, use lines per page
    pages = analyze_result.get("pages") or []
    if pages:
        for page in pages:
            pn = page.get("pageNumber") or page.get("page_number") or 1
            lines = page.get("lines") or []
            text = "\n".join([ln.get("content") or "" for ln in lines if ln.get("content")])
            pages_output.append({"page_number": int(pn), "text": text})
        return {"pages": pages_output}

    # 3) Fallback: full content
    full_content = analyze_result.get("content") or result.get("content")
    if full_content:
        pages_output.append({"page_number": 1, "text": str(full_content)})
        return {"pages": pages_output}

    # 4) Last resort: return empty structure
    return {"pages": []}

if __name__ == "__main__":
    # Read env vars
    pdf_path_env = os.getenv("PDF_INPUT_PATH", "./data/input.pdf")
    json_path_env = os.getenv("JSON_OUTPUT_PATH", "./data/output.json")
    raw_json_path_env = os.getenv("RAW_JSON_OUTPUT_PATH")
    endpoint = os.getenv("AZURE_ENDPOINT")
    api_key = os.getenv("AZURE_API_KEY")
    api_version = os.getenv("AZURE_API_VERSION", "2023-07-31")
    model_id = os.getenv("AZURE_MODEL_ID", "prebuilt-layout")

    # Validate required configuration
    missing = [k for k, v in {
        "AZURE_ENDPOINT": endpoint,
        "AZURE_API_KEY": api_key,
    }.items() if not v]
    if missing:
        print(f"Missing required env vars: {', '.join(missing)}. Check your .env in {BASE_DIR}.")
        raise SystemExit(1)

    # Resolve paths
    pdf_path = _resolve_path(pdf_path_env, BASE_DIR)
    json_path = _resolve_path(json_path_env, BASE_DIR)
    # Ensure we are not writing JSON to a .pdf by mistake
    if json_path.suffix.lower() != ".json":
        suggested = json_path.with_suffix(".json")
        print(f"Warning: JSON_OUTPUT_PATH does not end with .json. Using: {suggested}")
        json_path = suggested

    # Pre-flight checks
    if not pdf_path.exists():
        print(f"Input PDF not found: {pdf_path}")
        print("Tip: If using a relative path, ensure you run from the project root or keep the default './data/input.pdf'.")
        raise SystemExit(1)

    json_path.parent.mkdir(parents=True, exist_ok=True)

    try:
        result = analyze_pdf_with_azure(
            pdf_path=pdf_path,
            endpoint=endpoint,
            api_key=api_key,
            model_id=model_id,
            api_version=api_version,
        )

        # Optionally write raw result
        if raw_json_path_env:
            raw_path = _resolve_path(raw_json_path_env, BASE_DIR)
            raw_path.parent.mkdir(parents=True, exist_ok=True)
            with open(raw_path, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            print(f"Raw DI JSON written to: {raw_path}")

        # Always write simplified text output
        simplified = simplify_layout_result(result)
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(simplified, json_file, ensure_ascii=False, indent=2)

        print(f"Simplified text JSON written to: {json_path}")
    except Exception as e:
        print(f"An error occurred: {e}")