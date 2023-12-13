from flask import Flask
import mwapi
import re

app = Flask(__name__)

SFN_TEMPLATES = [
    r"Shortened footnote template", r"sfn",
    r"Sfnp",
    r"Sfnm",
    r"Sfnmp"
]

@app.route("/")
def hello_world():
    return "<p>Hello, World! This is the References API.</p>"

@app.route('/api/v1/references/<project>/<lang>/<int:revid>')
def get_references(project, lang, revid):
    # Request the wikitext
    session = mwapi.Session(f'https://{lang}.{project}.org')

    result = session.get(
                action="parse",
                oldid=revid,
                prop='wikitext',
                format='json',
                formatversion=2
            )
    
    wikitext = result['parse']['wikitext']
    
    # Compile regular expressions
    ref_singleton = re.compile(r'<ref(\s[^/>]*)?/>', re.M | re.I)
    ref_tag = re.compile(r'<ref(\s[^/>]*)?>[\s\S]*?</ref>', re.M | re.I)
    shortened_footnote_templates = re.compile("|".join(SFN_TEMPLATES), re.I)

    # remove comments / lowercase for matching namespace prefixes better
    wikitext = re.sub(r'<!--.*?-->', '', wikitext, flags=re.DOTALL).lower()
    
    num_ref_singleton = len(ref_singleton.findall(wikitext))
    num_ref_tag = len(ref_tag.findall(wikitext))
    num_ref_sft = len(shortened_footnote_templates.findall(wikitext))
    num_ref = num_ref_singleton + num_ref_tag + num_ref_sft

    return {
        "project": project,
        "lang": lang,
        "revid": revid,
        "num_ref_singleton": num_ref_singleton,
        "num_ref_tag": num_ref_tag,
        "num_ref_sft": num_ref_sft,
        "wikitext": wikitext,
        "num_ref": num_ref,
        }
