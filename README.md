<h1 align="center">DANDI NWB Inspector</h1>

<p align="center">
  Checks a public NWB file on the DANDI Archive against NWB best practices with NWB Inspector, streaming it without a full download, and outputs text and JSON reports.
</p>

<p align="center">
  <a href="https://github.com/brainlife/abcd-spec"><img src="https://img.shields.io/badge/ABCD_Spec-v1.1-green.svg" alt="ABCD Spec v1.1"></a>
  <a href="https://doi.org/10.25663/brainlife.app.918"><img src="https://img.shields.io/badge/Brainlife-brainlife.app.918-blue.svg" alt="Run on brainlife.io"></a>
</p>

## At a glance

<!-- brainlife-app:begin (generated from the App manifest; edit the manifest, not this block) -->

> **Checks a public NWB file on the DANDI Archive against NWB best practices with NWB Inspector, streaming it without a full download, and outputs text and JSON reports.**

Parses the dandiset ID, version and asset ID from a DANDI asset API URL, resolves its S3 location with the DANDI API, streams the file with remfile and runs nwbinspector on it. Use it to validate NWB files before or after publishing on DANDI. It takes no input dataset, only the asset_url parameter, and needs internet access.

| | |
|---|---|
| **Outputs** | `raw` |
| **Container** | `ghcr.io/catalystneuro/dandi-nwb-inspector-brainlife-app:latest` |
| **Run it** | [doi.org/10.25663/brainlife.app.918](https://doi.org/10.25663/brainlife.app.918) |

#### Outputs

| Output | Datatype | Description |
|---|---|---|
| `output` | `raw` | NWB Inspector results as report.txt (human-readable, grouped by importance) and report.json. |

<details>
<summary><b>Parameters</b> (1)</summary>

| Parameter | Type | Default | Description |
|---|---|---|---|
| `asset_url` | string |  | Full DANDI asset API URL, e.g. https://api.dandiarchive.org/api/dandisets/<id>/versions/<version>/assets/<asset_id>/. |

</details>

<!-- brainlife-app:end -->

## Running the App

### On brainlife.io

Open the App at [doi.org/10.25663/brainlife.app.918](https://doi.org/10.25663/brainlife.app.918), choose the input datasets from your project, set the parameters and press **Execute**. The results are saved to your project as `raw`.

### Locally

You need [Singularity/Apptainer](https://apptainer.org/) (the App runs in `ghcr.io/catalystneuro/dandi-nwb-inspector-brainlife-app:latest`), [`jq`](https://jqlang.github.io/jq/).

1. Clone this repository.
2. Create `config.json` with the paths to your inputs and the parameters:

   ```json
   {
       "asset_url": ""
   }
   ```

3. Run `./main`.

## Troubleshooting

- **Could not parse DANDI asset URL**: Use the full DANDI asset API URL.

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

## Citing

If you use this App, please cite it, the software it builds on and brainlife.io:

- DANDI NWB Inspector. brainlife.io App. [doi:10.25663/brainlife.app.918](https://doi.org/10.25663/brainlife.app.918)
- Hayashi S, Caron BA, Heinsfeld AS, et al. brainlife.io: a decentralized and open-source cloud platform to support neuroscience research. *Nature Methods* 21:809–813 (2024). [doi:10.1038/s41592-024-02237-2](https://doi.org/10.1038/s41592-024-02237-2)
- Avesani P, McPherson B, Hayashi S, et al. The open diffusion data derivatives, brain data upcycling via integrated publishing of derivatives and reproducible open cloud services. *Scientific Data* 6:69 (2019). [doi:10.1038/s41597-019-0073-y](https://doi.org/10.1038/s41597-019-0073-y)

## Authors

Maintained by [@catalystneuro](https://github.com/catalystneuro).
