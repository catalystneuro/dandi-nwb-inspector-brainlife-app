#!/usr/bin/env python3
"""Brainlife app: Stream an NWB file from DANDI and print its contents."""

import json
from pathlib import Path

import h5py
import remfile
from dandi.dandiapi import DandiAPIClient
from pynwb import NWBHDF5IO


def safe_attr(obj, name, default=None):
    """Safely get an attribute, returning default if obj is None or attr missing."""
    if obj is None:
        return default
    return getattr(obj, name, default)


def inspect_nwb(nwbfile):
    """Extract a structured summary from an open NWB file."""
    subject = nwbfile.subject
    summary = {
        "identifier": safe_attr(nwbfile, "identifier"),
        "session_description": safe_attr(nwbfile, "session_description"),
        "session_start_time": str(safe_attr(nwbfile, "session_start_time", "")),
        "subject": {
            "subject_id": safe_attr(subject, "subject_id"),
            "species": safe_attr(subject, "species"),
            "age": safe_attr(subject, "age"),
            "sex": safe_attr(subject, "sex"),
        },
        "acquisition": list(nwbfile.acquisition.keys()),
        "processing_modules": list(nwbfile.processing.keys()),
        "devices": list(nwbfile.devices.keys()),
        "electrode_groups": list(nwbfile.electrode_groups.keys()),
        "electrodes_columns": (
            list(nwbfile.electrodes.colnames) if nwbfile.electrodes is not None else []
        ),
        "units_columns": (
            list(nwbfile.units.colnames) if nwbfile.units is not None else []
        ),
        "intervals": {
            name: len(table) for name, table in nwbfile.intervals.items()
        } if nwbfile.intervals else {},
    }
    return summary


def format_summary(dandiset_id, version, asset_path, summary):
    """Format the summary dict into a human-readable string."""
    lines = [
        "=" * 60,
        "DANDI NWB Inspector — Summary",
        "=" * 60,
        "",
        f"Dandiset:            {dandiset_id}",
        f"Version:             {version}",
        f"Asset path:          {asset_path}",
        "",
        f"Identifier:          {summary['identifier']}",
        f"Session description: {summary['session_description']}",
        f"Session start time:  {summary['session_start_time']}",
        "",
        "--- Subject ---",
        f"  ID:      {summary['subject']['subject_id']}",
        f"  Species: {summary['subject']['species']}",
        f"  Age:     {summary['subject']['age']}",
        f"  Sex:     {summary['subject']['sex']}",
        "",
        f"Acquisition keys:    {summary['acquisition']}",
        f"Processing modules:  {summary['processing_modules']}",
        f"Devices:             {summary['devices']}",
        f"Electrode groups:    {summary['electrode_groups']}",
        f"Electrodes columns:  {summary['electrodes_columns']}",
        f"Units columns:       {summary['units_columns']}",
    ]

    if summary["intervals"]:
        lines.append(f"Intervals:")
        for name, count in summary["intervals"].items():
            lines.append(f"  {name}: {count} rows")

    lines.append("")
    return "\n".join(lines)


def main():
    # Read Brainlife config
    with open("config.json") as f:
        cfg = json.load(f)

    dandiset_id = cfg["dandiset_id"]
    version = cfg.get("version", "draft")
    asset_path = cfg["asset_path"]

    print(f"Fetching asset from DANDI: {dandiset_id}/{version}/{asset_path}")

    # Get S3 URL from DANDI (no auth needed for public data)
    with DandiAPIClient() as client:
        dandiset = client.get_dandiset(dandiset_id, version)
        asset = dandiset.get_asset_by_path(asset_path)
        s3_url = asset.get_content_url(follow_redirects=1, strip_query=True)

    print(f"Streaming NWB from: {s3_url}")

    # Stream-read NWB file (no full download)
    rem_file = remfile.File(s3_url)
    with h5py.File(rem_file, "r") as h5_file:
        with NWBHDF5IO(file=h5_file, load_namespaces=True) as io:
            nwbfile = io.read()
            summary = inspect_nwb(nwbfile)

    # Format and print
    text = format_summary(dandiset_id, version, asset_path, summary)
    print(text)

    # Write Brainlife raw output
    Path("summary.txt").write_text(text)

    # Write product.json for Brainlife UI
    product = {
        "brainlife": {
            "ui": [
                {
                    "type": "text",
                    "name": "NWB Summary",
                    "value": text,
                }
            ]
        },
        **summary,
    }
    Path("product.json").write_text(json.dumps(product, indent=2, default=str))

    print("\nDone. Output written to summary.txt and product.json")


if __name__ == "__main__":
    main()
