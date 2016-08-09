#!/usr/bin/python
# coding: utf-8

import sys
import signal
import textwrap
import optparse
import datetime
import logging.config
from uuid import uuid4
import multiprocessing
from multiprocessing import Pool

from mongoengine import connect

from opac_schema.v1 import models
from mongoengine import Q, DoesNotExist
from thrift_clients import clients

import config
import utils

articlemeta = clients.ArticleMeta(
    config.ARTICLE_META_THRIFT_DOMAIN,
    config.ARTICLE_META_THRIFT_PORT)

logger = logging.getLogger(__name__)

def init_worker():
    signal.signal(signal.SIGINT, signal.SIG_IGN)


def config_logging(logging_level='INFO', logging_file=None):

    allowed_levels = {
        'DEBUG': logging.DEBUG,
        'INFO': logging.INFO,
        'WARNING': logging.WARNING,
        'ERROR': logging.ERROR,
        'CRITICAL': logging.CRITICAL
    }

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    logger.setLevel(allowed_levels.get(logging_level, config.OPAC_PROC_LOG_LEVEL))

    if logging_file:
        hl = logging.FileHandler(logging_file, mode='a')
    else:
        hl = logging.StreamHandler()

    hl.setFormatter(formatter)
    hl.setLevel(allowed_levels.get(logging_level, 'INFO'))

    logger.addHandler(hl)

    return logger


def process_collection(collection):

    m_collection = models.Collection()
    m_collection._id = str(uuid4().hex)
    m_collection.acronym = collection.acronym
    m_collection.name = collection.name

    return m_collection.save()


def process_journal(issn_collection):

    issn, collection = issn_collection

    connect(**config.MONGODB_SETTINGS)

    try:
        journal = articlemeta.get_journal(collection=collection, code=issn)

        logger.info(u"Adicionando journal %s" % journal.title)

        m_journal = models.Journal()

        # We have to define which id will be use to legacy journals.
        _id = str(uuid4().hex)
        m_journal._id = _id
        m_journal.jid = _id

        m_journal.created = datetime.datetime.now()
        m_journal.updated = datetime.datetime.now()

        # Set collection
        collection = models.Collection.objects.get(
            acronym__iexact=journal.collection_acronym)
        m_journal.collection = collection

        m_journal.subject_categories = journal.subject_areas
        m_journal.study_areas = journal.wos_subject_areas
        m_journal.current_status = journal.current_status
        m_journal.publisher_city = journal.publisher_loc

        # Alterar no opac_schema, pois o xylose retorna uma lista e o opac_schema
        # aguarda um string.
        m_journal.publisher_name = journal.publisher_name[0]
        m_journal.eletronic_issn = journal.electronic_issn
        m_journal.scielo_issn = journal.scielo_issn
        m_journal.print_issn = journal.print_issn
        m_journal.acronym = journal.acronym
        m_journal.previous_title = journal.previous_title

        m_journal.title = journal.title
        m_journal.title_iso = journal.abbreviated_iso_title

        missions = []
        for lang, des in journal.mission.items():
            m = models.Mission()
            m.language = lang
            m.description = des
            missions.append(m)

        m_journal.mission = missions

        timelines = []
        for status in journal.status_history:
            timeline = models.Timeline()
            timeline.reason = status[2]
            timeline.status = status[1]

            # Corrigir datetime
            timeline.since = utils.trydate(status[0])
            timelines.append(timeline)

        m_journal.timeline = timelines
        m_journal.short_title = journal.abbreviated_title
        m_journal.index_at = journal.wos_citation_indexes
        m_journal.updated = utils.trydate(journal.update_date)
        m_journal.created = utils.trydate(journal.creation_date)
        m_journal.copyrighter = journal.copyrighter
        if journal.publisher_country:
            m_journal.publisher_country = journal.publisher_country[1]
        m_journal.online_submission_url = journal.submission_url
        m_journal.publisher_state = journal.publisher_state
        m_journal.sponsors = journal.sponsors

        if journal.other_titles:
            other_titles = []
            for title in journal.other_titles:
                t = models.OtherTitle()
                t.title = title
                t.category = "other"
                other_titles.append(t)

            m_journal.other_titles = other_titles

        m_journal.save()
    except Exception as e:
        logger.error(u"Exception %s. Processando Journal (ISSN: %s, Collection: %s)" % (
            str(e), issn, collection))


