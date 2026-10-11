# Neofetch profile generation

Personal fields are in `profile.json`; ASCII initials and layout are in `scripts/update_profile.py`. Run `python3 scripts/update_profile.py` to regenerate dark/light desktop and compact SVGs. Only the Python standard library is required. `README.md` selects the theme and compact layout using `<picture>` and provides clickable GitHub, LinkedIn and email links.

The generator also versions the four image URLs in README.md with a hash of their SVG content. It uses direct raw.githubusercontent.com URLs because GitHub's redirect for relative raw image URLs drops query parameters. Changed artwork receives a new URL so cached profile images refresh; unchanged artwork retains the same URL. The Action commits README.md along with the SVGs.

The Action runs daily, on manual dispatch and on configuration/generator/workflow changes. Its built-in `github.token` supplies optional API authentication and authorizes committing the four SVGs. No personal access token is required.

Statistics come from GitHub's public API:

- Repos: public repository count, including forks and the profile repository.
- Commits.Public: public indexed commits authored by gc292, returned by commit search (`author:gc292 is:public`). This is not private activity or the contributions calendar. Incomplete searches stop generation and preserve existing SVGs.
- Stars: stars across original public repositories, excluding forks.
- Followers: the public follower count.
- Uptime and Account.Uptime: days since the GitHub account was created, calculated in UTC. Uptime is explicitly marked `(GitHub)` because no birth date or host boot time has been provided.

Commit search documentation: https://docs.github.com/en/rest/search/search#search-commits

An offline snapshot may be passed as the sole command argument. It must contain `user` (GitHub user response), `repos` (all pages of the public repository list), and `commits` (commit search response). The snapshot is not committed. Personal configuration never contains fixed statistics.

The generator validates a 65-character grid with 24-character labels and 41-character values. Long descriptions can use continuation rows with an empty label. All four variants are rendered before any output is written, so API/validation failures preserve previous artwork.
