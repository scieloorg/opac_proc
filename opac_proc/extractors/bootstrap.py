# coding: utf-8
from __future__ import unicode_literals
import logging

import config
from opac_proc.extractors.collections import extraction

logger = logging.getLogger(__name__)


def run(collection_acronym):
    coll_extractor = extraction.CExtactor(collection_acronym)
    coll_extractor.run()
    col = coll_extractor.get_extracted_raw_data()[0]
    print(col)
    import pdb; pdb.set_trace()
    # collection.save()
    # transformed_collection = transform_collection(collection_data)


if __name__ == '__main__':
    run('spa')
