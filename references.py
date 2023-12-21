from flask import abort, Flask
import mwapi
import re

app = Flask(__name__)

USER_AGENT = "https://toolsadmin.wikimedia.org/tools/id/reference-counter"

PROJECTS = [
    "wikipedia",
    "wikibooks",
    #"wikidata", wikidata project has its own way of counting references
    "wikimedia",
    "wikinews",
    "wikiquote",
    "wikisource",
    "wikiversity",
    "wikivoyage",
    "wiktionary",
]

# These templates are specific to English language.
SFN_TEMPLATES = [
    r"Shortened footnote template", r"sfn",
    r"Sfnp",
    r"Sfnm",
    r"Sfnmp"
]

LANGUAGE_CODES = ['aa', 'ab', 'ace', 'ady', 'af', 'ak', 'als', 'am', 'an', 'ang', 'ar', 'arc', 'ary', 'arz', 'as', 'ast', 'atj', 'av', 'avk', 'awa', 'ay', 'az', 'azb', 'ba', 'ban', 'bar', 'bat-smg', 'bcl', 'be', 'be-x-old', 'bg', 'bh', 'bi', 'bjn', 'bm', 'bn', 'bo', 'bpy', 'br', 'bs', 'bug', 'bxr', 'ca', 'cbk-zam', 'cdo', 'ce', 'ceb', 'ch', 'cho', 'chr', 'chy', 'ckb', 'co', 'cr', 'crh', 'cs', 'csb', 'cu', 'cv', 'cy', 'da', 'de', 'din', 'diq', 'dsb', 'dty', 'dv', 'dz', 'ee', 'el', 'eml', 'en', 'eo', 'es', 'et', 'eu', 'ext', 'fa', 'ff', 'fi', 'fiu-vro', 'fj', 'fo', 'fr', 'frp', 'frr', 'fur', 'fy', 'ga', 'gag', 'gan', 'gcr', 'gd', 'gl', 'glk', 'gn', 'gom', 'gor', 'got', 'gu', 'gv', 'ha', 'hak', 'haw', 'he', 'hi', 'hif', 'ho', 'hr', 'hsb', 'ht', 'hu', 'hy', 'hyw', 'hz', 'ia', 'id', 'ie', 'ig', 'ii', 'ik', 'ilo', 'inh', 'io', 'is', 'it', 'iu', 'ja', 'jam', 'jbo', 'jv', 'ka', 'kaa', 'kab', 'kbd', 'kbp', 'kg', 'ki', 'kj', 'kk', 'kl', 'km', 'kn', 'ko', 'koi', 'kr', 'krc', 'ks', 'ksh', 'ku', 'kv', 'kw', 'ky', 'la', 'lad', 'lb', 'lbe', 'lez', 'lfn', 'lg', 'li', 'lij', 'lld', 'lmo', 'ln', 'lo', 'lrc', 'lt', 'ltg', 'lv', 'mai', 'map-bms', 'mdf', 'mg', 'mh', 'mhr', 'mi', 'min', 'mk', 'ml', 'mn', 'mnw', 'mr', 'mrj', 'ms', 'mt', 'mus', 'mwl', 'my', 'myv', 'mzn', 'na', 'nah', 'nap', 'nds', 'nds-nl', 'ne', 'new', 'ng', 'nl', 'nn', 'no', 'nov', 'nqo', 'nrm', 'nso', 'nv', 'ny', 'oc', 'olo', 'om', 'or', 'os', 'pa', 'pag', 'pam', 'pap', 'pcd', 'pdc', 'pfl', 'pi', 'pih', 'pl', 'pms', 'pnb', 'pnt', 'ps', 'pt', 'qu', 'rm', 'rmy', 'rn', 'ro', 'roa-rup', 'roa-tara', 'ru', 'rue', 'rw', 'sa', 'sah', 'sat', 'sc', 'scn', 'sco', 'sd', 'se', 'sg', 'sh', 'shn', 'si', 'simple', 'sk', 'sl', 'sm', 'smn', 'sn', 'so', 'sq', 'sr', 'srn', 'ss', 'st', 'stq', 'su', 'sv', 'sw', 'szl', 'szy', 'ta', 'tcy', 'te', 'tet', 'tg', 'th', 'ti', 'tk', 'tl', 'tn', 'to', 'tpi', 'tr', 'ts', 'tt', 'tum', 'tw', 'ty', 'tyv', 'udm', 'ug', 'uk', 'ur', 'uz', 've', 'vec', 'vep', 'vi', 'vls', 'vo', 'wa', 'war', 'wo', 'wuu', 'xal', 'xh', 'xmf', 'yi', 'yo', 'za', 'zea', 'zh', 'zh-classical', 'zh-min-nan', 'zh-yue', 'zu']

@app.route("/")
def hello_world():
    return "<p>Hello, World! This is the References API.</p>"

@app.route('/api/v1/references/<project>/<lang>/<int:revid>')
def get_references(project, lang, revid):
    error = validate_api_args(project, lang)
    if error:
        return error, 400
    
    # TODO: get the wikitext by querying the replica db directly
    try:
        # Request the wikitext
        session = mwapi.Session(f'https://{lang}.{project}.org', user_agent=USER_AGENT)

        result = session.get(
                    action="parse",
                    oldid=revid,
                    prop='wikitext',
                    format='json',
                    formatversion=2
                )
    
    except mwapi.errors.APIError as e:
        return e.info, 404
    
    wikitext = result['parse']['wikitext']

    # Compile regular expressions
    
    # Match references using <ref /> tags
    ref_singleton = re.compile(r'<ref(\s[^/>]*)?/>', re.M | re.I)
    # Match regerences using <ref> and </ref> tags
    ref_tag = re.compile(r'<ref(\s[^/>]*)?>[\s\S]*?</ref>', re.M | re.I)
    # Match shortened footnote templates
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

def validate_api_args(project, lang):
    """Validate API arguments."""
    error = ''
    if not lang in LANGUAGE_CODES:
        error = f'Language {lang} is not a valid language. '
    if not project in PROJECTS:
        error+= f'Project {project} is not a valid project.'
    return error
