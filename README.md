# World EPG

Automatically generated worldwide Electronic Program Guide (EPG), powered by
the open-source [iptv-org/epg](https://github.com/iptv-org/epg) grabber.

## Features

- Discovers all source configurations available in the upstream `iptv-org/epg`
  repository at run time.
- Downloads EPG data from all discovered sources without restricting countries.
- Runs automatically every 12 hours using GitHub Actions.
- Supports manual runs from the Actions tab.
- Generates XMLTV, GZIP-compressed XMLTV, and JSON.
- Validates all generated files before publishing.
- Publishes generated files to a dedicated `data` branch.
- Replaces only the `data` branch with a fresh single-commit snapshot, keeping
  generated EPG history from growing indefinitely.
- Keeps workflow and validation code on `main`.

## Public guide URLs

Replace `royrover` if the repository owner changes.

- XMLTV: `https://raw.githubusercontent.com/royrover/World-EPG/data/epg/guide.xml`
- XMLTV GZIP: `https://raw.githubusercontent.com/royrover/World-EPG/data/epg/guide.xml.gz`
- JSON: `https://raw.githubusercontent.com/royrover/World-EPG/data/epg/guide.json`

## Schedule

The workflow runs at 00:20 and 12:20 UTC (07:20 and 19:20 Thailand time).

GitHub Actions scheduled workflows can be delayed during periods of high load.
Use **Actions → Update World EPG → Run workflow** to start an update manually.

## Manual run options

The workflow_dispatch form supports:

- `days`: number of days of listings to request (default: 3)
- `max_connections`: maximum concurrent source requests (default: 4)

Use a conservative connection count. Some upstream websites may rate-limit or
block requests when too many connections are opened at once.

## Validation and safe publishing

The workflow validates:

1. XMLTV root and XML syntax.
2. Minimum channel and programme counts.
3. Required programme channel/start/stop attributes.
4. Programme start and stop timestamps.
5. GZIP integrity and exact match with `guide.xml`.
6. JSON syntax and non-empty output.

If grabbing or validation fails, publishing is not run. The previous `data`
branch therefore remains available.

The minimum counts are safety thresholds, not a promise that every country or
every channel has programme data.

## Data coverage

"Worldwide" means all source configurations discovered in the upstream
`iptv-org/epg` repository during that run. It does not mean every TV channel
in every country. Actual coverage depends on source availability, channel
mapping, provider restrictions, and the programme data published by each site.

Some sources may fail, be rate-limited, or provide only a limited number of
days. A successful workflow does not guarantee complete EPG coverage for all
channels.

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
