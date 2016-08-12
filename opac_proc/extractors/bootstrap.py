# coding: utf-8
from __future__ import unicode_literals
import logging

import config
from .collections.extraction import extract_collection

logger = logging.getLogger(__name__)


def start(collection_acronym):
    collection_id = extract_collection(collection_acronym)
    transformed_collection = transform_collection(collection_data)
