# DANDI NWB Inspector — Brainlife App

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Checks a public NWB file on the DANDI Archive against NWB best practices with NWB Inspector, streaming it without a full download, and outputs text and JSON reports.**

Parses the dandiset ID, version and asset ID from a DANDI asset API URL, resolves its S3 location with the DANDI API, streams the file with remfile and runs nwbinspector on it. Use it to validate NWB files before or after publishing on DANDI. It takes no input dataset, only the asset_url parameter, and needs internet access.

| | |
|---|---|
| 📤 **Outputs** | `raw` |
| 🐳 **Container** | `ghcr.io/catalystneuro/dandi-nwb-inspector-brainlife-app:latest` |
| 🔗 **Run it** | [doi.org/10.25663/brainlife.app.918](https://doi.org/10.25663/brainlife.app.918) |

#### 📤 Outputs

| Output | Datatype | Description |
|---|---|---|
| `output` | `raw` | NWB Inspector results as report.txt (human-readable, grouped by importance) and report.json. |

<details>
<summary><b>⚙️ Parameters</b> (1)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `asset_url` | string |  | Full DANDI asset API URL, e.g. https://api.dandiarchive.org/api/dandisets/<id>/versions/<version>/assets/<asset_id>/. |

</details>

<!-- brainlife-app:end -->

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
