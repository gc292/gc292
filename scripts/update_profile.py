"""Generate neofetch profile SVGs with public GitHub statistics."""
import datetime as dt
import html
import hashlib
import json
import os
import re
from pathlib import Path
import sys
import urllib.parse
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
INITIALS = [
    ' ██████╗  ██████╗ ',
    '██╔════╝ ██╔════╝ ',
    '██║  ███╗██║      ',
    '██║   ██║██║      ',
    '╚██████╔╝╚██████╗ ',
    ' ╚═════╝  ╚═════╝ ',
]


def fetch(path):
    headers = {'User-Agent': 'gc292-profile', 'Accept': 'application/vnd.github+json'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    request = urllib.request.Request('https://api.github.com/' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def load_public(username):
    username = urllib.parse.quote(username, safe='')
    user = fetch('users/' + username)
    repos = []
    for page in range(1, 101):
        batch = fetch(f'users/{username}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            break
    else:
        raise RuntimeError('Repository pagination limit reached')
    query = urllib.parse.urlencode({'q': f'author:{username} is:public', 'per_page': 1})
    commits = fetch('search/commits?' + query)
    if commits['incomplete_results']:
        raise RuntimeError('Incomplete commit statistics; existing SVGs preserved')
    return {'user': user, 'repos': repos, 'commits': commits}


def render(config, snapshot, theme, compact=False):
    if theme == 'dark':
        bg, fg, key, value, muted = '#161b22', '#c9d1d9', '#ffa657', '#a5d6ff', '#616e7f'
    else:
        bg, fg, key, value, muted = '#f6f8fa', '#24292f', '#953800', '#0550ae', '#8c959f'
    width, height = (650, 860) if compact else (985, 630)
    column, offset = (24, 230) if compact else (350, 0)
    columns, label_width = 65, 24
    now = dt.datetime.now(dt.timezone.utc)
    user = snapshot['user']
    created = dt.datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
    account_age = f'{(now - created).days:,} days'
    text = []

    def plain(x, y, content, color=fg, size=15):
        text.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{html.escape(content)}</text>')

    def row(y, label, content):
        content = str(content).replace('{account_age}', account_age)
        prefix = label + ':' if label else ''
        if len(prefix) > label_width or len(content) > columns - label_width:
            raise ValueError(f'Profile row is too long: {label}. Shorten its value in profile.json.')
        padding = ' ' * (label_width - len(prefix))
        text.append(f'<text x="{column}" y="{y + offset}"><tspan fill="{key}">{html.escape(prefix)}</tspan><tspan>{padding}</tspan><tspan fill="{value}">{html.escape(content)}</tspan></text>')

    def section(y, title):
        plain(column, y + offset, '- ' + title + ' ' + '─' * (columns - len(title) - 3))

    plain(28, 34, '$ whoami', muted, 14)
    for i, line in enumerate(INITIALS):
        plain(32 if compact else 18, (65 if compact else 200) + i * 25, line, value, 23)
    plain(380 if compact else 100, 100 if compact else 375, config['username'], fg, 18)
    for i, color in enumerate(['#f85149', '#ffa657', '#e3b341', '#3fb950', '#58a6ff', '#bc8cff', '#a5d6ff', fg]):
        text.append(f'<rect x="{(350 if compact else 42) + 28*i}" y="{155 if compact else 430}" width="24" height="16" fill="{color}"/>')
    plain(column, 30 + offset, config['heading'])
    plain(column, 43 + offset, '─' * columns, muted)
    for i, (label, content) in enumerate(config['system']): row(65 + i * 20, label, content)
    section(180, 'Languages')
    for i, (label, content) in enumerate(config['languages']): row(205 + i * 20, label, content)
    section(280, 'Hobbies')
    for i, (label, content) in enumerate(config['hobbies']): row(305 + i * 20, label, content)
    section(380, 'Contact')
    for i, (label, content) in enumerate(config['contact']): row(405 + i * 20, label, content)
    section(480, 'GitHub Stats')
    stars = sum(r['stargazers_count'] for r in snapshot['repos'] if not r['private'] and not r['fork'])
    for i, (label, content) in enumerate([
        ('Repos', user['public_repos']),
        ('Commits.Public', snapshot['commits']['total_count']),
        ('Stars', stars),
        ('Followers', user['followers']),
        ('Account.Uptime', account_age),
    ]): row(505 + i * 20, label, content)
    plain(28 if not compact else column, height - 12, 'Updated ' + now.strftime('%Y-%m-%d') + ' UTC · public indexed GitHub data', muted, 11)
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(config['heading'])} neofetch profile">
<rect width="{width}" height="{height}" rx="15" fill="{bg}"/>
<g font-family="Consolas, 'DejaVu Sans Mono', monospace" font-size="15" fill="{fg}" xml:space="preserve">{''.join(text)}</g></svg>"""


if __name__ == '__main__':
    config = json.loads((ROOT / 'profile.json').read_text())
    snapshot = json.loads(Path(sys.argv[1]).read_text()) if len(sys.argv) == 2 else load_public(config['username'])
    if snapshot['commits']['incomplete_results']:
        raise RuntimeError('Incomplete commit statistics; existing SVGs preserved')
    rendered = {
        f'{theme}_mode{"_compact" if compact else ""}.svg': render(config, snapshot, theme, compact)
        for theme in ('dark', 'light') for compact in (False, True)
    }
    for filename, svg in rendered.items():
        (ROOT / filename).write_text(svg + '\n')
    # Version image URLs by content so GitHub's image cache sees fresh artwork.
    readme_path = ROOT / 'README.md'
    readme = readme_path.read_text()
    for filename, svg in rendered.items():
        version = hashlib.sha256((svg + '\n').encode()).hexdigest()[:12]
        pattern = r'((?:src|srcset)=")(?:https://raw\.githubusercontent\.com/[^"\s]+/)?' + re.escape(filename) + r'(?:\?[^"\s]*)?"'
        url = f'https://raw.githubusercontent.com/{config["username"]}/{config["username"]}/main/{filename}?v={version}'
        readme = re.sub(pattern, lambda match: match[1] + url + '"', readme)
    readme_path.write_text(readme)
