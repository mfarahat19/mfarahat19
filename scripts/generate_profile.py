#!/usr/bin/env python3
"""Build the animated profile images in assets/ from live GitHub data.

Standard library only. Usage: GH_TOKEN=... python3 scripts/generate_profile.py

GitHub shows these SVGs through <img>, where CSS animation runs but scripts do not.
"""
import base64
import json
import os
import pathlib
import re
import urllib.request
from datetime import date
from html import escape

LOGIN = "mfarahat19"
FIRST_NAME, LAST_NAME = "Mohamed", "Farahat"
TYPED_LINES = ["Flutter Developer", "Clean Architecture & SOLID", "Firebase & Supabase", "AI agents & MCP"]
PROJECTS = [
    ("MovieApp", "Movie browsing app"),
    ("IslamiApp", "Islamic companion app"),
    ("Ecommerce-App", "Online shopping app"),
    ("Clean-Architecture-Repo", "Clean Architecture in practice"),
]
STACK = ["flutter", "dart", "firebase", "supabase", "androidstudio", "java", "git", "github", "docker", "figma", "vscode"]
ROOT = pathlib.Path(__file__).resolve().parent.parent
ASSETS = ROOT / "assets"

SANS = "-apple-system,BlinkMacSystemFont,'Segoe UI',Helvetica,Arial,sans-serif"
MONO = "ui-monospace,SFMono-Regular,Menlo,Consolas,monospace"
BG, CARD, BORDER = "#070b14", "#0d1420", "#1f2a3a"
TEXT, MUTED, CYAN, BLUE = "#f4f8ff", "#93a1b5", "#54c5f8", "#2f7bf6"
REDUCED = "@media (prefers-reduced-motion:reduce){*{animation:none!important}}"

QUERY = """
query($login: String!) {
  user(login: $login) {
    repositories(ownerAffiliations: OWNER, isFork: false, privacy: PUBLIC, first: 100) {
      totalCount
      nodes { name stargazerCount primaryLanguage { name color } }
    }
    contributionsCollection {
      contributionCalendar {
        totalContributions
        weeks { contributionDays { date contributionCount weekday } }
      }
    }
  }
}
"""


