# coding: utf-8
import os
import sys
from dateutil import parser

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../'))
sys.path.append(PROJECT_PATH)

from opac_proc.extractors.source_clients.thrift import am_clients
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.extractors import jobs

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger
from opac_proc.core.notifications import (
    # create_default_msg,
    create_error_msg,
    # create_warning_msg,
    create_info_msg,
    # create_debug_msg,
)


if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "extract")
else:
    logger = getMongoLogger(__name__, "INFO", "extract")


class BaseExtractDiffHandler(object):
    query_filters = {}
    db = None
    client = None
    metadata = {}
    stage = 'extract'
    model_name = ''  # deve ser definido na subclase

    def __init__(self, query_filters=None):
        self.query_filters = query_filters or {}
        self.db = get_db_connection()
        self.am_client = am_clients.ArticleMeta(
            config.ARTICLE_META_THRIFT_DOMAIN,
            config.ARTICLE_META_THRIFT_PORT)
        if not self.model_name:
            raise AttributeError('Deve indicar o atributo: "model_name" na subclasse')

    def pre_processing(self):
        """
        Método chamado logo no inicio de começar o processamento (método process)
        """
        msg = u"A coleta parcial de {stage}->{model} foi iniciada agora".format(
            stage=self.stage, model=self.model_name)
        app_msg = create_info_msg(msg, msg, self.stage, self.model_name)
        app_msg.send_email()

    def post_processing(self):
        """
        Método chamado logo após finalizar o processamento (método process)
        """
        msg = u"A coleta parcial de {stage}->{model} finalizou agora".format(
            stage=self.stage, model=self.model_name)
        app_msg = create_info_msg(msg, msg, self.stage, self.model_name)
        app_msg.send_email()

    def collect_diff_data(self):
        """
        Conecta com a fonte de dados para extrair os dados novos (add|update|delete)
        Retorna um iterável de dict com os dados novos. Pode ser um gerador, que
        sera consumido no método process
        """
        raise NotImplementedError

    def process_add_action(self, item):
        """
        Tratamendo de um item ADICIONADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        raise NotImplementedError

    def process_update_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        raise NotImplementedError

    def process_delete_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        raise NotImplementedError

    def process(self):
        """
        Método chamado pelo DiffController correspondente,
        que orquestra toda a extração de cada modelo
        """
        self.pre_processing()
        # chamar collect_diff_data para pegar os dados e iterar sobre os dados coletados
        collected_data = self.collect_diff_data()
        for data_item in collected_data:
            print "collected event doc:", data_item
            action = data_item['event'].lower()
            if action == 'add':
                self.process_add_action(data_item)
            elif action == 'update':
                self.process_update_action(data_item)
            elif action == 'delete':
                self.process_delete_action(data_item)
            else:
                # melhorar com notifiação que do erro, e continuar com o resto do iterável
                raise RuntimeError('unexpected action: %s' % action)
        self.post_processing()


class ExtractCollectionDiffHandler(BaseExtractDiffHandler):
    stage = 'extract'
    model_name = 'collection'

    def process(self):
        """
        Método chamado pelo DiffController correspondente,
        que orquestra toda a extração de cada modelo
        ---------------------------------------------------------
        Como a coleção é um caso particular, tratamos diferente:
        1. chamamos o método: self.pre_processing()
        2. invocamos a task: task_collection_update() para atualizar (chamado síncrona)
        3. chamamos o método: self.post_processing()
        Chamamos a task: task_collection_update de forma syncrona
        """
        self.pre_processing()
        jobs.task_extract_collection()
        self.post_processing()


class ExtractJournalDiffHandler(BaseExtractDiffHandler):
    stage = 'extract'
    model_name = 'journal'

    def collect_diff_data(self):
        self.query_filters = {
            'collection': config.OPAC_PROC_COLLECTION,
            'from_date': None,
            'until_date': None,
        }
        return self.am_client.journal_history_changes(**self.query_filters)

    def process_add_action(self, item):
        """
        Tratamendo de um item ADICIONADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_add_action > code" % self.model_name, item['code']

    def process_update_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_update_action > code" % self.model_name, item['code']

    def process_delete_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_delete_action > code" % self.model_name, item['code']


