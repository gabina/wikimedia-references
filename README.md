# wikimedia-references
A first version of the Flask API to get existing references for a specific revision in some Wikimedia project and language.
Find more context on why this API is being developed on [this phabricator task](https://phabricator.wikimedia.org/T352177).

This version is intended to be run only locally, not in [Toolforge](https://wikitech.wikimedia.org/wiki/Help:Toolforge/Web/Python).

The code is based on the already existing APIs to get references, such as [quality-revid-features](https://github.com/wikimedia/research-api-endpoint-template/blob/quality-article/model/wsgi.py#L621) and [articlequality](https://github.com/wikimedia/articlequality/blob/master/articlequality/feature_lists/enwiki.py#L49-L51).


The primary goal of this initial version is to verify that the results obtained from the API utilized in the [WikiEduDashboard](https://github.com/WikiEducationFoundation/WikiEduDashboard) align with those obtained from this new API.

## How to run

You need [Flask](https://flask.palletsprojects.com/en/3.0.x/installation/) and [mwapi](https://pypi.org/project/mwapi/) installed. Then, run
``$ flask --app references run``

## Examples

http://127.0.0.1:5000/api/v1/references/wikipedia/en/829840085

http://127.0.0.1:5000/api/v1/references/wikipedia/en/829840094