def fetch():
    request = urllib.request.Request(
        "https://api.github.com/graphql",
        data=json.dumps({"query": QUERY, "variables": {"login": LOGIN}}).encode(),
        headers={"Authorization": f"bearer {os.environ['GH_TOKEN']}", "User-Agent": "profile-images"},
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        payload = json.load(response)
    if payload.get("errors"):
        raise SystemExit(payload["errors"])
    return payload["data"]["user"]


def text(x, y, value, size, fill=TEXT, weight=400, extra=""):
    return f'<text x="{x}" y="{y}" font-size="{size}" fill="{fill}" font-weight="{weight}" {extra}>{escape(str(value))}</text>'


def bars(x, y, widths, fill="#2a3a52", step=16):
    return "".join(f'<rect x="{x}" y="{y + i * step}" width="{w}" height="7" rx="3.5" fill="{fill}"/>' for i, w in enumerate(widths))


def movie_screen():
    posters = "".join(
        f'<rect x="{12 + col * 62}" y="{44 + row * 86}" width="54" height="78" rx="8" fill="{color}"/>'
        for row, colors in enumerate((("#e5484d", "#2f7bf6"), ("#f5a524", "#8e4ec6"), ("#12a594", "#e93d82")))
        for col, color in enumerate(colors)
    )
    return text(12, 32, "Movies", 15, TEXT, 700) + posters


def islami_screen():
    crescent = (
        '<circle cx="66" cy="76" r="26" fill="#f5c451"/><circle cx="76" cy="69" r="23" fill="#0b1626"/>'
    )
    rows = "".join(
        f'<rect x="12" y="{122 + i * 36}" width="116" height="28" rx="8" fill="#13233a"/>'
        f'<circle cx="26" cy="{136 + i * 36}" r="6" fill="#30a46c"/>'
        f'<rect x="40" y="{133 + i * 36}" width="{w}" height="6" rx="3" fill="#3b4f6b"/>'
        for i, w in enumerate((70, 52, 78, 60))
    )
    return text(12, 32, "Islami", 15, TEXT, 700) + crescent + rows


def shop_screen():
    tiles = "".join(
        f'<rect x="{12 + col * 62}" y="{44 + row * 92}" width="54" height="54" rx="10" fill="#13233a"/>'
        f'<circle cx="{39 + col * 62}" cy="{71 + row * 92}" r="14" fill="{color}"/>'
        + bars(12 + col * 62, 104 + row * 92, [44], step=0)
        + f'<rect x="{12 + col * 62}" y="{115 + row * 92}" width="26" height="7" rx="3.5" fill="{CYAN}"/>'
        for row, colors in enumerate((("#f76b15", "#3e63dd"), ("#e93d82", "#30a46c")))
        for col, color in enumerate(colors)
    )
    return text(12, 32, "Shop", 15, TEXT, 700) + tiles


def hero(user):
    calendar = user["contributionsCollection"]["contributionCalendar"]
    active_days = sum(
        1 for week in calendar["weeks"] for day in week["contributionDays"] if day["contributionCount"]
    )
    stats = [
        (f'{calendar["totalContributions"]:,}', "CONTRIBUTIONS"),
        (user["repositories"]["totalCount"], "PUBLIC REPOS"),
        (active_days, "ACTIVE DAYS"),
    ]
    width, height = 860, 340
    cycle = len(TYPED_LINES) * 4
    style = f"""<style>
@keyframes drift{{from{{transform:translate(-30px,-16px)}}to{{transform:translate(50px,26px)}}}}
@keyframes rise{{from{{opacity:0;transform:translateY(16px)}}to{{opacity:1;transform:none}}}}
@keyframes bob{{from{{transform:translateY(-6px)}}to{{transform:translateY(6px)}}}}
@keyframes type{{0%{{opacity:1;clip-path:inset(-4px 100% -8px 0)}}10%{{opacity:1;clip-path:inset(-4px 0 -8px 0)}}22%{{opacity:1;clip-path:inset(-4px 0 -8px 0)}}25%,100%{{opacity:0;clip-path:inset(-4px 0 -8px 0)}}}}
@keyframes screen{{0%,30%{{opacity:1}}34%,96%{{opacity:0}}100%{{opacity:1}}}}
.blob{{animation:drift 9s ease-in-out infinite alternate}}
.b2{{animation-duration:12s;animation-direction:alternate-reverse}}
.rise{{animation:rise .8s cubic-bezier(.2,.8,.2,1) both}}
.phone{{animation:bob 3.5s ease-in-out infinite alternate}}
.line{{opacity:0}}.l0{{opacity:1}}
.screen{{opacity:0;animation:screen 12s linear infinite}}.s0{{opacity:1}}
{REDUCED}</style>"""
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="{SANS}" role="img" aria-label="{FIRST_NAME} {LAST_NAME}, Flutter Developer">',
        style,
        f'<defs><clipPath id="frame"><rect width="{width}" height="{height}" rx="20"/></clipPath>'
        '<clipPath id="display"><rect x="0" y="0" width="140" height="272" rx="20"/></clipPath>'
        f'<radialGradient id="c1"><stop offset="0" stop-color="{CYAN}" stop-opacity=".30"/><stop offset="1" stop-color="{CYAN}" stop-opacity="0"/></radialGradient>'
        f'<radialGradient id="c2"><stop offset="0" stop-color="{BLUE}" stop-opacity=".38"/><stop offset="1" stop-color="{BLUE}" stop-opacity="0"/></radialGradient>'
        f'<linearGradient id="name" x1="0" x2="1"><stop offset="0" stop-color="{CYAN}"/><stop offset="1" stop-color="{BLUE}"/></linearGradient></defs>',
        f'<g clip-path="url(#frame)"><rect width="{width}" height="{height}" fill="{BG}"/>',
        '<circle class="blob" cx="150" cy="50" r="260" fill="url(#c1)"/>',
        '<circle class="blob b2" cx="690" cy="300" r="300" fill="url(#c2)"/></g>',
        f'<rect x=".5" y=".5" width="{width - 1}" height="{height - 1}" rx="20" fill="none" stroke="{BORDER}"/>',
        '<g class="rise">' + text(48, 58, "HELLO, I BUILD MOBILE APPS", 13, CYAN, 600, f'font-family="{MONO}" letter-spacing="2"') + "</g>",
        '<g class="rise" style="animation-delay:.12s">' + text(46, 122, FIRST_NAME, 64, TEXT, 800, 'letter-spacing="-1.5"') + "</g>",
        '<g class="rise" style="animation-delay:.24s">' + text(46, 186, LAST_NAME, 64, "url(#name)", 800, 'letter-spacing="-1.5"') + "</g>",
    ]
    for index, line in enumerate(TYPED_LINES):
        timing = (
            f"animation:type {cycle}s steps({len(line) * 3},end) {index * 4}s infinite both"
        )
        parts.append(
            f'<text class="line l{index}" x="48" y="228" font-size="18" fill="{MUTED}" '
            f'font-family="{MONO}" style="{timing}">{escape("> " + line)}</text>'
        )
    for index, (value, label) in enumerate(stats):
        x = 48 + index * 150
        parts.append(
            f'<g class="rise" style="animation-delay:{.4 + index * .1:.1f}s">'
            + text(x, 284, value, 28, TEXT, 700)
            + text(x, 306, label, 11, MUTED, 600, 'letter-spacing="1.2"')
            + "</g>"
        )
    parts.append(
        '<g transform="translate(652 28)"><g class="phone">'
        f'<rect x="-8" y="-8" width="156" height="296" rx="28" fill="#111a29" stroke="#34445c" stroke-width="1.5"/>'
        '<rect width="140" height="272" rx="20" fill="#0b1626"/><g clip-path="url(#display)">'
    )
    for index, screen in enumerate((movie_screen, islami_screen, shop_screen)):
        parts.append(f'<g class="screen s{index}" style="animation-delay:{index * 4}s">{screen()}</g>')
    parts.append('<rect x="50" y="8" width="40" height="9" rx="4.5" fill="#000"/></g></g></g></svg>')
    return "".join(parts)


