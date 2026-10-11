"""Refresh public repository statistics using only the Python standard library."""
import collections
import datetime
import html
import json
import os
from pathlib import Path
import sys
import urllib.request


def repositories(username):
    result = []
    for page in range(1, 101):
        request = urllib.request.Request(
            f'https://api.github.com/users/{username}/repos?per_page=100&page={page}',
            headers={'Accept': 'application/vnd.github+json', 'User-Agent': 'profile-artwork'},
        )
        if os.environ.get('GH_TOKEN'):
            request.add_header('Authorization', 'Bearer ' + os.environ['GH_TOKEN'])
        with urllib.request.urlopen(request, timeout=30) as response:
            batch = json.load(response)
        result.extend(batch)
        if len(batch) < 100:
            return result
    raise RuntimeError('Repository pagination limit reached')


def render(repos):
    public = [r for r in repos if not r['private'] and not r['fork']]
    languages = collections.Counter(r['language'] for r in public if r.get('language'))
    top = languages.most_common(1)[0][0] if languages else '—'
    stars = sum(r['stargazers_count'] for r in public)
    date = datetime.datetime.now(datetime.timezone.utc).strftime('%d %b %Y')
    values = [(str(len(public)), 'PUBLIC ORIGINAL REPOS'), (str(stars), 'REPOSITORY STARS'), (top, 'TOP REPO LANGUAGE')]
    blocks = []
    for i, (value, label) in enumerate(values):
        x = 36 + i * 280
        blocks.append(f'<text x="{x}" y="83" font-size="34" fill="#8fe3cf">{html.escape(value)}</text><text x="{x}" y="112" font-size="10" letter-spacing="1.5" fill="#9aaeb7">{label}</text>')
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="900" height="160" viewBox="0 0 900 160" role="img" aria-label="Public repository statistics">
<rect x="1" y="1" width="898" height="158" rx="16" fill="#101820" stroke="#283b43"/>
<g font-family="Arial, sans-serif"><text x="36" y="29" fill="#9aaeb7" font-size="10" letter-spacing="2">GITHUB / PUBLIC SNAPSHOT</text>
{''.join(blocks)}
<text x="36" y="141" fill="#71868f" font-size="10">Original public repositories · language by repository count · refreshed {date} UTC</text></g></svg>'''


if __name__ == '__main__':
    repos = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) > 1 else repositories(os.environ.get('PROFILE_USERNAME', 'gc292'))
    target = Path(__file__).resolve().parents[1] / 'assets' / 'stats.svg'
    target.write_text(render(repos) + '\n')
