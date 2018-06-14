from opac_proc.datastore import models
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.loaders.jobs import task_load_issue, task_load_article

# setup:
get_db_connection()
stage = 'load'
r_queues = RQueues()
r_queues.create_queues_for_stage(stage)

# definição de journals a processar
target_issn_list = [
    # '0034-8910',  # rsp
    '1726-4634',  # # rpmesp
]

collection = models.TransformCollection.objects.all().first()

# filtramos para pegar os ids de children_ids
for child in collection['children_ids']:
    print u"procurando... issn: ", child['issn']
    target_issn = child['issn']
    if target_issn in target_issn_list:
        issues_uuids = models.TransformIssue.objects.filter(pid__contains=target_issn).values_list('uuid')
        articles_uuids = models.TransformArticle.objects.filter(pid__contains=target_issn).values_list('uuid')
        print u"encontrei %s pids de issues do periódico %s para processar" % (len(issues_uuids), target_issn)
        print u"encontrei %s pids de artigos do periódico %s para processar" % (len(articles_uuids), target_issn)
        # para cada pid de issues, enfileramos na quere certa:
        enqueued_issues_counts = 0
        for issue_uuid in issues_uuids:
            r_queues.enqueue(stage, 'issue', task_load_issue, issue_uuid)
            enqueued_issues_counts += 1
        print u"enfilerados %s PIDs de issues do periódico %s" % (enqueued_issues_counts, issue_uuid)
        # para cada pid de artigos, enfileramos na queue certa:
        enqueued_articles_counts = 0
        for article_uuid in articles_uuids:
            r_queues.enqueue(stage, 'article', task_load_article, article_uuid)
            enqueued_articles_counts += 1
        print u"enfilerados %s PIDs de artigos do periódico %s" % (enqueued_articles_counts, article_uuid)
