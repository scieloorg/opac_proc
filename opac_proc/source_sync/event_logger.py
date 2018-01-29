# coding: utf-8
import sys
import os

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore import events_models
from opac_proc.datastore.mongodb_connector import get_db_connection


def create_sync_event_record(stage, model_name, func_name, description):
    get_db_connection()
    entry = events_models.SyncEventModel(description=description)
    entry['stage'] = stage
    entry['model_name'] = model_name
    entry['func_name'] = str(func_name)
    entry.save()
    return entry.pk
