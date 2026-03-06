"""
Skript for å generere en samlet HTML-rapport fra Markdown-dokumentasjonen.
Bruksanvisning:
1. Sørg for at 'pandoc' er installert på systemet.
2. Kjør skriptet med: python3 generate_monitoring_html.py
"""
import os
import re
import subprocess

# Oppsett
DOCS_DIR = "bufDocs/Bufdir.no/Monitorering/Verification"
OUTPUT_FILE = os.path.join(DOCS_DIR, "monitorerings-gjennomgang.html")

MD_FILES = [
    "oppsummering-overvaaking.md",
    "kritiske-funn-og-tiltak.md",
    "implementasjonsguide.md",
    "app-gateway-fallgruver.md",
    "serilog-og-opentelemetry.md",
    "js-ts-monitoring-verification.md",
    "gap-analysis-implementation.md"
]

# Mapping fra filnavn til Pandoc-genererte ID-er for hovedoverskrifter
# Disse ID-ene er basert på Pandocs standard algoritme (små bokstaver, fjern spesialtegn)
FILE_TO_ID = {
    "oppsummering-overvaaking.md": "oppsummering-monitorering-og-infrastruktur-fsa-og-bufdirno",
    "kritiske-funn-og-tiltak.md": "vurdert-sannsynlig-årsak-til-produksjonsstopp-fsa",
    "implementasjonsguide.md": "implementasjonsguide-fix-av-monitorering-og-infrastruktur",
    "app-gateway-fallgruver.md": "fallgruver-ved-bruk-av-azure-application-gateway-og-monitorering",
    "serilog-og-opentelemetry.md": "serilog-og-opentelemetry-i-bufdir.no",
    "js-ts-monitoring-verification.md": "verifisering-av-jsts-monitorering",
    "gap-analysis-implementation.md": "gap-analyse-implementasjon-vs.-strategi"
}

def fix_markdown_lists(content):
    """Sørger for at det er en tom linje før lister for korrekt Pandoc-tolkning."""
    # Finn linjer som starter med kulepunkt eller tall, men som ikke har en tom linje over seg
    lines = content.split('\n')
    fixed_lines = []
    for i, line in enumerate(lines):
        if i > 0 and re.match(r'^\s*[\*\-\+] ', line) and lines[i-1].strip() != "" and not lines[i-1].startswith(' '):
            fixed_lines.append("")
        elif i > 0 and re.match(r'^\s*\d+\. ', line) and lines[i-1].strip() != "" and not lines[i-1].startswith(' '):
            fixed_lines.append("")
        fixed_lines.append(line)
    return '\n'.join(fixed_lines)

def run_generation():
    print("Pre-prosesserer Markdown-filer...")
    temp_files = []
    for f in MD_FILES:
        path = os.path.join(DOCS_DIR, f)
        with open(path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        fixed_content = fix_markdown_lists(content)
        temp_path = path + ".tmp"
        with open(temp_path, 'w', encoding='utf-8') as file:
            file.write(fixed_content)
        temp_files.append(temp_path)

    print("Kjører Pandoc...")
    title = "Monitorerings- og Infrastruktur-gjennomgang for Bufdir.no og FSA"
    cmd = [
        "pandoc", "-s", "-f", "markdown", "-t", "html",
        "--wrap=none",
        "--metadata", f"title={title}",
        "--metadata", f"date=Generert: {subprocess.check_output(['date', '+%Y-%m-%d']).decode().strip()}",
        "-o", OUTPUT_FILE
    ] + temp_files
    
    subprocess.run(cmd, check=True)

    # Opprydding av temp-filer
    for tf in temp_files:
        os.remove(tf)

    print("Post-prosesserer HTML...")
    with open(OUTPUT_FILE, 'r', encoding='utf-8') as f:
        html = f.read()

    # 1. Fiks interne lenker (endre .md til interne ankre)
    # Håndter lenker med ankre: filnavn.md#anker -> #anker
    # Vi må vaske ankeret slik at det matcher Pandocs ID-generering (fjerner ofte ledende tall og punktum)
    def clean_anchor(match):
        anchor = match.group(1)
        # Dekode URL-enkoding (%C3%A5 -> å)
        from urllib.parse import unquote
        anchor = unquote(anchor)
        # Fjern ledende tall og punktum (f.eks. "1.-vurdert..." -> "vurdert...")
        anchor = re.sub(r'^[0-9.]+\s*', '', anchor)
        # Gjør til små bokstaver
        anchor = anchor.lower()
        # Erstatt spesialtegn som dash (–) med vanlig bindestrek (-)
        anchor = anchor.replace('–', '-')
        # Erstatt mellomrom med bindestrek
        anchor = anchor.replace(' ', '-')
        # Fjern tegn som Pandoc vanligvis stripper (punktum, parenteser, kolon, etc.)
        # Men BEHOLD norske tegn (æøå)
        anchor = re.sub(r'[^\w\s\-æøå]', '', anchor)
        # Fjern gjentatte bindestreker
        anchor = re.sub(r'-+', '-', anchor)
        # Fjern ledende/avsluttende bindestreker
        anchor = anchor.strip('-')
        return f'href="#{anchor}"'

    html = re.sub(r'href="[^"]+\.md#([^"]+)"', clean_anchor, html)
    
    # Håndter lenker til hele filer: filnavn.md -> #hoved-id
    for filename, section_id in FILE_TO_ID.items():
        html = html.replace(f'href="{filename}"', f'href="#{section_id}"')

    # 2. Legg til CSS for bred layout og forbedret typografi
    custom_css = """
<style>
    body {
        max-width: 1400px;
        margin: 0 auto;
        padding: 40px;
        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
        line-height: 1.6;
        color: #333;
    }
    h1, h2, h3 { color: #005aab; }
    pre {
        background: #f4f4f4;
        padding: 15px;
        border-radius: 5px;
        overflow-x: auto;
    }
    code { font-family: "SFMono-Regular", Consolas, "Liberation Mono", Menlo, monospace; }
    ul, ol { margin-bottom: 20px; }
    li { margin-bottom: 8px; }
    a { 
        color: #005aab; 
        text-decoration: underline; 
    }
    a:hover { 
        color: #003d73;
        text-decoration: none; 
    }
    #TOC { display: none; } /* Skjul TOC hvis den er der */
</style>
"""
    # Injiser CSS i <head>
    html = html.replace('</head>', f'{custom_css}\n</head>')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"Fullført! HTML-fil lagret som {OUTPUT_FILE}")

if __name__ == "__main__":
    run_generation()
