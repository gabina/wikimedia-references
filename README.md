# wikimedia-references
Flask API designed specifically to get the number of references for a given revision in some Wikimedia project and language.

Find more context on why this API is being developed on [this phabricator task](https://phabricator.wikimedia.org/T352177).

This version is intended to be run only locally, not in [Toolforge](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python).

The code is based on the already existing APIs to get references, such as [quality-revid-features](https://github.com/wikimedia/research-api-endpoint-template/blob/quality-article/model/wsgi.py#L621) and [articlequality](https://github.com/wikimedia/articlequality/blob/master/articlequality/feature_lists/enwiki.py#L49-L51).

The primary goal of this initial version is to verify that the results obtained from the API utilized in the [WikiEduDashboard](https://github.com/WikiEducationFoundation/WikiEduDashboard) align with those obtained from this new API.

## Decisions/Concerns

- This API counts references based on the wikitext for the revision. It includes the self-closing tag `<ref/>` and the container version (`<ref>` and `</ref>`). It also takes shortened footnote templates into account.
- Shortened footnote templates are wiki-specific, varying across languages and projects. While it is possible to build wiki-specific lists of templates, the API employs a basic English set of templates for all languages. Many of these templates may not exist in languages other than English, but this shouldn't create false positives, as editors won't use them there (it'd be highly unlikely that the same template exists for another language but with a totally different purpose). It's always possible to add local-language variants of these templates for new wikis.
- The Wikidata project isn't covered by this API, as it operates differently from other projects. There already exists a specific Ruby gem called [wikidata-diff-analyzer](https://github.com/WikiEducationFoundation/wikidata-diff-analyzer) recommended for extracting references.
- The reference count isn't flawless. Some references may be overlooked, such as when a shortened footnote template is absent from the list. Conversely, false positives may occur. For example, revision [1189646754](https://en.wikipedia.org/w/index.php?title=Wikipedia:Citing_sources&action=edit&oldid=1189646754) has a lot of false positives due to the <ref> tag being inserted as code, a scenario the API doesn't handle with precision.

## How to run

You need [Flask](https://flask.palletsprojects.com/en/3.0.x/installation/) and [mwapi](https://pypi.org/project/mwapi/) installed. Then, run
``$ flask --app references run``

## Examples

http://127.0.0.1:5000/api/v1/references/wikipedia/en/829840085

http://127.0.0.1:5000/api/v1/references/wikipedia/en/829840094
