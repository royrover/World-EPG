# World EPG

Automatically generated Electronic Program Guide (EPG), powered by the
open-source [iptv-org/epg](https://github.com/iptv-org/epg) grabber.

Each source website gets its own XMLTV file, so channel IDs always match the
playlist that uses that source (no cross-source ID merging).

## Features

- Selects source configurations from the upstream `iptv-org/epg` repository at
  run time, filtered by the `TARGET_REGEX` in the workflow (currently
  `trueid|3bb`).
- Grabs each source separately and writes one set of files per source.
- Skips a source that fails to download; the run only fails if every source
  fails.
- Runs automatically once a day using GitHub Actions.
- Supports manual runs from the Actions tab.
- Generates XMLTV, GZIP-compressed XMLTV, and JSON for each source.
- Validates all generated files before publishing.
- Publishes generated files to a dedicated `data` branch.
- Replaces only the `data` branch with a fresh single-commit snapshot, keeping
  generated EPG history from growing indefinitely.
- Keeps workflow and validation code on `main`.

## Public guide URLs

Replace `royrover` if the repository owner changes. Replace `<site>` with the
source name, for example `tv.trueid.net` or `gigatv.3bbtv.co.th`.

- XMLTV: `https://raw.githubusercontent.com/royrover/World-EPG/data/epg/<site>.xml`
- XMLTV GZIP: `https://raw.githubusercontent.com/royrover/World-EPG/data/epg/<site>.xml.gz`
- JSON: `https://raw.githubusercontent.com/royrover/World-EPG/data/epg/<site>.json`

In an M3U playlist, point `url-tvg` at the file of the source that playlist
uses, for example:

```
#EXTM3U url-tvg="https://raw.githubusercontent.com/royrover/World-EPG/data/epg/tv.trueid.net.xml"

#EXTM3U url-tvg="https://raw.githubusercontent.com/royrover/World-EPG/data/epg/gigatv.3bbtv.co.th.xml"
```

## Schedule

The workflow runs daily at 00:20 UTC (07:20 Thailand time).

## Choosing sources

Edit `TARGET_REGEX` in the `Discover targeted EPG sources` step of
`.github/workflows/update-epg.yml`. It is matched against the folder names in
`epg-engine/sites`. For example, `(trueid|3bb)` selects every folder whose name
contains `trueid` or `3bb`.

## Manual run options

The workflow_dispatch form supports:

- `days`: number of days of listings to request (default: 2)
- `max_connections`: maximum concurrent source requests (default: 4)

Use a conservative connection count. Some upstream websites may rate-limit or
block requests when too many connections are opened at once.

## Validation and safe publishing

For every `<site>.xml` in the output folder the workflow validates:

1. XMLTV root and XML syntax.
2. Minimum channel and programme counts.
3. Required programme channel/start/stop attributes.
4. Programme start and stop timestamps.
5. Every programme references a channel that exists in the same file.
6. GZIP integrity and exact match with `<site>.xml`.
7. JSON syntax and non-empty output.

If grabbing or validation fails, publishing is not run. The previous `data`
branch therefore remains available.

The minimum counts are safety thresholds, not a promise that every channel has
programme data.

## Data coverage

Coverage depends on source availability, channel mapping, provider
restrictions, and the programme data published by each site. Some sources may
fail, be rate-limited, or provide only a limited number of days. A successful
workflow does not guarantee complete EPG coverage for all channels.

## First-time setup

1. Create a public GitHub repository named `World-EPG` under `royrover`.
2. Push the files from this project to the repository's `main` branch.
3. Open **Settings → Actions → General**.
4. Under **Workflow permissions**, select **Read and write permissions**.
5. Save the setting.
6. Open **Actions**, enable workflows if GitHub asks, then run **Update World EPG**.
7. Wait for the first run to finish successfully. It creates the `data` branch.

No personal access token is required. The workflow uses the repository's
built-in `GITHUB_TOKEN`.

## License and upstream

The grabber and source configurations are maintained by
[iptv-org/epg](https://github.com/iptv-org/epg). Each upstream source may have
its own terms, access limits, and data availability. Review those terms before
redistributing data.
