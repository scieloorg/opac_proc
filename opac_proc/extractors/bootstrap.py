# coding: utf-8
from __future__ import unicode_literals
import logging

import config
from opac_proc.extractors.collections import extraction

logger = logging.getLogger(__name__)


def run(collection_acronym):
    collection_id = extraction.CExtactor(collection_acronym)
    transformed_collection = transform_collection(collection_data)


if __name__ == '__main__':
    run('spa')
