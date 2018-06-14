# coding: utf-8
from flask import render_template

from opac_proc.datastore.mongodb_connector import register_connections
from opac_proc.datastore import events_models


def timeline_index():
    register_connections()

    sync_events = events_models.SyncEventModel.objects.all()

    collection_events = sync_events.filter(model_name='collection')
    journal_events = sync_events.filter(model_name='journal')
    issue_events = sync_events.filter(model_name='issue')
    article_events = sync_events.filter(model_name='article')
    news_events = sync_events.filter(model_name='news')
    press_release_events = sync_events.filter(model_name='press_release')

    context = {
        'all_events': sync_events,
        'collection_events': collection_events,
        'journal_events': journal_events,
        'issue_events': issue_events,
        'article_events': article_events,
        'news_events': news_events,
        'press_release_events': press_release_events,
    }
    return render_template("timeline_index.html", **context)
