
# Asked claude to do this. I don't care enough.

# I altered build_tasks() to use our dataset / openrouter schema code.



#!/usr/bin/env python3
"""
Threaded POST requests with retry logic, saving each response to its own file.

Usage:
    python threaded_post_requests.py

Customize the `TASKS` list below with the URLs/payloads you want to POST to,
or adapt `build_tasks()` to generate them programmatically.
"""

import json
import logging
import os
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# --------------------------------------------------------------------------
# Configuration
# --------------------------------------------------------------------------

MAX_WORKERS = 10                 # number of concurrent threads
OUTPUT_DIR = Path("responses")   # where response files get saved
REQUEST_TIMEOUT = 15             # seconds, per request attempt

# Retry policy (applied automatically by the HTTP adapter for connection-level
# issues and configurable HTTP status codes), plus a manual outer retry loop
# for anything that slips past that (e.g. timeouts, which urllib3's Retry
# does not cover for the whole request by default in older versions).
MAX_RETRIES = 4
BACKOFF_FACTOR = 1.5             # delay = BACKOFF_FACTOR * (2 ** (attempt - 1))
RETRY_STATUS_CODES = {429, 500, 502, 503, 504}

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)


@dataclass
class Task:
    name: str                     # used to build the output filename
    url: str
    json_body: Optional[dict] = None
    data: Optional[Any] = None
    headers: dict = field(default_factory=dict)


def build_tasks() -> list[Task]:
    """Define the list of requests to fire off. Edit this to fit your needs."""
    
    from tools.references.formats import FormatStyle
    from tools.help import read_json
    from tools.llms.orouterapi import make_payload_completions
    from tools.llms.schemas import ProtoSchemas
    import random

    dataset = read_json("./data/set.json")
    models = ( "deepseek/deepseek-v4-flash",
               "nvidia/nemotron-3-super-120b-a12b",
               "xiaomi/mimo-v2.5",
               "google/gemini-3-flash-preview",
               "minimax/minimax-m3")
               #"anthropic/claude-sonnet-5" )

    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {"Authorization":f"Bearer {os.environ["THEKEY"]}","Content-Type":"application/json" }
    schema = ProtoSchemas.make_schema(ProtoSchemas.make_schema_properties())        # Later on this can be tailored. A "prompt trimming" experiment (make it easier on the AI).

    tasks = []
    for ID, entry in dataset.items():
        for model in models:
            form = random.choice(list(FormatStyle))
            ref = entry["ref_citation"][form]["text"]
            payload = make_payload_completions(model, ref, schema)
            
            name = f"{ID}_{model.split("/")[1]}_{form}"
            
            tasks.append(Task(name=name, url=url, headers=headers, json_body=payload))

    return tasks
    #return [
    #    Task(name=f"item_{i}", url="https://httpbin.org/post", json_body={"id": i})
    #    for i in range(20)
    #]


def build_session() -> requests.Session:
    """
    A session per thread with automatic retries baked into the transport
    adapter, so connection errors / retryable status codes are retried
    without extra code on every call.
    """
    session = requests.Session()
    retry_strategy = Retry(
        total=MAX_RETRIES,
        backoff_factor=BACKOFF_FACTOR,
        status_forcelist=RETRY_STATUS_CODES,
        allowed_methods={"POST"},
        raise_on_status=False,
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    session.mount("http://", adapter)
    session.mount("https://", adapter)
    return session


def post_with_retry(session: requests.Session, task: Task) -> requests.Response:
    """
    Perform the POST with an outer retry loop as well, to catch errors the
    adapter-level Retry doesn't (e.g. ReadTimeout, ConnectionError raised
    before the adapter can intervene, or JSON decode issues downstream).
    """
    last_exc = None
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = session.post(
                task.url,
                json=task.json_body,
                data=task.data,
                headers=task.headers,
                timeout=REQUEST_TIMEOUT,
            )
            if response.status_code in RETRY_STATUS_CODES:
                raise requests.exceptions.HTTPError(
                    f"Retryable status code: {response.status_code}"
                )
            response.raise_for_status()
            return response

        except (
            requests.exceptions.ConnectionError,
            requests.exceptions.Timeout,
            requests.exceptions.HTTPError,
        ) as exc:
            last_exc = exc
            if attempt == MAX_RETRIES:
                break
            delay = BACKOFF_FACTOR * (2 ** (attempt - 1))
            logger.warning(
                "Attempt %d/%d failed for %s (%s). Retrying in %.1fs...",
                attempt, MAX_RETRIES, task.name, exc, delay,
            )
            time.sleep(delay)

        except requests.exceptions.RequestException as exc:
            # Non-retryable request error (e.g. bad URL, SSL issue) - fail fast.
            last_exc = exc
            break

    raise last_exc


def save_response(task: Task, response: requests.Response) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{task.name}.json"

    payload = {
        "task_name": task.name,
        "url": task.url,
        "status_code": response.status_code,
        "headers": dict(response.headers),
    }
    try:
        payload["body"] = response.json()
    except ValueError:
        payload["body"] = response.text

    out_path.write_text(json.dumps(payload, indent=2))
    return out_path


def save_error(task: Task, exc: Exception) -> Path:
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    out_path = OUTPUT_DIR / f"{task.name}.error.json"
    payload = {
        "task_name": task.name,
        "url": task.url,
        "error": str(exc),
        "error_type": type(exc).__name__,
    }
    out_path.write_text(json.dumps(payload, indent=2))
    return out_path


def worker(task: Task) -> tuple[str, bool, str]:
    """Runs in a thread: does the POST, saves result, returns a status tuple."""
    session = build_session()
    try:
        response = post_with_retry(session, task)
        out_path = save_response(task, response)
        logger.info("Saved response for %s -> %s", task.name, out_path)
        return (task.name, True, str(out_path))
    except Exception as exc:
        out_path = save_error(task, exc)
        logger.error("Giving up on %s after retries: %s", task.name, exc)
        return (task.name, False, str(out_path))
    finally:
        session.close()


def main():
    tasks = build_tasks()
    logger.info("Starting %d tasks with %d worker threads", len(tasks), MAX_WORKERS)

    results = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS, thread_name_prefix="poster") as executor:
        future_to_task = {executor.submit(worker, task): task for task in tasks}
        for future in as_completed(future_to_task):
            task = future_to_task[future]
            try:
                results.append(future.result())
            except Exception as exc:
                # Should be rare since worker() catches internally, but just in case.
                logger.error("Unhandled exception for %s: %s", task.name, exc)
                results.append((task.name, False, "unhandled_exception"))

    succeeded = sum(1 for _, ok, _ in results if ok)
    failed = len(results) - succeeded
    logger.info("Done. %d succeeded, %d failed. Output dir: %s",
                succeeded, failed, OUTPUT_DIR.resolve())


if __name__ == "__main__":
    main()
