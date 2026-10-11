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


def render(config, user, theme, compact=False):
    if theme == 'dark':
        bg, fg, key, value, muted = '#161b22', '#c9d1d9', '#ffa657', '#a5d6ff', '#616e7f'
    else:
        bg, fg, key, value, muted = '#f6f8fa', '#24292f', '#953800', '#0550ae', '#8c959f'
    width, height = (620, 820) if compact else (985, 550)
    column = 24 if compact else 350
    offset = 270 if compact else 0
    columns = 60
    # Both layouts share the same text grid; mobile moves it below the ASCII art.
    text = []
    def plain(x, y, content, color=fg, size=16):
        text.append(f'<text x="{x}" y="{y}" fill="{color}" font-size="{size}">{html.escape(content)}</text>')
    def row(y, label, content):
        content = str(content)
        # Fix the total row width so the right-hand values align as in neofetch.
        if len(label) + len(content) + 6 > columns:
            raise ValueError(f'Profile row is too long: {label}. Shorten its value in profile.json.')
        dots = '.' * (columns - len(label) - len(content) - 5)
        text.append(f'<text x="{column}" y="{y + offset}"><tspan fill="{muted}">. </tspan><tspan fill="{key}">{html.escape(label)}</tspan><tspan fill="{fg}">: </tspan><tspan fill="{muted}">{dots} </tspan><tspan fill="{value}">{html.escape(content)}</tspan></text>')
    def section(y, title):
        plain(column, y + offset, '- ' + title + ' ' + '─' * (columns - len(title) - 3), size=15)
    art = INITIALS if config.get('art') == 'initials' else PENGUIN
    plain(28, 34, '$ whoami', muted, 14)
    for i, line in enumerate(art):
        plain(4 if compact else 0, (65 if compact else 135) + i * (22 if compact else 25), line, fg, 16)
    plain(370 if compact else 113, 75 if compact else 350, config['username'], value, 18)
    for i, line in enumerate(config.get('education', [])):
        plain(330 if compact else 38, (122 if compact else 390) + i * 22, line, muted, 14)
    for i, color in enumerate(['#f85149', '#ffa657', '#e3b341', '#3fb950', '#58a6ff', '#bc8cff', '#a5d6ff', fg]):
        text.append(f'<rect x="{(330 if compact else 42) + 28*i}" y="{188 if compact else 460}" width="24" height="16" fill="{color}"/>')
    plain(column, 30 + offset, config['heading'] + ' ' + '─' * (columns - len(config['heading']) - 1), size=15)
    for i, (label, content) in enumerate(config['system']): row(50 + i * 20, label, content)
    section(170, 'Engineering Stack')
    for i, (label, content) in enumerate(config['stack']): row(190 + i * 20, label, content)
    section(330, 'Public Projects')
    for i, (label, content) in enumerate(config['projects']): row(350 + i * 20, label, content)
    section(410, 'GitHub')
    created = dt.datetime.fromisoformat(user['created_at'].replace('Z', '+00:00'))
    days = (dt.datetime.now(dt.timezone.utc) - created).days
    row(430, 'Repos.Public', user['public_repos'])
    row(450, 'Account.Age', f'{days:,} days')
    plain(column, 510 + offset, 'Updated ' + dt.datetime.now(dt.timezone.utc).strftime('%Y-%m-%d') + ' UTC · public GitHub data', muted, 12)
    return f'''<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{html.escape(config['heading'])} terminal profile">
<rect width="{width}" height="{height}" rx="15" fill="{bg}"/>
<g font-family="Consolas, 'DejaVu Sans Mono', monospace" font-size="15" xml:space="preserve">{''.join(text)}</g></svg>'''


if __name__ == '__main__':
    config = json.loads((ROOT / 'profile.json').read_text())
    if len(sys.argv) == 2:
        user = json.loads(Path(sys.argv[1]).read_text())
    else:
        user = fetch('users/' + config['username'])
    rendered = {
        f'{theme}_mode{"_compact" if compact else ""}.svg': render(config, user, theme, compact)
        for theme in ('dark', 'light') for compact in (False, True)
    }
    for filename, svg in rendered.items():
        (ROOT / filename).write_text(svg + '\n')
