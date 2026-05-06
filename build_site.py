from __future__ import annotations

import html
import json
import re
import shutil
from pathlib import Path


ROOT = Path(__file__).parent
SOURCE = ROOT / "DNO_Newbie_Guide.md"
PUBLIC = ROOT / "site"
PAGES = ROOT / "docs"
ASSETS = ROOT / "assets"


def slugify(value: str, used: set[str]) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    slug = slug or "section"
    base = slug
    index = 2
    while slug in used:
        slug = f"{base}-{index}"
        index += 1
    used.add(slug)
    return slug


def inline_markup(text: str) -> str:
    escaped = html.escape(text)
    escaped = re.sub(r"`([^`]+)`", r"<code>\1</code>", escaped)
    escaped = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", escaped)
    escaped = re.sub(
        r"(\[Note[^:\]]*\s*[-:][^\]]+\])",
        r"<em>\1</em>",
        escaped,
        flags=re.IGNORECASE,
    )
    escaped = re.sub(
        r"(\[Important[^\]]+\])|(?<!\[)(Important\s*[-:][^.]+)",
        lambda match: f"<strong>{match.group(1) or match.group(2)}</strong>",
        escaped,
        flags=re.IGNORECASE,
    )
    escaped = re.sub(
        r"(\[[^\[\]]+\])",
        r'<span class="bracketed">\1</span>',
        escaped,
    )
    escaped = re.sub(
        r"(\([^()]+\))",
        r'<span class="parenthetical">\1</span>',
        escaped,
    )
    return escaped