def project_card(repo, description, index):
    width, height = 420, 180
    # Clear space under the last row separates the cards from the links below.
    canvas = height + (14 if index >= len(PROJECTS) - 2 else 0)
    language = repo["primaryLanguage"] or {"name": "Code", "color": MUTED}
    style = f"""<style>
@keyframes comet{{from{{stroke-dashoffset:0}}to{{stroke-dashoffset:-100}}}}
.comet{{animation:comet 6s linear infinite;animation-delay:{-index * 1.5}s}}
{REDUCED}</style>"""
    title_size = 30 if len(repo["name"]) <= 16 else 25
    return "".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {canvas}" width="{width}" height="{canvas}" '
            f'font-family="{SANS}" role="img" aria-label="{escape(repo["name"])}: {escape(description)}">',
            style,
            f'<rect x="1" y="1" width="{width - 2}" height="{height - 2}" rx="16" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
            f'<rect class="comet" x="1" y="1" width="{width - 2}" height="{height - 2}" rx="16" fill="none" stroke="{CYAN}" '
            'stroke-width="2" stroke-linecap="round" pathLength="100" stroke-dasharray="14 86"/>',
            text(28, 62, repo["name"], title_size, TEXT, 700, 'letter-spacing="-.4"'),
            text(28, 98, description, 18, MUTED),
            f'<circle cx="35" cy="142" r="7" fill="{escape(language["color"] or MUTED)}"/>',
            text(50, 148, language["name"], 17, TEXT, 500),
            text(width - 28, 148, f'★ {repo["stargazerCount"]}', 17, MUTED, 500, 'text-anchor="end"'),
            text(width - 28, 58, "↗", 24, CYAN, 600, 'text-anchor="end"'),
            "</svg>",
        ]
    )