def process_issue(issn_collection):

    issn, collection = issn_collection

    connect(**config.MONGODB_SETTINGS)

    for issue in articlemeta.issues(collection=collection, issn=issn):

        m_issue = models.Issue()

        logger.info(u"Adicionando issue: %s - %s" % (issn, issue.label))

        # We have to define which id will be use to legacy journals.
        _id = str(uuid4().hex)
        m_issue._id = _id
        m_issue.iid = _id

        m_issue.created = datetime.datetime.now()
        m_issue.updated = datetime.datetime.now()

        m_issue.unpublish_reason = issue.publisher_id

        # Get Journal of the issue
        try:
            journal = models.Journal.objects.get(scielo_issn=issue.journal.scielo_issn)
            m_issue.journal = journal
        except Exception as e:
            logger.warning(u"Erro obtendo journal com ISSN: %s, Exception: %s" % (issue.journal.scielo_issn, str(e)))

        m_issue.volume = issue.volume
        m_issue.number = issue.number

        m_issue.type = issue.type

        m_issue.start_month = issue.start_month
        m_issue.end_month = issue.end_month
        m_issue.year = int(issue.publication_date[:4])

        m_issue.label = issue.label
        m_issue.order = issue.order

        m_issue.bibliographic_legend = '%s. vol.%s no.%s %s %s./%s. %s' % (issue.journal.abbreviated_title, issue.volume, issue.number, issue.journal.publisher_state, issue.start_month, issue.end_month, issue.publication_date[:4])

        m_issue.pid = issue.publisher_id

        m_issue.save()

    process_last_issue(issn)


def process_article(issn_collection):

    issn, collection = issn_collection

    connect(**config.MONGODB_SETTINGS)

    for article in articlemeta.articles(collection=collection, issn=issn):

        logger.info(u"Adicionando artigo: %s" % article.publisher_id)

        m_article = models.Article()

        _id = str(uuid4().hex)
        m_article._id = _id
        m_article.aid = _id

        try:
            issue = models.Issue.objects.get(pid=article.issue.publisher_id)
            m_article.issue = issue
        except DoesNotExist as e:
            logger.warning(u"Artigo SEM issue. publisher_id: %s" % str(article.publisher_id))
        except Exception as e:
            logger.error(u"Erro ao tentar acessar o atributo issue do artigo: %s, Erro %s" % (str(article.publisher_id), e))

        try:
            journal = models.Journal.objects.get(
                scielo_issn=article.journal.scielo_issn)
            m_article.journal = journal
        except Exception as e:
            logger.error(u"Erro: %s" % e)

        m_article.title = article.original_title()

        if article.translated_abstracts():
            m_article.abstract_languages = article.translated_abstracts().keys()

        if article.translated_section():
            translated_sections = []

            for lang, title in article.translated_section().items():
                translated_section = models.TranslatedSection()
                translated_section.language = lang
                translated_section.name = title
                translated_sections.append(translated_section)

            m_article.sections = translated_sections

        m_article.section = article.original_section()

        if article.translated_titles():
            translated_titles = []

            for lang, title in article.translated_titles().items():
                translated_title = models.TranslatedTitle()
                translated_title.language = lang
                translated_title.name = title
                translated_titles.append(translated_title)

            m_article.translated_titles = translated_titles

        try:
            m_article.order = int(article.order)
        except ValueError as e:
            logger.error(u'Ordenação inválida: %s-%s' % (e, article.publisher_id))

        htmls = []
        pdfs = []

        try:
            m_article.doi = article.doi
            m_article.is_aop = article.is_ahead_of_print

            m_article.created = datetime.datetime.now()
            m_article.updated = datetime.datetime.now()

            m_article.original_language = article.original_language()

            m_article.languages = list(set(article.languages() + m_article.abstract_languages))

            m_article.abstract = article.original_abstract()

            if article.authors:
                m_article.authors = ['%s, %s' % (author['surname'], author['given_names']) for author in article.authors]

            if article.fulltexts():
                for text, val in article.fulltexts().items():
                    if text == 'html':
                        for lang, url in val.items():
                            resource = models.Resource()
                            resource._id = str(uuid4().hex)
                            resource.type = 'html'
                            resource.language = lang
                            resource.url = url
                            resource.save()
                            htmls.append(resource)
                    if text == 'pdf':
                        for lang, url in val.items():
                            resource = models.Resource()
                            resource._id = str(uuid4().hex)
                            resource.type = 'pdf'
                            resource.language = lang
                            resource.url = url
                            resource.save()
                            pdfs.append(resource)

        except Exception as e:
            logger.error(u"Erro inesperado: %s, %s" % (article.publisher_id, e))
            continue

        m_article.htmls = htmls
        m_article.pdfs = pdfs

        m_article.pid = article.publisher_id

        m_article.save()