def clean_source_text(text: str) -> str:
    replacements = {
        "Aswell": "As well",
        "Infinte": "Infinite",
        "Sroll": "Scroll",
        "Ouryken": "Ouryuken",
        "KasierGreymon": "KaiserGreymon",
        "Sussanomon": "Susanoomon",
        "Cranimon": "Craniamon",
        "DigiEggs": "DigiEggs",
        "Ill-advised": "ill-advised",
        "atleast": "at least",
        "Digimon's": "Digimon",
        "dungeon's": "dungeons",
        "Dungeon's": "Dungeons",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    text = re.sub(r"(?m)^(\d+)\s+\)\s+", r"\1. ", text)
    text = re.sub(r"\s+:", ":", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    return text


def close_list(out: list[str], list_state: str | None) -> str | None:
    if list_state:
        out.append(f"</{list_state}>")
    return None


def split_marked_items(text: str, markers: list[str]) -> list[str]:
    pattern = r"(?=(" + "|".join(re.escape(marker) for marker in markers) + r"))"
    return [part.strip() for part in re.split(pattern, text) if part.strip()]


def render_ul(items: list[str], class_name: str = "structured-list") -> str:
    rows = [f"<li>{inline_markup(item)}</li>" for item in items if item.strip()]
    return f'<ul class="{class_name}">' + "".join(rows) + "</ul>"


def render_table(headers: list[str], rows: list[list[str]], class_name: str = "data-table") -> str:
    head = "".join(f"<th>{html.escape(header)}</th>" for header in headers)
    body = "".join(
        "<tr>" + "".join(f"<td>{inline_markup(cell)}</td>" for cell in row) + "</tr>"
        for row in rows
    )
    return f'<table class="{class_name}"><thead><tr>{head}</tr></thead><tbody>{body}</tbody></table>'


def render_static_table(headers: list[str], rows: list[list[str]], class_name: str = "overview-table") -> str:
    return render_table(headers, rows, class_name)


def render_overview() -> str:
    map_unlocks = render_static_table(
        ["Map / Area", "Access", "Requirement"],
        [
            ["Oil Refinery 1, 2, 3", "Portal Guide Oil Refinery Employee in Yokohama Village: East", "Level 12 Tamer"],
            ["D-Terminal B1/B2", "Kevin Krier in Dats Center", "Complete Richard Sampson sub quest"],
            ["Snowstorm Village", "Miki in D-Terminal", "Level 20 Tamer and 20M"],
            ["Village of the Beginning", "Elecmon in D-Terminal", "20M teleport cost"],
            ["Western Village: West", "Cerberusmon in Western Village", "Level 55 Tamer"],
            ["Digimon Maze Entrance", "Starmon in Dark Tower Wasteland", "Urgent Request sub quest at level 55 Tamer"],
            ["Infinite Mountain Dungeon", "Elecmon in Infinite Mountain", "Complete Lost Historic Site and File Island Waterfront main quests"],
            ["Server Continent Desert", "Raft near Gennai in File Island Waterfront", "Main quests unlocked after Infinite Mountain Dungeon access"],
            ["Campsite / Tokyo-Odaiba", "Odaiba, White-Beared Guru in D-Terminal", "1 Tera"],
            ["Shinjuku Western: Day", "DAT Member PawnChessmon W in D-Terminal", "10 Tera"],
            ["Verdandi Terminal", "Verdandi T. / Digimon Lv 99+ Mary in D-Terminal", "First-slot Digimon level 99"],
        ],
    )
    farming_routes = render_static_table(
        ["Route", "Primary Goal", "Key Drops / Rewards", "Notes"],
        [
            ["Lost Historic Site cards", "Fast Tera and early materials", "SS5/SS6, accelerators, BM boxes, villain boxes", "Use AoE farmer plus Lillymon AA attacker"],
            ["Server Continent cards", "Tera, fruit, mid data", "SS9/SS10, Fruit of Yggdrasil, Mid Data Boxes", "Good repeatable farm after Server Continent access"],
            ["Villain Box loop", "True Bulk Fruit and upgrade materials", "Bulk Fruit, OCS, NCS, seal openers, clone boxes", "Best once Super Villain cards are manageable"],
            ["Adventure Beach crests", "Omegamon Merciful Mode route", "Daily crest types by weekday", "AFK-friendly route; target 6,000 of each crest"],
        ],
    )
    milestones = render_static_table(
        ["Milestone", "Target", "Primary Source", "Estimated Time / Gate"],
        [
            ["Archive setup", "70 Digimon in Archive", "Hatching and unlocking lines", "Unlocks stronger archive scaling and route choices"],
            ["Alphamon Ouryuken Extreme", "T10 and 75/75 clones", "Royal Base Easy and Nexus Coins", "About 9h 45m at 1 min per boss"],
            ["Omegamon X", "T10 and 75/75 clones", "Finest Mysterious X-Antibody Factor Omegamon X", "RNG from Royal Base Easy boxes"],
            ["Max Fanglongmon Ancient Accessories", "Necklace, ring, earring", "Normal Points through Fanglongmon Normal", "About 11h 40m at 4 min FDGN runs"],
            ["Omegamon X Awaken (Black)", "640 containers", "Yggdrasil's Room", "About 42h 40m at 4 min runs"],
            ["Fanglongmon Ruin Mode", "4 Black Hearts", "Fanglongmon Hard / Yin and Yang boxes", "About 13h 54m at 1 min runs"],
            ["VIP 5", "50,000 VIP Points", "Fanglongmon Hard", "About 30h 24m total from VIP 0"],
            ["P.W. Armagedomon", "2,500 Lost Historic Site boxes", "P.W. Lost Historic Site / Invade", "Final late-game milestone"],
        ],
    )
    dungeon_routes = render_static_table(
        ["Dungeon / Route", "Purpose", "Recommended Focus", "Important Note"],
        [
            ["Royal Base Easy", "Easy Points, Nexus Coins, Alphamon route", "Clear six bosses through NPC rooms", "Each boss gives VIP points"],
            ["Fanglongmon Normal", "Normal Points and Fanglongmon Shin boxes", "Farm 2,100 Normal Points", "Best early accessory progression"],
            ["Yggdrasil's Room", "Omegamon X Awaken (Black)", "Save 640 containers for pity", "Do not open containers early"],
            ["Fanglongmon Hard", "VIP grind and Fanglongmon Ruin Mode", "Farm Hard Points and Yin/Yang boxes", "VIP increases point gain and field drops"],
            ["P.W. Lost Historic Site", "P.W. Armagedomon and endgame boxes", "Choose route by party attribute", "Party strongly recommended"],
        ],
    )
    return f"""
        <section class="overview" id="guide-overview">
          <div class="overview-head">
            <p class="eyebrow">Clean Player View</p>
            <h2>Guide Overview</h2>
            <p>Use these tables for quick decisions, then jump into the detailed guide below for the full route instructions.</p>
          </div>
          <div class="callout-grid">
            <div class="callout important-callout"><strong>Important:</strong> Server Continent completion rewards are especially valuable because they include the Palmon [Origin] egg route.</div>
            <div class="callout warning-callout"><strong>Warning:</strong> Save pity-based dungeon boxes when the guide says not to open them early.</div>
            <div class="callout time-callout"><strong>Time plan:</strong> The original guide estimates 136 hours and 9 minutes from start to completion.</div>
          </div>
          <section class="overview-block" id="map-unlocks-table">
            <h3>Map Unlocks</h3>
            {map_unlocks}
          </section>
          <section class="overview-block" id="farming-routes-table">
            <h3>Farming Routes</h3>
            {farming_routes}
          </section>
          <section class="overview-block" id="progression-milestones-table">
            <h3>Progression Milestones</h3>
            {milestones}
          </section>
          <section class="overview-block" id="dungeon-routes-table">
            <h3>Dungeon Routes</h3>
            {dungeon_routes}
          </section>
        </section>
    """


def split_known_sequence(text: str, starters: list[str]) -> list[str]:
    positions = []
    for starter in starters:
        index = text.find(starter)
        if index != -1:
            positions.append((index, starter))
    positions.sort()
    items = []
    for idx, (start, _) in enumerate(positions):
        end = positions[idx + 1][0] if idx + 1 < len(positions) else len(text)
        item = text[start:end].strip(" ,")
        if item:
            items.append(item)
    return items


def render_structured_block(section_id: str, text: str, class_name: str) -> str | None:
    if class_name not in {"guide-line", "note", "important", "time-estimate"}:
        return None

    if text == "Digimon Enhancement Buff Package -":
        return '<p class="section-label">Digimon Enhancement Buff Package</p>'

    data_markers = [
        "Beast Data:",
        "Dragon Data:",
        "Fire Data:",
        "Bird Data:",
        "Devil Data:",
        "Plant Data:",
        "Rock Data:",
        "Insectoid Data:",
        "Aquatic Data:",
    ]
    if any(marker in text for marker in data_markers) and "Data:" in text:
        items = split_known_sequence(text, data_markers)
        rows = []
        for item in items:
            label, _, value = item.partition(":")
            rows.append([label.strip(), value.strip()])
        return render_table(["Data Type", "Farm Location"], rows)

    if section_id == "claim-map-completion-rewards":
        markers = [
            "Wester Area Rewards",
            "File Island Area Rewards",
            "Glacier Area Rewards",
            "Server Continent Area Rewards",
        ]
        if any(marker in text for marker in markers):
            rows = []
            for item in split_known_sequence(text, markers):
                label, _, rewards = item.partition("-")
                rows.append([label.strip(), rewards.strip()])
            return render_table(["Area", "Completion Rewards"], rows)

    if "Ensure auto pickup is enabled for the following items:" in text:
        before, _, after = text.partition("Ensure auto pickup is enabled for the following items:")
        quoted = re.findall(r'"([^"]+)"', after)
        remaining = re.sub(r'"[^"]+"', "", after)
        loose = [
            item.strip()
            for item in re.split(r"(?=Respective Farming Mob|450B DigiEgg)", remaining)
            if item.strip()
        ]
        items = loose + quoted
        if not items:
            return f'<p class="{class_name}">{inline_markup(before + "Ensure auto pickup is enabled for the following items:")}</p>'
        return (
            f'<p class="{class_name}">{inline_markup(before + "Ensure auto pickup is enabled for the following items:")}</p>'
            + render_ul(items)
        )

    if section_id == "choose-the-right-card-trades":
        items = [
            item.strip()
            for item in re.split(r"(?=\b(?:5|6|7|8|9|10|11,12,13,14,15)\s*->)", text)
            if item.strip()
        ]
        if len(items) > 1:
            return render_ul(items, "sequence-list")

    if section_id == "recycle-stones-for-more-boxes" and "%" in text:
        markers = [
            "58.08% of Original Box Amount",
            "Super Villain level 5 Cards",
            "Super Villain level 4 Cards",
            "Super Villain level 3 Cards",
            "Super Villain level 2 Cards",
            "Average Number",
        ]
        items = split_known_sequence(text, markers)
        if len(items) > 1:
            return render_ul(items)

    if text.startswith("Digimon Boost -"):
        markers = [
            "Digimon Boost - Critical Attack 100",
            "Digimon Boost - Skill Damage 100",
            "Digimon Boost - Max DS 50",
            "Digimon Boost - Max HP 50",
            "Digimon Boost - Attack 50",
            "Digimon Boost - Hit Rate 500",
            "Digimon Boost - Evade 500",
        ]
        buffs = split_known_sequence(text, markers)
        tail_start = text.find("Always Use")
        tail = text[tail_start:].strip() if tail_start != -1 else ""
        return render_ul(buffs) + (f'<p class="important">{inline_markup(tail)}</p>' if tail else "")

    seal_rows = re.findall(r"(\d+)\s+Seal\s*-\s*(\d+)% Stats Obtained\s*\[(\d+) Openers? Needed\]", text)
    if section_id == "open-seals-for-permanent-stats" and seal_rows:
        table = render_table(
            ["Seals", "Stats Obtained", "Openers Needed"],
            [[seal, f"{stat}%", openers] for seal, stat, openers in seal_rows],
        )
        tail = re.sub(r"\d+\s+Seal\s*-\s*\d+% Stats Obtained\s*\[\d+ Openers? Needed\]", "", text).strip()
        return table + (f'<p class="guide-line">{inline_markup(tail)}</p>' if tail else "")

    buw_markers = [
        "Sodom and Gomorrah:",
        "Omega Blade:",
        "Gehenna:",
        "Gungnir:",
        "Holy Wing:",
        "Ornis Wing:",
        "Tyrant Claw:",
        "Dramon Breaker:",
    ]
    if any(marker in text for marker in buw_markers):
        return render_ul(split_known_sequence(text, buw_markers))

    if '"Kudamon" NPC' in text:
        markers = ['"Kudamon" NPC', '"Candlemon" NPC', '"Harugumon" NPC', '"Dracomon" NPC', '"Gladimon" NPC', '"Veemon" NPC']
        items = split_known_sequence(text, markers)
        cleaned = []
        for item in items:
            item = item.replace("Each Boss Gives 4 VIP Points Each", "").strip()
            if item:
                cleaned.append(item)
        return render_ul(cleaned)

    if section_id == "spend-extra-easy-points-wisely":
        items = split_known_sequence(text, ["DS Attribute Rank C LvMax", "AT Attribute Rank C LvMax"])
        if len(items) > 1:
            return render_ul(items)

    if section_id == "as-well-as-other-important-items-from-the-craniamon-x-npc-using-nexus-coins-such-as":
        markers = [
            "Jogress Data B-",
            "Jogress Data A-",
            "Exchange Tamer Box Adventure",
            "Random Tamer Skill Box",
            "65 Digimon Archive Slots",
        ]
        items = split_known_sequence(text, markers)
        if len(items) > 1:
            return render_ul(items)

    if section_id.startswith("roll-the-recommended-accessory-stats"):
        stat_markers = [
            "Max Fanglongmon Ancient Necklace",
            "Max Fanglongmon Ancient Ring",
            "Max Fanglongmon Ancient Earring",
        ]
        if any(marker in text for marker in stat_markers):
            return render_ul(split_known_sequence(text, stat_markers))
        upgrade_markers = [
            "Accessory Upgrade Items",
            "High Rank Digitary Power Stone",
            "Amazing Digitary Power Stone",
            "Digitary Power Stone",
            "Amazing Renewal Increase Stones",
            "High Rank Renewal Increase Stone",
            "Option Change Stones",
            "Number Change Stones",
        ]
        if any(marker in text for marker in upgrade_markers):
            items = split_known_sequence(text, upgrade_markers)
            if items and items[0] == "Accessory Upgrade Items":
                items = items[1:]
            return render_ul(items)

    if section_id == "follow-the-weekly-crest-schedule":
        days = ["Monday:", "Tuesday:", "Wednesday:", "Thursday:", "Friday:", "Saturday:", "Sunday:"]
        items = split_known_sequence(text, days)
        if len(items) > 1:
            return render_ul(items)

    if section_id == "plan-your-vip-dungeon-runs":
        items = [
            item.strip()
            for item in re.split(r"(?=VIP \d to VIP \d)", text)
            if item.strip()
        ]
        if len(items) > 1:
            return render_ul(items)

    boss_markers = [
        "Imperialdramon Fighter Mode",
        "Omegamon Merciful Mode",
        "Rafflesimon",
        "Zeed Millenniummon",
        "(Raid) Slash Angemon",
        "DANGER",
        "Fanglongmon (Shin)",
        "Valkyrimon",
        "Death-X-Mon",
        "(Fear) Omegamon Anti-Nexus",
        "(Absolute Light) Imperialdramon Paladin Mode",
        "(Raid Boss) Kuzuhamon",
        "Omegamon Alter-S",
        "(Ruin Mode) Fanglongmon",
        "(Dark Side) Omegamon Alter-B",
        "Omegamon X",
        "Omegamon Zwart-D",
        "Omegamon Nexus",
        "(Lucemon X's Follower) Barbamon X",
        "Susanoomon (Shin)",
    ]
    route_sections = {
        "follow-the-full-boss-route",
        "run-the-va-party-route",
        "run-the-vi-party-route",
        "run-the-da-party-route",
        "run-the-steel-weakness-route",
    }
    if section_id in route_sections and any(marker in text for marker in boss_markers):
        items = split_known_sequence(text, boss_markers)
        if len(items) > 1:
            return render_ul(items, "boss-list")

    return None


def display_title(title: str) -> str:
    replacements = {
        "Quick Progression Summary": "Follow the full progression path",
        "The Following Sections will be included": "Preview what this section covers",
        "Introduction": "Start here",
        "Accessibility: Map Unlocking": "Unlock maps and travel routes",
        "Map Completion Rewards": "Claim map completion rewards",
        "General Leveling": "Find the best leveling spots",
        "Best Leveling Spots": "Pick a leveling location",
        "Example AoE Digimon Leveling Setup": "Set up AoE leveling",
        "Getting the Deck Buff: Burst Ultimate Wings (BUW)": "Build the BUW deck buff",
        "BUW Digimon Checklist": "Level the BUW Digimon",
        "Main Material Farms": "Farm core materials",
        "Lost Historic Site Method": "Farm Tera at Lost Historic Site",
        "Server Continent Method": "Farm Tera at Server Continent",
        "Data Collection": "Collect hatch data",
        "Data Farming Spots": "Farm specific data types",
        "Lost Historic Site/Server Continent Card Guide Summation": "Choose the right card trades",
        "Villain Boxes Provides important Items such as": "Use Villain Box rewards",
        "Average % Number of Boxes obtained from Recycling Obtained Summoning Stones": "Recycle stones for more boxes",
        "Enhancement Buff Sources": "Get enhancement buff boxes",
        "Enhancement Buff List": "Use your enhancement buffs",
        "Seal Master Exchange Ticket - Can be obtained through the following": "Collect Seal Master tickets",
        "Number of Seals needed to unlock the stats": "Open seals for permanent stats",
        "From Early Game to Mid Game Progression": "Begin early-to-mid progression",
        "Once you have obtained 70 Digimon in your Archives": "Route Split: 70 Digimon Archive",
        "Route Split: 70 Digimon Archive": "Choose your route at 70 archives",
        "6. For Alphamon Ouryuken X, You will need": "Alphamon Ouryuken X Requirements",
        "Alphamon Ouryuken X Requirements": "Unlock Alphamon Ouryuken X",
        "7. For Alphamon Ouryuken X Awaken, You will need": "Alphamon Ouryuken X Awaken Requirements",
        "Alphamon Ouryuken X Awaken Requirements": "Upgrade to Alphamon X Awaken",
        "8. For Alphamon Ouryuken Extreme, You will need": "Alphamon Ouryuken Extreme Requirements",
        "Alphamon Ouryuken Extreme Requirements": "Finish Alphamon X Extreme",
        "Utilize the Easy Points on other important items at the Alphamon NPC such as": "Easy Points Priorities",
        "Easy Points Priorities": "Spend extra Easy Points wisely",
        "Aswell as Other important Items from the Craniamon X NPC using Nexus Coins Such as": "Nexus Coin Priorities",
        "Nexus Coin Priorities": "Spend Nexus Coins wisely",
        "The only Dungeon's that break this rule is": "Normal Dungeon Rank Exceptions",
        "Normal Dungeon Rank Exceptions": "Know the Normal dungeon exceptions",
        "Fanglongmon Shin Requires 4 Evolution Items": "Unlock Fanglongmon Shin",
        "Stat Recommendations": "Roll the recommended accessory stats",
        "Part 1": "Start the AFK route",
        "Kunemon Mercenary Eggs can either be farmed": "Farm three Kunemon",
        "Part 2": "Farm Adventure Beach crests",
        "The Crest Schedule will be down below": "Follow the weekly crest schedule",
        "One you have completed the 14 Day Crest Farm": "After the 14 Day Crest Farm",
        "After the 14 Day Crest Farm": "Finish the 14-day crest route",
        "9. For Omegamon Merciful Mode, You will need": "Omegamon Merciful Mode Requirements",
        "Omegamon Merciful Mode Requirements": "Unlock Omegamon Merciful Mode",
        "From Mid Game to Late Game": "Move into late-game goals",
        "The VIP Grind Begins": "Start the VIP grind",
        "The Following Completion Rewards for the Maps are": "Map Completion Rewards",
        "The following are the best spots": "Best Leveling Spots",
        "following Digimon to level 70 and unlocking their Burst Mode Evolutions": "BUW Digimon Checklist",
        "To Get Data, You can either": "Data Collection",
        "Below is a list of some spots that drop their data": "Data Farming Spots",
        "Can be obtained in large quantities by either": "Enhancement Buff Sources",
        "Buffs obtained once opened": "Enhancement Buff List",
        "Once defeated, Fanglongmon (Ruin Mode) will give": "Fanglongmon Hard Rewards",
        "Fanglongmon Hard Rewards": "Farm Fanglongmon Hard rewards",
        "Below will be the Required number of Fanglongmon Hard Dungeon runs for Each VIP level": "VIP Run Requirements",
        "VIP Run Requirements": "Plan your VIP dungeon runs",
        "You will also get the ability to Unlock Fanglongmon Ruin, This can be done by": "Unlock Fanglongmon Ruin Mode",
        "Unlock Fanglongmon Ruin Mode": "Unlock Fanglongmon Ruin Mode",
        "Normal Dungeon Grind (AFK Route Only)": "Catch up on Normal dungeon gear",
        "The best Normal Dungeons to farm are": "Best Normal Dungeon Farms",
        "Best Normal Dungeon Farms": "Choose a Normal dungeon farm",
        "To Lost Historic Site and Late Game": "Enter P.W. Lost Historic Site",
        "All of the Bosses listed below in order of which you should defeat": "P.W. LHS Full Boss Order",
        "P.W. LHS Full Boss Order": "Follow the full boss route",
        "VA Majority Party Route": "Run the VA party route",
        "VI Majority Party Route": "Run the VI party route",
        "DA Majority Party Route": "Run the DA party route",
        "The Route You will be Taking will be down Below": "Steel Weak Route",
        "Steel Weak Route": "Run the Steel weakness route",
        "Ways to Increase your SK% Damage Further": "Boost your SK damage",
        "Ways to Increase your HP Further": "Raise HP for Armagedomon",
        "Utilizing the Deck Buff \"The Healers\" Deck Buff": "HP: The Healers Deck Buff",
        "HP: The Healers Deck Buff": "Use The Healers for HP",
        "Utilizing the Deck Buff \"Ancient Spirit Evolution\"": "HP: Ancient Spirit Evolution",
        "HP: Ancient Spirit Evolution": "Use Ancient Spirit Evolution",
        "Quick Guide Summary": "Review the final checklist",
    }
    current = title
    for _ in range(4):
        updated = replacements.get(current, current)
        if updated == current:
            return current
        current = updated
    return current


def nav_group(title: str, level: int) -> str | None:
    if title in {"General Information", "Progression Guide"}:
        return None
    groups = {
        "Start": {
            "Follow the full progression path",
            "Start here",
            "Unlock maps and travel routes",
            "Claim map completion rewards",
            "Find the best leveling spots",
            "Pick a leveling location",
            "Set up AoE leveling",
            "Build the BUW deck buff",
            "Level the BUW Digimon",
        },
        "Farming": {
            "Farm core materials",
            "Farm Tera at Lost Historic Site",
            "Farm Tera at Server Continent",
            "Collect hatch data",
            "Farm specific data types",
            "Choose the right card trades",
            "Use Villain Box rewards",
            "Recycle stones for more boxes",
            "Get enhancement buff boxes",
            "Use your enhancement buffs",
            "Collect Seal Master tickets",
            "Open seals for permanent stats",
        },
        "Early Game": {
            "Begin early-to-mid progression",
            "Choose your route at 70 archives",
            "Unlock Alphamon Ouryuken X",
            "Upgrade to Alphamon X Awaken",
            "Finish Alphamon X Extreme",
            "Spend extra Easy Points wisely",
            "Spend Nexus Coins wisely",
            "Know the Normal dungeon exceptions",
            "Unlock Fanglongmon Shin",
            "Roll the recommended accessory stats",
            "Start the AFK route",
            "Farm three Kunemon",
            "Farm Adventure Beach crests",
            "Follow the weekly crest schedule",
            "Finish the 14-day crest route",
            "Unlock Omegamon Merciful Mode",
        },
        "Mid Game": {
            "Move into late-game goals",
            "Start the VIP grind",
            "Farm Fanglongmon Hard rewards",
            "Plan your VIP dungeon runs",
            "Unlock Fanglongmon Ruin Mode",
            "Catch up on Normal dungeon gear",
            "Choose a Normal dungeon farm",
        },
        "Endgame": {
            "Enter P.W. Lost Historic Site",
            "Follow the full boss route",
            "Run the VA party route",
            "Run the VI party route",
            "Run the DA party route",
            "Run the Steel weakness route",
            "Boost your SK damage",
            "Raise HP for Armagedomon",
            "Use The Healers for HP",
            "Use Ancient Spirit Evolution",
            "Review the final checklist",
        },
    }
    for group, titles in groups.items():
        if title in titles:
            return group
    if level <= 2:
        return "Other"
    return None


def nav_label(title: str) -> str:
    labels = {
        "Follow the full progression path": "Full path",
        "Start here": "Intro",
        "Unlock maps and travel routes": "Map unlocks",
        "Claim map completion rewards": "Map rewards",
        "Find the best leveling spots": "Leveling basics",
        "Pick a leveling location": "Leveling spots",
        "Set up AoE leveling": "AoE setup",
        "Build the BUW deck buff": "BUW deck",
        "Level the BUW Digimon": "BUW Digimon",
        "Farm core materials": "Core farms",
        "Farm Tera at Lost Historic Site": "LHS Tera farm",
        "Farm Tera at Server Continent": "Server Tera farm",
        "Collect hatch data": "Hatch data",
        "Farm specific data types": "Data spots",
        "Choose the right card trades": "Card trades",
        "Use Villain Box rewards": "Villain boxes",
        "Recycle stones for more boxes": "Stone recycling",
        "Get enhancement buff boxes": "Buff boxes",
        "Use your enhancement buffs": "Buff list",
        "Collect Seal Master tickets": "Seal tickets",
        "Open seals for permanent stats": "Seal stats",
        "Begin early-to-mid progression": "Progression start",
        "Choose your route at 70 archives": "70 archive route",
        "Unlock Alphamon Ouryuken X": "Alphamon X",
        "Upgrade to Alphamon X Awaken": "Alphamon Awaken",
        "Finish Alphamon X Extreme": "Alphamon Extreme",
        "Spend extra Easy Points wisely": "Easy Points",
        "Spend Nexus Coins wisely": "Nexus Coins",
        "Know the Normal dungeon exceptions": "Rank exceptions",
        "Unlock Fanglongmon Shin": "Fanglongmon Shin",
        "Roll the recommended accessory stats": "Accessory rolls",
        "Start the AFK route": "AFK route",
        "Farm three Kunemon": "Kunemon farm",
        "Farm Adventure Beach crests": "Adventure Beach",
        "Follow the weekly crest schedule": "Crest schedule",
        "Finish the 14-day crest route": "14-day finish",
        "Unlock Omegamon Merciful Mode": "Merciful Mode",
        "Move into late-game goals": "Late-game goals",
        "Start the VIP grind": "VIP grind",
        "Farm Fanglongmon Hard rewards": "Fang Hard rewards",
        "Plan your VIP dungeon runs": "VIP runs",
        "Unlock Fanglongmon Ruin Mode": "Fanglongmon Ruin",
        "Catch up on Normal dungeon gear": "Normal gear",
        "Choose a Normal dungeon farm": "Normal farms",
        "Enter P.W. Lost Historic Site": "P.W. entry",
        "Follow the full boss route": "Full boss route",
        "Run the VA party route": "VA route",
        "Run the VI party route": "VI route",
        "Run the DA party route": "DA route",
        "Run the Steel weakness route": "Steel route",
        "Boost your SK damage": "SK damage",
        "Raise HP for Armagedomon": "Armagedomon HP",
        "Use The Healers for HP": "Healers deck",
        "Use Ancient Spirit Evolution": "Spirit deck",
        "Review the final checklist": "Final checklist",
    }
    return labels.get(title, title)


def render_nav(nav: list[dict[str, str]]) -> str:
    last_for_title = {display_title(item["title"]): index for index, item in enumerate(nav)}
    grouped: dict[str, list[dict[str, str]]] = {}
    for index, item in enumerate(nav):
        title = display_title(item["title"])
        if last_for_title.get(title) != index:
            continue
        group = nav_group(title, int(item["level"]))
        if not group:
            continue
        grouped.setdefault(group, []).append({**item, "title": title})

    order = [
        "Start",
        "Farming",
        "Early Game",
        "Mid Game",
        "Endgame",
        "Other",
    ]
    parts: list[str] = []
    for group in order:
        items = grouped.get(group, [])
        if not items:
            continue
        parts.append('<div class="toc-group">')
        parts.append(f'<p class="toc-group-title">{html.escape(group)}</p>')
        for item in items:
            label = nav_label(item["title"])
            parts.append(
                f'<a class="toc-level-{item["level"]}" href="#{item["id"]}" title="{html.escape(item["title"])}">{html.escape(label)}</a>'
            )
        parts.append("</div>")
    return "".join(parts)


def should_demote_heading(title: str) -> bool:
    return title in {
        "The Following Sections will be included",
        "following Digimon to level 70 and unlocking their Burst Mode Evolutions",
        "To Get Data, You can either",
        "Below is a list of some spots that drop their data",
        "Can be obtained in large quantities by either",
        "Buffs obtained once opened",
        "The only Dungeon's that break this rule is",
        "Kunemon Mercenary Eggs can either be farmed",
        "The Route You will be Taking will be down Below",
    }


def render_markdown(markdown: str) -> tuple[str, list[dict[str, str]], list[dict[str, str]]]:
    used: set[str] = set()
    nav: list[dict[str, str]] = []
    sections: list[dict[str, str]] = []
    out: list[str] = []
    list_state: str | None = None
    current_id = "top"
    current_title = "Digital Nexus Online Newbie Guide"
    current_text: list[str] = []
    section_open = False
    paragraph_lines: list[str] = []
    paragraph_class = "guide-line"

    def flush_section() -> None:
        nonlocal current_text
        if current_text:
            sections.append(
                {
                    "id": current_id,
                    "title": current_title,
                    "text": " ".join(current_text),
                }
            )
            current_text = []

    def line_class(stripped: str) -> str:
        lower = stripped.lower()
        if (
            lower.startswith("[total time")
            or lower.startswith("[time estimate")
            or lower.startswith("total expected time")
        ):
            return "time-estimate"
        if stripped.startswith("[") and stripped.endswith("]"):
            if lower.startswith("[important"):
                return "important"
            return "note"
        if lower.startswith(("requirements", "requirement")):
            return "requirement"
        if lower.startswith(("main goal", "side goal")):
            return "goal"
        if lower.startswith(("important", "[important")) or "do not open" in lower:
            return "important"
        return "guide-line"

    def flush_paragraph() -> None:
        nonlocal paragraph_class, paragraph_lines
        if not paragraph_lines:
            return
        text = " ".join(item.strip() for item in paragraph_lines if item.strip())
        structured = render_structured_block(current_id, text, paragraph_class)
        if structured:
            out.append(structured)
        else:
            out.append(f'<p class="{paragraph_class}">{inline_markup(text)}</p>')
        current_text.append(text)
        paragraph_lines = []
        paragraph_class = "guide-line"

    for raw in markdown.splitlines():
        line = raw.rstrip()
        stripped = line.strip()
        if not stripped:
            list_state = close_list(out, list_state)
            flush_paragraph()
            continue
        if stripped.startswith("<!-- PAGE"):
            flush_paragraph()
            page = stripped.replace("<!--", "").replace("-->", "").strip()
            out.append(f'<div class="page-marker">{html.escape(page)}</div>')
            continue

        heading = re.match(r"^(#{1,4})\s+(.+)$", stripped)
        if heading:
            list_state = close_list(out, list_state)
            flush_paragraph()
            flush_section()
            if section_open:
                out.append("</section>")
            level = len(heading.group(1))
            title = re.sub(r"\s+", " ", heading.group(2)).strip()
            if level >= 3 and should_demote_heading(title):
                if title == "following Digimon to level 70 and unlocking their Burst Mode Evolutions":
                    current_id = "build-the-buw-deck-buff"
                out.append(f'<p class="section-label">{inline_markup(display_title(title))}</p>')
                current_text.append(display_title(title))
                continue
            title = display_title(title)
            section_id = slugify(title, used)
            current_id = section_id
            current_title = title
            if level <= 3:
                nav.append({"id": section_id, "title": title, "level": str(level)})
            out.append(
                f'<section class="guide-section" id="{section_id}" data-title="{html.escape(title)}">'
            )
            section_open = True
            out.append('<div class="section-head">')
            out.append(f"<h{min(level, 3)}>{inline_markup(title)}</h{min(level, 3)}>")
            out.append(
                f'<a class="anchor-link" href="#{section_id}" aria-label="Copy link to {html.escape(title)}">#</a>'
            )
            out.append("</div>")
            continue

        if stripped == "---":
            list_state = close_list(out, list_state)
            flush_paragraph()
            out.append('<hr class="divider">')
            continue

        unordered = re.match(r"^[-*]\s+(.+)$", stripped)
        ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
        step = re.match(r"^Step\s+\d+\s*:\s*(.+)$", stripped, flags=re.IGNORECASE)
        if unordered or ordered or step:
            tag = "ul" if unordered else "ol"
            content = (unordered or ordered or step).group(1)
            if (
                ordered
                and paragraph_lines
                and not any("following items:" in pending for pending in paragraph_lines)
                and not re.search(r"[.:]$", paragraph_lines[-1].strip())
            ):
                paragraph_lines.append(content)
                continue
            flush_paragraph()
            if list_state != tag:
                list_state = close_list(out, list_state)
                out.append(f"<{tag}>")
                list_state = tag
            checklist = re.match(r"^\[\s*\]\s+(.+)$", content)
            if checklist:
                out.append(
                    f'<li class="check-item"><span class="fake-check" aria-hidden="true"></span>{inline_markup(checklist.group(1))}</li>'
                )
            else:
                out.append(f"<li>{inline_markup(content)}</li>")
            current_text.append(content)
            continue

        list_state = close_list(out, list_state)
        class_name = line_class(stripped)
        if stripped.lower().startswith("total expected time"):
            class_name = "important"
        if paragraph_lines and class_name != paragraph_class:
            flush_paragraph()
        paragraph_class = class_name
        paragraph_lines.append(stripped)

    list_state = close_list(out, list_state)
    flush_paragraph()
    flush_section()
    if section_open:
        out.append("</section>")
    return "\n".join(out), nav, sections


def write_site() -> None:
    PUBLIC.mkdir(exist_ok=True)
    full_markdown = clean_source_text(SOURCE.read_text(encoding="utf-8"))
    quick_match = re.search(
        r"## Quick Progression Summary[\s\S]*?(?=\n## Converted Source Draft)",
        full_markdown,
    )
    draft = full_markdown.split("## Converted Source Draft", 1)[-1].strip()
    markdown = f"{quick_match.group(0).strip()}\n\n{draft}" if quick_match else draft
    content, nav, sections = render_markdown(markdown)
    data = json.dumps(sections, ensure_ascii=False)
    nav_html = render_nav(nav)
    overview_html = render_overview()

    (PUBLIC / "index.html").write_text(
        f"""<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>Digital Nexus Online Guide</title>
    <link rel="icon" href="./assets/favicon.ico" sizes="any">
    <link rel="icon" href="./assets/site-logo.webp" type="image/webp">
    <link rel="apple-touch-icon" href="./assets/site-logo.webp">
    <link rel="stylesheet" href="./styles.css">
  </head>
  <body>
    <div class="app-shell">
      <aside class="sidebar">
        <a class="brand" href="#top" aria-label="Digital Nexus Online guide home">
          <img class="brand-logo" src="./assets/site-logo.webp" alt="Digital Nexus Online">
        </a>
        <label class="search-box">
          <span>Search guide</span>
          <input id="searchInput" type="search" placeholder="Search maps, Digimon, items..." autocomplete="off">
        </label>
        <div class="search-meta">
          <span id="resultCount">Ready</span>
          <button id="clearSearch" type="button">Clear</button>
        </div>
        <div id="searchResults" class="search-results" aria-live="polite"></div>
        <nav class="toc" aria-label="Guide sections">
          {nav_html}
        </nav>
      </aside>

      <main class="content">
        <header class="hero" id="top">
          <p class="eyebrow">Player Progression Database</p>
          <h1>Digital Nexus Online Newbie Guide</h1>
          <p class="hero-copy">A searchable, linkable guide for maps, farming routes, dungeon progression, VIP goals, and late-game milestones.</p>
          <div class="hero-stats">
            <span><strong>26</strong> PDF pages converted</span>
            <span><strong>8</strong> core milestones</span>
            <span><strong>136h 9m</strong> source estimate</span>
          </div>
        </header>
        {overview_html}
        <article id="guideContent" class="guide-content">
          {content}
        </article>
      </main>
    </div>
    <button id="backToTop" class="back-to-top" type="button" aria-label="Back to top">↑</button>
    <script>window.GUIDE_SECTIONS = {data};</script>
    <script src="./app.js"></script>
  </body>
</html>
""",
        encoding="utf-8",
    )

    (PUBLIC / "styles.css").write_text(
        """@font-face {
  font-family: "DNO Mono";
  src: local("Cascadia Mono"), local("Consolas");
}

:root {
  --bg: #06110c;
  --panel: #0c1f16;
  --panel-2: #10291d;
  --ink: #e8fff2;
  --muted: #9ac9aa;
  --green: #32f287;
  --green-2: #00b96b;
  --cyan: #64ffe0;
  --line: rgba(73, 255, 151, 0.18);
  --warn: #e6ff7a;
  --danger: #ff9f7a;
  color-scheme: dark;
}

* {
  box-sizing: border-box;
}

html {
  scroll-behavior: smooth;
}

body {
  margin: 0;
  background:
    linear-gradient(90deg, rgba(50, 242, 135, 0.035) 1px, transparent 1px),
    linear-gradient(rgba(50, 242, 135, 0.03) 1px, transparent 1px),
    radial-gradient(circle at 18% 10%, rgba(0, 185, 107, 0.2), transparent 30rem),
    var(--bg);
  background-size: 44px 44px, 44px 44px, auto, auto;
  color: var(--ink);
  font-family: Inter, "Segoe UI", Arial, sans-serif;
  line-height: 1.62;
}

a {
  color: inherit;
}

.app-shell {
  display: grid;
  grid-template-columns: 21rem minmax(0, 1fr);
  min-height: 100vh;
}

.sidebar {
  position: sticky;
  top: 0;
  height: 100vh;
  overflow: auto;
  border-right: 1px solid var(--line);
  background: rgba(6, 17, 12, 0.9);
  backdrop-filter: blur(18px);
  padding: 1.25rem;
}

.brand {
  display: flex;
  align-items: center;
  justify-content: center;
  text-decoration: none;
  padding-bottom: 1.25rem;
  border-bottom: 1px solid var(--line);
}

.brand-logo {
  display: block;
  width: min(12rem, 82%);
  height: auto;
  border: 1px solid rgba(50, 242, 135, 0.25);
  border-radius: 8px;
  box-shadow: var(--glow);
}

.hero h1,
.section-head h1,
.section-head h2,
.section-head h3 {
  font-family: "DNO Mono", "Segoe UI", sans-serif;
  letter-spacing: 0;
}

.search-box {
  display: grid;
  gap: 0.45rem;
  margin-top: 1.2rem;
  color: var(--muted);
  font-size: 0.82rem;
}

.search-box input {
  width: 100%;
  min-height: 2.75rem;
  border: 1px solid rgba(50, 242, 135, 0.35);
  background: #07170f;
  color: var(--ink);
  border-radius: 6px;
  padding: 0.75rem 0.85rem;
  font: inherit;
  outline: none;
}

.search-box input:focus {
  border-color: var(--green);
  box-shadow: 0 0 0 3px rgba(50, 242, 135, 0.12);
}

.search-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.8rem;
  margin: 0.75rem 0;
  color: var(--muted);
  font-size: 0.82rem;
}

button {
  border: 1px solid rgba(50, 242, 135, 0.35);
  background: rgba(50, 242, 135, 0.08);
  color: var(--ink);
  border-radius: 6px;
  min-height: 2.3rem;
  padding: 0.4rem 0.7rem;
  cursor: pointer;
}

button:hover {
  border-color: var(--green);
}

.search-results {
  display: grid;
  gap: 0.45rem;
  margin-bottom: 1rem;
}

.search-results a {
  display: block;
  border: 1px solid rgba(50, 242, 135, 0.18);
  border-radius: 6px;
  padding: 0.65rem;
  background: rgba(16, 41, 29, 0.62);
  text-decoration: none;
}

.search-results strong {
  display: block;
  color: var(--green);
  font-size: 0.88rem;
}

.search-results small {
  display: block;
  color: var(--muted);
  margin-top: 0.25rem;
}

.toc {
  display: grid;
  gap: 0.95rem;
  padding-top: 0.4rem;
}

.toc-group {
  display: grid;
  gap: 0.18rem;
}

.toc-group-title {
  margin: 0.3rem 0 0.15rem;
  color: var(--green);
  font-family: "DNO Mono", Consolas, monospace;
  font-size: 0.76rem;
  text-transform: uppercase;
}

.toc a {
  color: var(--muted);
  text-decoration: none;
  border-left: 2px solid transparent;
  padding: 0.38rem 0.55rem;
  border-radius: 0 6px 6px 0;
  font-size: 0.92rem;
}

.toc .toc-level-3 {
  padding-left: 1rem;
  font-size: 0.84rem;
}

.toc a:hover,
.toc a.active {
  color: var(--ink);
  background: rgba(50, 242, 135, 0.08);
  border-left-color: var(--green);
}

.content {
  min-width: 0;
  padding: 2rem clamp(1rem, 4vw, 4rem) 5rem;
}

.hero {
  border: 1px solid var(--line);
  background:
    linear-gradient(135deg, rgba(50, 242, 135, 0.12), rgba(100, 255, 224, 0.05)),
    rgba(12, 31, 22, 0.86);
  border-radius: 8px;
  padding: clamp(1.4rem, 4vw, 3rem);
  margin-bottom: 1.5rem;
}

.eyebrow {
  color: var(--cyan);
  font-family: "DNO Mono", Consolas, monospace;
  margin: 0 0 0.4rem;
  text-transform: uppercase;
  font-size: 0.8rem;
}

.hero h1 {
  margin: 0;
  font-size: clamp(2rem, 5vw, 4.5rem);
  line-height: 1.02;
  color: var(--ink);
  text-shadow: 0 0 24px rgba(50, 242, 135, 0.38);
}

.hero-copy {
  max-width: 54rem;
  color: var(--muted);
  font-size: 1.05rem;
}

.hero-stats {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem;
  margin-top: 1.3rem;
}

.hero-stats span {
  border: 1px solid rgba(50, 242, 135, 0.22);
  background: rgba(6, 17, 12, 0.58);
  border-radius: 6px;
  padding: 0.6rem 0.8rem;
  color: var(--muted);
}

.hero-stats strong {
  color: var(--green);
  font-family: "DNO Mono", Consolas, monospace;
}

.guide-content {
  max-width: 72rem;
}

.overview {
  max-width: 72rem;
  margin-bottom: 2rem;
  border-bottom: 1px solid var(--line);
  padding-bottom: 1.5rem;
}

.overview-head {
  margin: 0 0 1rem;
}

.overview-head h2 {
  margin: 0;
  color: var(--green);
  font-family: "DNO Mono", Consolas, monospace;
  font-size: clamp(1.5rem, 3vw, 2.4rem);
}

.overview-head p:not(.eyebrow) {
  color: var(--muted);
  max-width: 56rem;
}

.callout-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(16rem, 1fr));
  gap: 0.75rem;
  margin: 1rem 0 1.4rem;
}

.callout {
  border-left: 3px solid var(--green);
  border-radius: 0 6px 6px 0;
  background: rgba(50, 242, 135, 0.07);
  padding: 0.8rem 0.9rem;
  color: #d8f7e5;
}

.warning-callout,
.time-callout {
  border-left-color: var(--warn);
}

.overview-block {
  margin-top: 1.35rem;
}

.overview-block h3 {
  margin: 0 0 0.7rem;
  color: var(--cyan);
  font-family: "DNO Mono", Consolas, monospace;
  font-size: 1.05rem;
}

.guide-section {
  scroll-margin-top: 1rem;
  border-bottom: 1px solid var(--line);
  padding: 1rem 0 1.5rem;
}

.section-head {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin-top: 0.4rem;
}

.section-head h1,
.section-head h2,
.section-head h3 {
  margin: 0.6rem 0 0.35rem;
  color: var(--green);
  line-height: 1.15;
}

.section-head h2 {
  font-size: clamp(1.35rem, 3vw, 2.1rem);
}

.section-head h3 {
  font-size: 1.12rem;
  color: var(--cyan);
}

.anchor-link {
  color: var(--muted);
  text-decoration: none;
  opacity: 0.65;
  font-family: "DNO Mono", Consolas, monospace;
}

.anchor-link:hover {
  color: var(--green);
  opacity: 1;
}

p,
li {
  color: #d8f7e5;
}

code {
  color: var(--cyan);
  background: rgba(100, 255, 224, 0.08);
  border: 1px solid rgba(100, 255, 224, 0.18);
  border-radius: 4px;
  padding: 0.08rem 0.3rem;
}

ul,
ol {
  padding-left: 1.35rem;
}

.guide-content ol {
  counter-reset: route-step;
  display: grid;
  gap: 0.75rem;
  list-style: none;
  margin: 1rem 0 1.35rem;
  padding-left: 0;
}

.guide-content ol li {
  counter-increment: route-step;
  position: relative;
  border: 1px solid rgba(50, 242, 135, 0.18);
  border-left: 3px solid rgba(50, 242, 135, 0.72);
  border-radius: 0 8px 8px 0;
  background: rgba(50, 242, 135, 0.045);
  padding: 0.65rem 0.8rem 0.7rem 3.25rem;
}

.guide-content ol li::before {
  content: counter(route-step);
  position: absolute;
  left: 0.75rem;
  top: 0.72rem;
  display: grid;
  place-items: center;
  width: 1.65rem;
  height: 1.65rem;
  border-radius: 50%;
  border: 1px solid rgba(139, 255, 206, 0.5);
  background: rgba(11, 75, 50, 0.85);
  color: var(--green-soft);
  font-family: var(--font-mono);
  font-size: 0.85rem;
  font-weight: 800;
}

.guide-content ul li.check-item {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  border: 1px solid rgba(100, 255, 224, 0.18);
  border-left: 3px solid var(--cyan);
  border-radius: 0 8px 8px 0;
  background: rgba(100, 255, 224, 0.045);
  padding: 0.65rem 0.8rem;
}

.fake-check {
  width: 1.2rem;
  height: 1.2rem;
  flex: 0 0 1.2rem;
  border-radius: 4px;
  border: 1px solid rgba(139, 255, 206, 0.7);
  background: rgba(11, 75, 50, 0.55);
  box-shadow: inset 0 0 0 2px rgba(1, 18, 12, 0.9);
}

.requirement,
.goal,
.important,
.note,
.time-estimate {
  border-left: 3px solid var(--green);
  background: rgba(50, 242, 135, 0.07);
  padding: 0.7rem 0.9rem;
  border-radius: 0 6px 6px 0;
}

.goal {
  border-left-color: var(--cyan);
}

.important,
.note {
  border-left-color: var(--warn);
}

.time-estimate {
  border-left-color: var(--cyan);
  background: rgba(100, 255, 224, 0.075);
  font-family: "DNO Mono", Consolas, monospace;
}

.note {
  font-style: italic;
}

.important {
  font-weight: 800;
}

.guide-line em,
.note em {
  color: #dfffc1;
}

.guide-line strong,
.important strong {
  color: var(--warn);
}

.bracketed,
.parenthetical {
  display: inline-block;
  border: 1px solid rgba(100, 255, 224, 0.24);
  background: rgba(100, 255, 224, 0.07);
  color: #c8fff1;
  border-radius: 4px;
  padding: 0 0.25rem;
  margin: 0 0.05rem;
  font-family: "DNO Mono", Consolas, monospace;
  font-size: 0.9em;
  font-style: normal;
  line-height: 1.45;
}

.structured-list,
.sequence-list,
.boss-list {
  display: grid;
  gap: 0.45rem;
  list-style-position: outside;
  margin: 0.9rem 0 1rem;
  padding-left: 1.4rem;
}

.structured-list li,
.sequence-list li,
.boss-list li {
  border-left: 2px solid rgba(50, 242, 135, 0.35);
  background: rgba(50, 242, 135, 0.045);
  border-radius: 0 6px 6px 0;
  padding: 0.45rem 0.65rem;
}

.boss-list {
  grid-template-columns: repeat(auto-fit, minmax(18rem, 1fr));
  list-style: none;
  padding-left: 0;
}

.data-table,
.overview-table {
  width: 100%;
  border-collapse: collapse;
  margin: 0.9rem 0 1rem;
  overflow: hidden;
  border: 1px solid rgba(50, 242, 135, 0.22);
  border-radius: 6px;
}

.data-table th,
.data-table td,
.overview-table th,
.overview-table td {
  border-bottom: 1px solid rgba(50, 242, 135, 0.14);
  padding: 0.65rem 0.75rem;
  text-align: left;
  vertical-align: top;
}

.data-table th,
.overview-table th {
  color: var(--green);
  background: rgba(50, 242, 135, 0.08);
  font-family: "DNO Mono", Consolas, monospace;
}

.data-table tr:last-child td,
.overview-table tr:last-child td {
  border-bottom: 0;
}

.parenthetical {
  border-color: rgba(50, 242, 135, 0.2);
  background: rgba(50, 242, 135, 0.055);
  color: #bdf8d3;
}

.divider {
  border: 0;
  border-top: 1px solid var(--line);
  margin: 1.3rem 0;
}

.page-marker {
  display: inline-block;
  margin-top: 1.1rem;
  color: var(--muted);
  border: 1px solid var(--line);
  border-radius: 999px;
  padding: 0.14rem 0.55rem;
  font-size: 0.75rem;
  font-family: "DNO Mono", Consolas, monospace;
}

.section-label {
  margin-top: 1.2rem;
  color: var(--cyan);
  font-family: "DNO Mono", Consolas, monospace;
  font-size: 0.9rem;
}

mark {
  background: rgba(230, 255, 122, 0.25);
  color: var(--ink);
  border-radius: 3px;
}

.hidden-by-search {
  display: none;
}

.back-to-top {
  position: fixed;
  right: 1rem;
  bottom: 1rem;
  width: 2.8rem;
  aspect-ratio: 1;
  display: none;
  padding: 0;
}

.back-to-top.visible {
  display: block;
}

@media (max-width: 980px) {
  .app-shell {
    grid-template-columns: 1fr;
  }

  .sidebar {
    position: relative;
    height: auto;
    border-right: 0;
    border-bottom: 1px solid var(--line);
  }

  .toc {
    max-height: 16rem;
    overflow: auto;
  }

  .content {
    padding-top: 1rem;
  }
}
""",
        encoding="utf-8",
    )

    (PUBLIC / "app.js").write_text(
        """const sections = window.GUIDE_SECTIONS || [];
const input = document.querySelector("#searchInput");
const results = document.querySelector("#searchResults");
const resultCount = document.querySelector("#resultCount");
const clearSearch = document.querySelector("#clearSearch");
const guideSections = [...document.querySelectorAll(".guide-section")];
const tocLinks = [...document.querySelectorAll(".toc a")];
const backToTop = document.querySelector("#backToTop");

const escapeRegExp = (value) => value.replace(/[.*+?^${}()|[\\]\\\\]/g, "\\\\$&");

function snippet(text, query) {
  const lower = text.toLowerCase();
  const index = lower.indexOf(query.toLowerCase());
  const start = Math.max(0, index - 58);
  const end = Math.min(text.length, index + query.length + 110);
  const raw = (index === -1 ? text.slice(0, 160) : text.slice(start, end)).trim();
  const escaped = raw.replace(/[&<>"']/g, (char) => ({
    "&": "&amp;",
    "<": "&lt;",
    ">": "&gt;",
    '"': "&quot;",
    "'": "&#039;"
  })[char]);
  return query ? escaped.replace(new RegExp(escapeRegExp(query), "ig"), "<mark>$&</mark>") : escaped;
}

function applySearch() {
  const query = input.value.trim();
  const normalized = query.toLowerCase();

  if (!query) {
    guideSections.forEach((section) => section.classList.remove("hidden-by-search"));
    results.innerHTML = "";
    resultCount.textContent = "Ready";
    return;
  }

  const matches = sections.filter((section) => {
    const haystack = `${section.title} ${section.text}`.toLowerCase();
    return haystack.includes(normalized);
  });
  const ids = new Set(matches.map((match) => match.id));
  guideSections.forEach((section) => {
    section.classList.toggle("hidden-by-search", !ids.has(section.id));
  });

  resultCount.textContent = `${matches.length} result${matches.length === 1 ? "" : "s"}`;
  results.innerHTML = matches.slice(0, 18).map((match) => `
    <a href="#${match.id}">
      <strong>${match.title}</strong>
      <small>${snippet(match.text, query)}</small>
    </a>
  `).join("");
}

input.addEventListener("input", applySearch);
clearSearch.addEventListener("click", () => {
  input.value = "";
  applySearch();
  input.focus();
});

document.querySelectorAll(".anchor-link").forEach((link) => {
  link.addEventListener("click", async () => {
    const url = `${location.origin}${location.pathname}${link.getAttribute("href")}`;
    if (navigator.clipboard && location.protocol !== "file:") {
      await navigator.clipboard.writeText(url);
    }
  });
});

const observer = new IntersectionObserver((entries) => {
  entries.forEach((entry) => {
    if (!entry.isIntersecting) return;
    tocLinks.forEach((link) => {
      link.classList.toggle("active", link.getAttribute("href") === `#${entry.target.id}`);
    });
  });
}, { rootMargin: "-20% 0px -70% 0px", threshold: 0.01 });

guideSections.forEach((section) => observer.observe(section));

window.addEventListener("scroll", () => {
  backToTop.classList.toggle("visible", window.scrollY > 700);
});

backToTop.addEventListener("click", () => {
  window.scrollTo({ top: 0, behavior: "smooth" });
});
""",
        encoding="utf-8",
    )

    PAGES.mkdir(exist_ok=True)
    if ASSETS.exists():
        shutil.copytree(ASSETS, PUBLIC / "assets", dirs_exist_ok=True)

    for filename in ("index.html", "styles.css", "app.js"):
        shutil.copy2(PUBLIC / filename, PAGES / filename)
    if ASSETS.exists():
        shutil.copytree(ASSETS, PAGES / "assets", dirs_exist_ok=True)

    print(f"Wrote {PUBLIC / 'index.html'}")
    print(f"Wrote {PAGES / 'index.html'}")


if __name__ == "__main__":
    write_site()
