"""Generate a terminal-style profile in dark and light themes. No dependencies."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import sys
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
PENGUIN = [
    '              .--.              ',
    '             |o_o |             ',
    '             |:_/ |             ',
    '            //   \\ \\            ',
    '           (|     | )           ',
    '          /\'\\_   _/`\\           ',
    '          \\___)=(___/           ',
]
INITIALS = [
    '     ██████╗  ██████╗     ',
    '    ██╔════╝ ██╔════╝     ',
    '    ██║  ███╗██║         ',
    '    ██║   ██║██║         ',
    '    ╚██████╔╝╚██████╗    ',
    '     ╚═════╝  ╚═════╝    ',
]


def fetch(path):
    headers = {'User-Agent': 'gc292-profile', 'Accept': 'application/vnd.github+json'}
    if os.environ.get('GH_TOKEN'):
        headers['Authorization'] = 'Bearer ' + os.environ['GH_TOKEN']
    request = urllib.request.Request('https://api.github.com/' + path, headers=headers)
    with urllib.request.urlopen(request, timeout=30) as response:
        return json.load(response)


def load_public(username):
    user = fetch('users/' + username)
    repos = []
    for page in range(1, 101):
        batch = fetch(f'users/{username}/repos?per_page=100&page={page}')
        repos.extend(batch)
        if len(batch) < 100:
            return user, repos
    raise RuntimeError('Pagination limit reached')


def render(config, user, repos, theme):
    if theme == 'dark':
        bg, fg, key, value, muted = '#161b22', '#c9d1d9', '#ffa657', '#a5d6ff', '#616e7f'
    else:
        bg, fg, key, value, muted = '#f6f8fa', '#24292f', '#953800', '#0550ae', '#8c959f'
    text = []
    def plain(x, y, content, color=fg, size=16):
        text.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{html.escape(content)}</text>')
    def row(y, label, content):
        content = str(content)
        # Fix the total row width so the right-hand values align as in neofetch.
        dots = '.' * max(2, 56 - len(label) - len(content) - 4)
        text.append(f'<text x="390" y="{y}"><tspan fill="{muted}">. </tspan><tspan fill="{key}">{html.escape(label)}</tspan><tspan fill="{fg}">: </tspan><tspan fill="{muted}">{dots} </tspan><tspan fill="{value}">{html.escape(content)}</tspan></text>')
    def section(y, title):
        plain(390, y, '- ' + title + ' ' + '─' * (54 - len(title)))
    art = INITIALS if config.get('art') == 'initials' else PENGUIN
    plain(28, 34, '$ whoami', muted, 14)
    for i, line in enumerate(art):
        plain(16, 163 + i * 25, line, fg, 18)
    plain(130, 375, config['username'], value, 18)
    plain(82, 405, 'build · learn · repeat', muted, 13)
    for i, color in enumerate(['#f85149', '#ffa657', '#e3b341', '#3fb950', '#58a6ff', '#bc8cff', '#a5d6ff', fg]):
        text.append(f'<rect x="{66 + 28*i}" y="443" width="24" height="16" fill="{color}"/>')
    plain(390, 30, config['heading'] + ' ' + '─' * (56 - len(config['heading'])))
    for i, (label, content) in enumerate(config['system']): row(50 + i * 20, label, content)
    for i, (label, content) in enumerate(config['languages']): row(170 + i * 20, label, content)
    section(290, 'Projects / Contact')
    for i, (label, content) in enumerate(config['projects']): row(310 + i * 20, label, content)
    section(410, 'GitHub Stats')
    original = [r for r in repos if not r['fork'] and not r['private']]
    stars = sum(r['stargazers_count'] for r in original)
    created = dt.datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
    days = (dt.datetime.now(dt.timezone.utc) - created).days
    row(430, 'Repos.Public', user['public_repos'])
    row(450, 'Stars / Followers', f"{stars} / {user['followers']}")
    row(470, 'Account.Uptime', f'{days:,} days')
    plain(390, 510, 'Updated ' + dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d') + ' UTC · public GitHub data', muted, 12)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="985" height="530" viewBox="0 0 985 530" role="img" aria-label="{html.escape(config['heading'])} terminal profile">
<rect width="985" height="530" rx="15" fill="{bg}"/>
<g font-family="Consolas, 'DejaVu Sans Mono', monospace" font-size="16" xml:space="preserve">{''.join(text)}</g></svg>'''


if __name__ == '__main__':
    config = json.loads((ROOT / 'profile.json').read_text())
    if len(sys.argv) == 3:
        user = json.loads(Path(sys.argv[1]).read_text())
        repos = json.loads(Path(sys.argv[2]).read_text())
    else:
        user, repos = load_public(config['username'])
    rendered = {theme: render(config, user, repos, theme) for theme in ('dark', 'light')}
    for theme, svg in rendered.items():
        (ROOT / f'{theme}_mode.svg').write_text(svg + '\n')
