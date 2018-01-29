from opac_proc.datastore import models
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.extractors.jobs import task_extract_issue, task_extract_article

# setup:
get_db_connection()
stage = 'extract'
r_queues = RQueues()
r_queues.create_queues_for_stage(stage)

# definição de journals a processar
target_issn_list = [
    # '0034-8910',  # rsp
    '1726-4634',  # # rpmesp
]

collection = models.ExtractCollection.objects.all().first()

# filtramos para pegar os ids de children_ids
for child in collection['children_ids']:
    print u"procurando... issn: ", child['issn']
    if child['issn'] in target_issn_list:
        print u"encontrei o periódico procurado: %s" % child['issn']
        # dos children_ids, pegamos os articles_ids (pids do artigos)
        articles_ids = child['articles_ids']
        issues_ids = child['issues_ids']
        print u"encontrei %s pids de issues do periódico %s para processar" % (len(issues_ids), child['issn'])
        print u"encontrei %s pids de artigos do periódico %s para processar" % (len(articles_ids), child['issn'])
        # para cada pid de issues, enfileramos na quere certa:
        enqueued_issues_counts = 0
        for issue_pid in issues_ids:
            r_queues.enqueue(stage, 'issue', task_extract_issue, collection.acronym, issue_pid)
            enqueued_issues_counts += 1
        print u"enfilerados %s PIDs de issues do periódico %s" % (enqueued_issues_counts, child['issn'])
        # para cada pid de artigos, enfileramos na queue certa:
        enqueued_articles_counts = 0
        for article_pid in articles_ids:
            r_queues.enqueue(stage, 'article', task_extract_article, collection.acronym, article_pid)
            enqueued_articles_counts += 1
        print u"enfilerados %s PIDs de artigos do periódico %s" % (enqueued_articles_counts, child['issn'])
