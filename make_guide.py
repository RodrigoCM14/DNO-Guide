from pathlib import Path


src = Path("newbie-guide-extracted.txt")
text = src.read_text(encoding="utf-8")

replacements = {
    "â€œ": '"',
    "â€\x9d": '"',
    "â€˜": '"',
    "â€™": "'",
    "â€“": "-",
    "â€”": "-",
    "â€": '"',
    "“": '"',
    "”": '"',
    "‘": "'",
    "’": "'",
    "–": "-",
    "—": "-",
    "Ê£": "1.",
    "Ê¤": "2.",
    "Ê¥": "3.",
    "Ê¦": "4.",
    "Ê§": "5.",
    "ʣ": "1.",
    "ʤ": "2.",
    "ʥ": "3.",
    "ʦ": "4.",
    "ʧ": "5.",
    "\u00a0": " ",
    "---------------------------------------------------------------------------------------------------------------------------------------------------": "---",
}

for old, new in replacements.items():
    text = text.replace(old, new)

text = text.replace("Dats Centre", "Dats Center")
lines = [line.rstrip() for line in text.splitlines()]

out = [
    "# Digital Nexus Online Newbie Guide",
    "",
    "Source: `Newbie Guide [Extensive].pdf` (26 pages).",
    "",
    (
        "This is a first-pass Markdown conversion of the PDF. The text has been "
        "cleaned for encoding artifacts and organized into editable source form, "
        "while preserving the original guide content for review."
    ),
    "",
    "## Working Table of Contents",
    "",
    "- General information and map unlocking",
    "- General leveling",
    "- Main material farming",
    "- Burst Ultimate Wings deck buff",
    "- Early to mid game progression",
    "- Active route: Omegamon X, Fanglongmon Shin, and accessories",
    "- AFK route: Omegamon Merciful Mode",
    "- Mid game to late game",
    "- VIP grind",
    "- P.W. Lost Historic Site and P.W. Armagedomon",
    "- Quick guide summary",
    "",
    "## Quick Progression Summary",
    "",
    "1. Get 70 Digimon in Archive.",
    "2. Get Alphamon Ouryuken Extreme and raise it to T10.",
    "3. Get Omegamon X and raise it to T10.",
    "4. Get all Max Fanglongmon Ancient Accessories.",
    "5. Get Omegamon X Awaken (Black) and raise it to T10.",
    "6. Get Fanglongmon Ruin Mode and raise it to T10.",
    "7. Reach VIP 5.",
    "8. Get P.W. Armagedomon.",
    "",
    (
        "Expected time from start to completion in the source guide: "
        "**136 hours and 9 minutes**."
    ),
    "",
    "## Converted Source Draft",
    "",
]

section_titles = {
    "Hello and welcome": "Introduction",
    "General Information :": "General Information",
    "Progression Guide :": "Progression Guide",
    "1.  Accessibility (Map Unlocking)": "Accessibility: Map Unlocking",
    "2.  General Leveling": "General Leveling",
    "3.  Main Material Farms": "Main Material Farms",
    "4.  Getting the Deck Buff : Burst Ultimate Wings (BUW)": (
        "Getting the Deck Buff: Burst Ultimate Wings (BUW)"
    ),
    "5.  From Early Game to Mid Game Progression": (
        "From Early Game to Mid Game Progression"
    ),
    "From Mid Game to Late Game": "From Mid Game to Late Game",
    "The VIP Grind Begins": "The VIP Grind Begins",
    "Normal Dungeon Grind (AFK Route only)": "Normal Dungeon Grind (AFK Route Only)",
    "To Lost Historic Site and Late Game!": "To Lost Historic Site and Late Game",
    "Quick Guide Summation :": "Quick Guide Summary",
}

for line in lines:
    stripped = line.strip()
    if not stripped:
        out.append("")
        continue
    if stripped.startswith("--- PAGE"):
        page = stripped.replace("---", "").strip()
        out.append(f"<!-- {page} -->")
        continue
    if stripped in section_titles:
        out.extend(["", f"## {section_titles[stripped]}", ""])
        continue
    if (
        stripped.endswith(":")
        and len(stripped) < 90
        and not stripped.startswith("Note")
        and not stripped.startswith("Requirements")
    ):
        out.extend(["", f"### {stripped[:-1].strip()}", ""])
        continue
    out.append(stripped)

clean = []
blank_count = 0
for line in out:
    if line == "":
        blank_count += 1
        if blank_count <= 2:
            clean.append(line)
    else:
        blank_count = 0
        clean.append(line)

Path("DNO_Newbie_Guide.md").write_text("\n".join(clean).strip() + "\n", encoding="utf-8")
print(f"wrote DNO_Newbie_Guide.md ({len(clean)} lines)")