class ExtractIssueDiffHandler(BaseExtractDiffHandler):
    stage = 'extract'
    model_name = 'issue'

    def collect_diff_data(self):
        self.query_filters = {
            'collection': config.OPAC_PROC_COLLECTION,
            'from_date': None,
            'until_date': None,
        }
        return self.am_client.issue_history_changes(**self.query_filters)

    def process_add_action(self, item):
        """
        Tratamendo de um item ADICIONADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_add_action > code" % self.model_name, item['code']

    def process_update_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_update_action > code" % self.model_name, item['code']

    def process_delete_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_delete_action > code" % self.model_name, item['code']


class ExtractArticleDiffHandler(BaseExtractDiffHandler):
    stage = 'extract'
    model_name = 'article'

    def collect_diff_data(self):
        self.query_filters = {
            'collection': config.OPAC_PROC_COLLECTION,
            'from_date': None,
            'until_date': None,
        }
        return self.am_client.article_history_changes(**self.query_filters)

    def process_add_action(self, item):
        """
        Tratamendo de um item ADICIONADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_add_action > code" % self.model_name, item['code']

    def process_update_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_update_action > code" % self.model_name, item['code']

    def process_delete_action(self, item):
        """
        Tratamendo de um item MODIFICADO.
        Geralmente esse novo dado é recuperado e enfilerado para ser processado
        pela subclasse do BaseExtractor, num rq-worker
        """
        print "[%s] process_delete_action > code" % self.model_name, item['code']


class ExtractPressReleaseDiffHandler(BaseExtractDiffHandler):
    stage = 'extract'
    model_name = 'press_release'

    def process(self):
        """
        Método chamado pelo DiffController correspondente,
        que orquestra toda a extração de cada modelo
        ---------------------------------------------------------
        Como a coleção é um caso particular, tratamos diferente:
        1. chamamos o método: self.pre_processing()
        2. invocamos a task: task_collection_update() para atualizar (chamado síncrona)
        3. chamamos o método: self.post_processing()
        Chamamos a task: task_collection_update de forma syncrona
        """
        self.pre_processing()
        jobs.task_press_release_create()
        self.post_processing()


class ExtractNewsDiffHandler(BaseExtractDiffHandler):
    stage = 'extract'
    model_name = 'news'

    def process(self):
        """
        Método chamado pelo DiffController correspondente,
        que orquestra toda a extração de cada modelo
        ---------------------------------------------------------
        Como a coleção é um caso particular, tratamos diferente:
        1. chamamos o método: self.pre_processing()
        2. invocamos a task: task_collection_update() para atualizar (chamado síncrona)
        3. chamamos o método: self.post_processing()
        Chamamos a task: task_collection_update de forma syncrona
        """
        self.pre_processing()
        jobs.task_press_release_create()
        self.post_processing()


class DiffController(object):
    # Controla o process de extração das diferencias
    collection_acronym = config.OPAC_PROC_COLLECTION

    def extract_collection_diff(self):
        # coletar histórico de mudança da coleção
        handler_class = ExtractCollectionDiffHandler()
        handler_class.process()

    def extract_journal_diff(self):
        # coletar histórico de mudança de journals
        handler_class = ExtractJournalDiffHandler()
        handler_class.process()

    def extract_issue_diff(self):
        # coletar histórico de mudança de issues
        handler_class = ExtractIssueDiffHandler()
        handler_class.process()

    def extract_article_diff(self):
        # coletar histórico de mudança de articles
        handler_class = ExtractArticleDiffHandler()
        handler_class.process()

    def extract_pressrelease_diff(self):
        # coletar histórico de mudança de pressrelease
        handler_class = ExtractPressReleaseDiffHandler()
        handler_class.process()

    def extract_news_diff(self):
        # coletar histórico de mudança de news
        handler_class = ExtractNewsDiffHandler()
        handler_class.process()

    def run(self):
        # dispara signal: "on_ready"

        # dispara signal: "collection diff started"
        self.extract_collection_diff()
        # dispara signal: "collection diff finished"

        # dispara signal: "journal diff started"
        self.extract_journal_diff()
        # dispara signal: "journal diff finished"

        # dispara signal: "issue diff started"
        self.extract_issue_diff()
        # dispara signal: "issue diff finished"

        # dispara signal: "article diff started"
        self.extract_article_diff()
        # dispara signal: "article diff finished"

        # dispara signal: "pressrelease diff started"
        self.extract_pressrelease_diff()
        # dispara signal: "pressrelease diff finished"

        # dispara signal: "extract_news_diff diff started"
        self.extract_news_diff()
        # dispara signal: "extract_news_diff diff finished"

        # dispara signal: "on_complete"


if __name__ == '__main__':
    controller = DiffController()
    controller.run()
