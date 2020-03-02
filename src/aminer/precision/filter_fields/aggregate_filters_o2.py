import os

import pkg_resources
from aminer.precision.utility import load_json, dump_json
support_directory = pkg_resources.resource_filename("aminer", "support")
directory_2019 = os.path.join(support_directory, "2019_filters")


fos = load_json(os.path.join(directory_2019, 'fos_filtered_recommendations.json'))
author = load_json(os.path.join(support_directory, 'author_filtered_citations_o2.json'))
years = load_json(os.path.join(support_directory, 'invalid_citations_based_on_year.json'))
language = load_json(os.path.join(directory_2019, 'invalid_citations_based_on_language.json'))

both = {}
for id in fos:
    if id in author:
        both[id] = list(set(author[id]).intersection(set(fos[id])) - set(years) - set(language))
    else:
        both[id] = list(set(fos[id]) - set(years))

dump_json(os.path.join(directory_2019, 'aggregated_filters_o2.json'), both)