def stack_strip():
    width, height, size, step = 860, 96, 56, 84
    track = step * len(STACK)
    defs, row = [], []
    for index, name in enumerate(STACK):
        request = urllib.request.Request(f"https://skillicons.dev/icons?i={name}", headers={"User-Agent": "profile-images"})
        with urllib.request.urlopen(request, timeout=30) as response:
            encoded = base64.b64encode(response.read()).decode()
        defs.append(f'<image id="i{index}" href="data:image/svg+xml;base64,{encoded}" width="{size}" height="{size}"/>')
        row.append(f'<use href="#i{index}" x="{index * step}" y="20"/>')
    icons = "".join(row)
    return "".join(
        [
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" role="img" '
            f'aria-label="Tech stack: {", ".join(STACK)}">',
            f"<style>@keyframes slide{{to{{transform:translateX(-{track}px)}}}}.track{{animation:slide 26s linear infinite}}{REDUCED}</style>",
            "<defs>" + "".join(defs),
            '<linearGradient id="fade"><stop offset="0" stop-color="#fff" stop-opacity="0"/><stop offset=".08" stop-color="#fff"/>'
            '<stop offset=".92" stop-color="#fff"/><stop offset="1" stop-color="#fff" stop-opacity="0"/></linearGradient>',
            f'<mask id="edges" maskUnits="userSpaceOnUse" x="0" y="0" width="{width}" height="{height}"><rect width="{width}" height="{height}" fill="url(#fade)"/></mask></defs>',
            f'<rect x=".75" y=".75" width="{width - 1.5}" height="{height - 1.5}" rx="16" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
            f'<g mask="url(#edges)"><g class="track"><g>{icons}</g><g transform="translate({track})">{icons}</g></g></g>',
            "</svg>",
        ]
    )


def calendar_card(calendar, snake_svg):
    """Frame the snake generated by Platane/snk in a titled card with month and day labels."""
    width, height, grid_x, grid_y = 860, 228, 62, 70
    scale = (width - grid_x - 28) / 848  # snk draws 53 columns at 16 units each
    step = 16 * scale
    weeks = calendar["weeks"][-53:]
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}" '
        f'font-family="{SANS}" role="img" aria-label="Snake eating a contribution calendar: {calendar["totalContributions"]} contributions in the last year">',
        f'<rect x=".75" y=".75" width="{width - 1.5}" height="{height - 1.5}" rx="16" fill="{CARD}" stroke="{BORDER}" stroke-width="1.5"/>',
        text(28, 34, "CONTRIBUTION CALENDAR", 12, MUTED, 600, 'letter-spacing="1.2"'),
        text(width - 28, 34, f'{calendar["totalContributions"]:,} in the last year', 13, TEXT, 600, 'text-anchor="end"'),
    ]
    for row, label in ((1, "Mon"), (3, "Wed"), (5, "Fri")):
        parts.append(text(28, round(grid_y + row * step + 10, 1), label, 11, MUTED))
    previous = None
    for column, week in enumerate(weeks):
        first = week["contributionDays"][0]["date"]
        month = first[:7]
        # Skip a label for a first column that holds only the tail of a month.
        if month != previous and (previous or first[8:] <= "07") and column < len(weeks) - 2:
            label = date(int(month[:4]), int(month[5:]), 1).strftime("%b")
            parts.append(text(round(grid_x + column * step, 1), 58, label, 11, MUTED))
        previous = month
    # Inline, because an SVG loaded as an image inside another image would not animate reliably.
    inner = snake_svg.replace(
        "<svg ",
        f'<svg x="{grid_x - 16 * scale:.1f}" y="{grid_y - 32 * scale:.1f}" ',
        1,
    )
    inner = re.sub(r'(<svg [^>]*?) width="880" height="192"', rf'\1 width="{880 * scale:.1f}" height="{192 * scale:.1f}"', inner, 1)
    parts.extend([inner, "</svg>"])
    return "".join(parts)


def main():
    user = fetch()
    ASSETS.mkdir(parents=True, exist_ok=True)
    snake = ROOT / "dist" / "snake.svg"
    if snake.exists():  # Produced by the workflow step that runs before this script.
        (ASSETS / "calendar.svg").write_text(
            calendar_card(user["contributionsCollection"]["contributionCalendar"], snake.read_text(encoding="utf-8")),
            encoding="utf-8",
        )
    (ASSETS / "hero.svg").write_text(hero(user), encoding="utf-8")
    repos = {repo["name"]: repo for repo in user["repositories"]["nodes"]}
    for index, (name, description) in enumerate(PROJECTS):
        (ASSETS / f"project-{index + 1}.svg").write_text(project_card(repos[name], description, index), encoding="utf-8")
    (ASSETS / "stack.svg").write_text(stack_strip(), encoding="utf-8")
    print("Wrote images to", ASSETS)


if __name__ == "__main__":
    main()
