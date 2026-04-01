# DANDI NWB Inspector — Brainlife App

A Brainlife app that runs [NWB Inspector](https://github.com/NeurodataWithoutBorders/nwbinspector) on a public NWB file from the DANDI archive. The file is streamed directly from DANDI — no full download required.

## How it works

1. Reads a DANDI `asset_url` from `config.json`
2. Parses the dandiset ID, version, and asset ID from the URL
3. Uses the DANDI API to get an S3 URL for the asset
4. Streams the NWB file using `remfile` (no full download required)
5. Runs NWB Inspector to check for best practices and potential issues
6. Writes `output/report.txt` (human-readable) and `output/report.json` (structured results)
7. Displays the report in the Brainlife UI via `product.json`

## Local testing

```bash
cp config.json.sample config.json
pip install -r requirements.txt
./main
```

Edit `config.json` to point to any public DANDI asset URL, e.g.:

```json
{
    "asset_url": "https://api.dandiarchive.org/api/dandisets/000950/versions/0.241029.1403/assets/e114bc42-dcb5-4c02-b663-545b49d04664/"
}
```

## Brainlife registration

- **Input datatypes**: none (config-parameter driven)
- **Config params**: `asset_url` (string) — full DANDI asset API URL
- **Output**: `raw` datatype, output directory: `output`
