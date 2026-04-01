# app-dandi-nwb-inspector

A Brainlife app prototype that streams a public NWB file from the DANDI archive and prints a summary of its contents.

## How it works

1. Reads `dandiset_id`, `version`, and `asset_path` from `config.json`
2. Uses the DANDI API to get an S3 URL for the asset
3. Streams the NWB file using `remfile` (no full download required)
4. Extracts and prints file metadata, subject info, acquisition keys, processing modules, etc.
5. Writes `summary.txt` (Brainlife raw output) and `product.json` (Brainlife UI)

## Local testing

```bash
cp config.json.sample config.json
pip install -r requirements.txt
./main
```

## Brainlife registration

- **Input datatypes**: none (config-parameter driven)
- **Config params**: `dandiset_id` (string), `version` (string, default "draft"), `asset_path` (string)
- **Output**: `raw` datatype containing `summary.txt`