def process_last_issue(issn):

    logger.info("Cadastrando os últimos fascículos...")

    connect(**config.MONGODB_SETTINGS)

    # Get last issue for each Journal
    journal = models.Journal.objects.get(scielo_issn=issn)

    logger.info(u"Recuperando último fascículo journal: %s" % journal.title)

    issue = models.Issue.objects.filter(journal=journal).order_by('-year', '-order').first()
    issue_count = models.Issue.objects.filter(journal=journal).count()

    if issue:
        last_issue = articlemeta.get_issue(code=issue.pid)

        m_last_issue = models.LastIssue()
        m_last_issue.volume = last_issue.volume
        m_last_issue.number = last_issue.number
        m_last_issue.year = last_issue.publication_date[:4]
        m_last_issue.start_month = last_issue.start_month
        m_last_issue.end_month = last_issue.end_month
        m_last_issue.iid = issue.iid
        m_last_issue.bibliographic_legend = '%s. vol.%s no.%s %s %s./%s. %s' % (issue.journal.title_iso, issue.volume, issue.number, issue.journal.publisher_state, issue.start_month, issue.end_month, issue.year)

        if last_issue.sections:
            sections = []
            for code, items in last_issue.sections.iteritems():
                if items:
                    for k, v in items.iteritems():
                        section = models.TranslatedSection()
                        section.name = v
                        section.language = k
                sections.append(section)

            m_last_issue.sections = sections

        journal.last_issue = m_last_issue
        journal.issue_count = issue_count
        journal.save()
    else:
        logger.info(u"Impossível recuperar o último fascículo para o períodico: %s" % journal.title)


def bulk(options, pool):

    db = connect(**config.MONGODB_SETTINGS)
    db_name = config.MONGODB_SETTINGS['db']
    db.drop_database(db_name)
    logger.info(u"Banco de dado (%s) removido completamente!" % db_name)

    # Collection
    for col in articlemeta.collections():
        if col.acronym == options.collection:
            logger.info(u"Adicionado a coleção: %s" % options.collection)
            process_collection(col)

    # Get the number of ISSNs
    issns = [(journal.scielo_issn, options.collection) for journal in articlemeta.journals(collection=options.collection)]

    issns_list = utils.split_list(issns, options.process)

    for i, pissns in enumerate(issns_list):
        logger.info(u"Enviando para processamento os issns: %s" % pissns)
        pool.map(process_journal, pissns)
        pool.map(process_issue, pissns)
        pool.map(process_article, pissns)


def run(options, pool):

    logger.info(u'Coleção alvo: %s' % options.collection)
    logger.debug(u'Articles Meta API: %s, at port: %s', config.ARTICLE_META_THRIFT_DOMAIN, config.ARTICLE_META_THRIFT_PORT)
    if config.MONGODB_USER and config.MONGODB_PASS:
        logger.debug(u'Conexão e credenciais do banco: mongo://{username}:{password}@{host}:{port}/{db}'.format(**config.MONGODB_SETTINGS))
    else:
        logger.debug(u'Conexão sem credenciais do banco: mongo://{host}:{port}/{db}'.format(**config.MONGODB_SETTINGS))

    logger.debug(u'Nível do log: %s', options.logging_level)
    logger.debug(u'Arquivo de log: %s', options.logging_file)
    logger.debug(u'Número de processadores: %s', options.process)

    started = datetime.datetime.now()
    logger.info(u'Inicialização o processo: %s', started)

    bulk(options, pool)

    finished = datetime.datetime.now()
    logger.info(u'Finalização do processo: %s', finished)

    elapsed_time = str(finished - started)
    logger.info(u"Tempo total de processamento: %s sec." % elapsed_time)

    logger.info(U"Processamento finalizado com sucesso.")
    pool.close()
    pool.join()


def main(argv=sys.argv[1:]):
    """
    Processo para carregar dados desde o Article Meta para o MongoDB usado pelo OPAC
    """

    usage = u"""\
    %prog Este processamento coleta todos os Journal, Issues, Articles do Article meta,
    de uma determinada coleção, armazenando estes dados em um banco MongoDB,
    que serão exposto pelo OPAC.
    """

    parser = optparse.OptionParser(
        textwrap.dedent(usage), version=u"version: 1.0")

    # Arquivo de log
    parser.add_option(
        '--logging_file',
        '-o',
        default=config.OPAC_PROC_LOG_FILE_PATH,
        help=u'Caminho absoluto do log file')

    # Nível do log
    parser.add_option(
        '--logging_level',
        '-l',
        default=config.OPAC_PROC_LOG_LEVEL,
        choices=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL'],
        help=u'Nível do log')

    # Coleção
    parser.add_option(
        '-c', '--collection',
        dest='collection',
        default=config.OPAC_PROC_COLLECTION,
        help=u'Acronimo da coleção. Por exemplo: spa, scl, col.')

    # Número de processos
    parser.add_option(
        '-p', '--num_process',
        dest='process',
        default=multiprocessing.cpu_count(),
        help=u'Número de processadores, o recomendado é utilizar a quantidade de processadores disponíveis na máquina.')

    options, args = parser.parse_args(argv)

    config_logging(options.logging_level, options.logging_file)

    pool = Pool(options.process, init_worker)

    try:
        return run(options, pool)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")
        pool.terminate()
        pool.join()

if __name__ == '__main__':
    main(sys.argv)
