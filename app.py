#!/usr/bin/env python3
"""Brainlife app: Run NWB Inspector on a DANDI asset."""

import json
import re
from pathlib import Path

import h5py
import remfile
from dandi.dandiapi import DandiAPIClient
from nwbinspector import inspect_nwbfile_object
from pynwb import NWBHDF5IO


def parse_asset_url(url):
    """Parse a DANDI asset API URL into dandiset_id, version, and asset_id.

    Accepts URLs like:
      https://api.dandiarchive.org/api/dandisets/000950/versions/0.241029.1403/assets/e114bc42-dcb5-4c02-b663-545b49d04664/
    """
    pattern = r"dandisets/(\d+)/versions/([^/]+)/assets/([^/]+)"
    match = re.search(pattern, url)
    if not match:
        raise ValueError(f"Could not parse DANDI asset URL: {url}")
    return match.group(1), match.group(2), match.group(3)


def format_message(msg):
    """Format a single InspectorMessage into a readable dict."""
    return {
        "importance": msg.importance.name,
        "check": msg.check_function_name,
        "object_type": msg.object_type,
        "object_name": msg.object_name,
        "location": msg.location,
        "message": msg.message,
    }


def format_report(dandiset_id, version, asset_id, asset_path, messages):
    """Format inspection results into a human-readable string."""
    lines = [
        "=" * 60,
        "NWB Inspector Report",
        "=" * 60,
        "",
        f"Dandiset:    {dandiset_id}",
        f"Version:     {version}",
        f"Asset ID:    {asset_id}",
        f"Asset path:  {asset_path}",
        "",
    ]

    if not messages:
        lines.append("No issues found.")
        return "\n".join(lines)

    # Group by importance
    by_importance = {}
    for msg in messages:
        key = msg["importance"]
        by_importance.setdefault(key, []).append(msg)

    # Display order
    order = ["CRITICAL", "BEST_PRACTICE_VIOLATION", "BEST_PRACTICE_SUGGESTION", "ERROR"]
    for importance in order:
        group = by_importance.get(importance, [])
        if not group:
            continue
        lines.append(f"--- {importance} ({len(group)}) ---")
        for msg in group:
            location = msg["location"] or ""
            obj = msg["object_name"] or ""
            prefix = f"  [{msg['check']}]"
            if obj:
                prefix += f" {obj}"
            if location:
                prefix += f" @ {location}"
            lines.append(prefix)
            lines.append(f"    {msg['message']}")
        lines.append("")

    total = len(messages)
    lines.append(f"Total issues: {total}")
    return "\n".join(lines)


def main():
    # Read Brainlife config
    with open("config.json") as f:
        cfg = json.load(f)

    asset_url = cfg["asset_url"]
    dandiset_id, version, asset_id = parse_asset_url(asset_url)

    print(f"Fetching asset from DANDI: {dandiset_id}/{version}/{asset_id}")

    # Get S3 URL from DANDI (no auth needed for public data)
    with DandiAPIClient() as client:
        dandiset = client.get_dandiset(dandiset_id, version)
        asset = dandiset.get_asset(asset_id)
        asset_path = asset.path
        s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)

    print(f"Asset path: {asset_path}")
    print(f"Streaming NWB from: {s3_url}")

    # Stream-read NWB file and run inspector
    rem_file = remfile.File(s3_url)
    with h5py.File(rem_file, "r") as h5_file:
        with NWBHDF5IO(file=h5_file, load_namespaces=True) as io:
            nwbfile = io.read()
            print("Running NWB Inspector...")
            raw_messages = list(inspect_nwbfile_object(nwbfile))

    messages = [format_message(msg) for msg in raw_messages]

    # Format and print report
    report = format_report(dandiset_id, version, asset_id, asset_path, messages)
    print(report)

    # Write Brainlife raw output
    outdir = Path("output")
    outdir.mkdir(exist_ok=True)
    (outdir / "report.txt").write_text(report)
    (outdir / "report.json").write_text(json.dumps(messages, indent=2))

    # Count issues by importance for product.json summary
    counts = {}
    for msg in messages:
        counts[msg["importance"]] = counts.get(msg["importance"], 0) + 1

    # Build Plotly bar chart of issues by importance
    importance_order = ["CRITICAL", "BEST_PRACTICE_VIOLATION", "BEST_PRACTICE_SUGGESTION"]
    importance_colors = {
        "CRITICAL": "#e74c3c",
        "BEST_PRACTICE_VIOLATION": "#e67e22",
        "BEST_PRACTICE_SUGGESTION": "#f1c40f",
    }
    chart_labels = [level for level in importance_order if counts.get(level, 0) > 0]
    chart_values = [counts[level] for level in chart_labels]
    chart_colors = [importance_colors[level] for level in chart_labels]

    plotly_chart = {
        "type": "plotly",
        "name": "Issues by Importance",
        "data": {
            "data": [
                {
                    "type": "bar",
                    "x": chart_values,
                    "y": chart_labels,
                    "orientation": "h",
                    "marker": {"color": chart_colors},
                }
            ],
            "layout": {
                "title": "NWB Inspector Issues by Importance",
                "xaxis": {"title": "Number of Issues"},
                "yaxis": {"autorange": "reversed"},
                "margin": {"l": 220},
            },
        },
    }

    # Write product.json for Brainlife UI
    product = {
        "brainlife": {
            "ui": [
                {
                    "type": "text",
                    "name": "NWB Inspector Report",
                    "value": report,
                },
                plotly_chart,
            ]
        },
        "dandiset_id": dandiset_id,
        "version": version,
        "asset_id": asset_id,
        "asset_path": asset_path,
        "total_issues": len(messages),
        "counts": counts,
        "messages": messages,
    }
    Path("product.json").write_text(json.dumps(product, indent=2, default=str))

    print(f"\nDone. Output written to output/ and product.json")


if __name__ == "__main__":
    main()
