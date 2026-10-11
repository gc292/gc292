# Profile generation

`README.md` displays SVG artwork with `<picture>`: dark/light themes and a narrower layout for viewports up to 650px. GitHub's image proxy may delay visible updates.

Personal content lives in `profile.json`. Keep values concise: the generator validates a 60-character text grid and rejects rows that would overflow. The desktop layout places the Linux ASCII art beside the profile; the compact layout moves the profile below it. Both use the same content and colours.

Run `python3 scripts/update_profile.py` from the repository to regenerate all four SVGs. Python's standard library is sufficient. `GH_TOKEN` is optional locally; GitHub Actions supplies its built-in token automatically. For an offline preview, pass a saved GitHub user API response: `python3 scripts/update_profile.py /path/to/user.json`.

The generator requests only the public user endpoint. `public_repos` comes from GitHub (including forks and this profile repository); account age is calculated from `created_at` in UTC. The refresh date is also calculated in UTC. No follower, star, commit or lines-of-code metrics are displayed or estimated.

The existing Action runs daily, on manual dispatch, and when the configuration, generator or workflow changes. It regenerates and commits all four SVGs. Configuration changes must be accompanied by regenerated SVGs for an immediate local preview.

The public project highlights are futebol-bot and IsKahoot. Private academic work informs the confirmed engineering stack but is not linked or exposed. Fast Paxos is not presented as completed work. All visible profile content is in English.
