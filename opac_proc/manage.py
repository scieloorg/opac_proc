# coding: utf-8
import os
import sys
import itertools
import unittest
from flask_script import Manager, Shell

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(PROJECT_PATH)

from articlemeta.client import ThriftClient

from opac_proc.web.config import (
    OPAC_PROC_COLLECTION,
    ARTICLE_META_THRIFT_DOMAIN,
    ARTICLE_META_THRIFT_PORT,
    ARTICLE_META_REST_DOMAIN,
    ARTICLE_META_REST_PORT)

from opac_proc.web.webapp import create_app
from opac_proc.web.accounts.forms import EmailForm
from opac_proc.web.accounts.mixins import User as UserMixin
from opac_proc.web.accounts.models import User as UserModel

from opac_proc.source_sync.ids_data_retriever_jobs import task_call_data_retriver_by_model

from opac_proc.extractors.jobs import (
    task_extract_one_collection,
    task_extract_selected_journals,
    task_extract_selected_issues,
    task_extract_selected_articles)

from opac_proc.transformers.jobs import (
    task_transform_one_collection,
    task_transform_selected_journals,
    task_transform_selected_issues,
    task_transform_selected_articles)

from opac_proc.loaders.jobs import (
    task_load_one_collection,
    task_load_selected_journals,
    task_load_selected_issues,
    task_load_selected_articles)

from opac_proc.datastore.identifiers_models import (
    CollectionIdModel,
    JournalIdModel,
    IssueIdModel,
    ArticleIdModel)

app = create_app()
manager = Manager(app)


def make_shell_context():
    app_models = {}  # TODO: adicionar os modelos no contexto
    return dict(app=app, **app_models)
manager.add_command("shell", Shell(make_context=make_shell_context))


def get_issn_by_acron(collection, acron):

    domain = "%s:%s" % (ARTICLE_META_THRIFT_DOMAIN,
                        ARTICLE_META_THRIFT_PORT)

    cl = ThriftClient(domain)

    for journal in cl.journals(collection=collection):

        if journal.acronym == acron:
            return journal.scielo_issn


def get_issns_by_acrons(collection, acrons):
    issn_list = []

    domain = "%s:%s" % (ARTICLE_META_THRIFT_DOMAIN,
                        ARTICLE_META_THRIFT_PORT)

    cl = ThriftClient(domain)

    acrons = set(acrons)

    for journal in cl.journals(collection=collection):

        if not acrons:
            break

        if journal.acronym in acrons:
            acrons.remove(journal.acronym)
            issn_list.append(journal.scielo_issn)

    return issn_list


def get_file_items(collection, file):
    """
        Return a dictionary, like:

        {'issn':set([issue_label, issue_label]),
         'issn':set([issue_label, issue_label]),
         'issn':set([issue_label, issue_label])}

    """
    data_dict = {}

    with open(file) as fp:

        lines = [line.strip() for line in fp if len(line.strip())]

    for line in lines:
        key, val = line.split()

        d = data_dict.setdefault(get_issn_by_acron(collection, key), set())

        d.add(val)

    return data_dict


def issue_labels_to_ids(collection, items):
    """
        Return a dictionary, like:

        {'issn':set([id, id]),
         'issn':set([id, id]),
         'issn':set([id, id])}
    """

    data_dict = {}

    domain = "%s:%s" % (ARTICLE_META_THRIFT_DOMAIN,
                        ARTICLE_META_THRIFT_PORT)

    cl = ThriftClient(domain)

    for issn, labels in items.items():
        d = data_dict.setdefault(issn, set())
        for label in labels:
            code = cl.get_issue_code_from_label(label, issn, collection)
            if code:
                d.add(code)

    return data_dict


def issue_ids_to_article_ids(collection, items):
    """
        Return a dictionary, like:

        {'issn':[pid, pid, ...]),
         'issn':[pid, pid, ...]),
         'issn':[pid, pid, ...])}
    """

    data_dict = {}

    domain = "%s:%s" % (ARTICLE_META_THRIFT_DOMAIN,
                        ARTICLE_META_THRIFT_PORT)

    cl = ThriftClient(domain)

    for issn, icodes in items.items():
        d = data_dict.setdefault(issn, [])
        for icode in icodes:
            for code in cl.documents(collection=collection,
                                     only_identifiers=True,
                                     extra_filter='{"code_issue":"%s"}' % icode):
                if code:
                    d.append(code.code)

    return data_dict


@manager.command
def process_ids():
    """
    Coleta todos os identifiers de: collection, journal, issue e artigo de forma sincrona
    """
    task_call_data_retriver_by_model(model='collection', force_serial=True)
    task_call_data_retriver_by_model(model='journal', force_serial=True)
    task_call_data_retriver_by_model(model='issue', force_serial=True)
    task_call_data_retriver_by_model(model='article', force_serial=True)


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
@manager.option('-f', '--file', dest='file')
def process_extract(issns=None, acrons=None, file=None):

    if bool(issns) == bool(acrons) == bool(file):
        sys.exit(u'Utilizar apenas ``issns`` ou apenas ``acrônimos`` ou apenas ``file``, param: -a ou -i ou -f')

    task_extract_one_collection()

    collection = OPAC_PROC_COLLECTION

    print u'Colecão que será carregada: %s' % collection

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection,
                                        acrons=clean_acrons)

    if issns:
        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    if issns or acrons:
        print u'Processando o(s) ISSN(s): %s' % issn_list

        journal_uuids = JournalIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        task_extract_selected_journals(journal_uuids)

        issue_uuids = IssueIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        print u'Processando %s issues' % len(issue_uuids)
        task_extract_selected_issues(issue_uuids)

        article_uuids = ArticleIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        print u'Processando %s artigos' % len(article_uuids)
        task_extract_selected_articles(article_uuids)

    if file:

        items = get_file_items(collection, file)
        ids_issue_dict = issue_labels_to_ids(collection, items)
        issn_list = ids_issue_dict.keys()
        print u'Processando o(s) ISSN(s): %s' % issn_list

        journal_uuids = JournalIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        task_extract_selected_journals(journal_uuids)

        issue_ids = list(itertools.chain(*ids_issue_dict.values()))
        issue_uuids = IssueIdModel.objects.filter(issue_pid__in=issue_ids).values_list('uuid')
        print u'Processando %s issues' % len(issue_uuids)
        task_extract_selected_issues(issue_uuids)

        ids_article_dict = issue_ids_to_article_ids(collection, ids_issue_dict)
        article_ids = list(itertools.chain(*ids_article_dict.values()))
        article_uuids = ArticleIdModel.objects.filter(article_pid__in=article_ids).values_list('uuid')
        print u'Processando %s artigos' % len(article_uuids)
        task_extract_selected_articles(article_uuids)


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
@manager.option('-f', '--file', dest='file')
def process_transform(issns=None, acrons=None, file=None):

    if bool(issns) == bool(acrons) == bool(file):
        sys.exit(u'Utilizar apenas ``issns`` ou apenas ``acrônimos`` ou apenas ``file``, param: -a ou -i ou -f')

    task_transform_one_collection()

    collection = OPAC_PROC_COLLECTION

    print u'Colecão que será carregada: %s' % collection

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection,
                                        acrons=clean_acrons)

    if issns:
        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    if issns or acrons:
        print u'Processando o(s) ISSN(s): %s' % issn_list

        journal_uuids = JournalIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        task_transform_selected_journals(journal_uuids)

        issue_uuids = IssueIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        print u'Processando %s issues' % len(issue_uuids)
        task_transform_selected_issues(issue_uuids)

        article_uuids = ArticleIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        print u'Processando %s artigos' % len(article_uuids)
        task_transform_selected_articles(article_uuids)

    if file:

        items = get_file_items(collection, file)
        ids_issue_dict = issue_labels_to_ids(collection, items)
        issn_list = ids_issue_dict.keys()
        print u'Processando o(s) ISSN(s): %s' % issn_list

        journal_uuids = JournalIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        task_transform_selected_journals(journal_uuids)

        issue_ids = list(itertools.chain(*ids_issue_dict.values()))
        issue_uuids = IssueIdModel.objects.filter(issue_pid__in=issue_ids).values_list('uuid')
        print u'Processando %s issues' % len(issue_uuids)
        task_transform_selected_issues(issue_uuids)

        ids_article_dict = issue_ids_to_article_ids(collection, ids_issue_dict)
        article_ids = list(itertools.chain(*ids_article_dict.values()))
        article_uuids = ArticleIdModel.objects.filter(article_pid__in=article_ids).values_list('uuid')
        print u'Processando %s artigos' % len(article_uuids)
        task_transform_selected_articles(article_uuids)


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
@manager.option('-f', '--file', dest='file')
def process_load(issns=None, acrons=None, file=None):

    if bool(issns) == bool(acrons) == bool(file):
        sys.exit(u'Utilizar apenas ``issns`` ou apenas ``acrônimos`` ou apenas ``file``, param: -a ou -i ou -f')

    collection = OPAC_PROC_COLLECTION

    collection_uuid = CollectionIdModel.objects.get(collection_acronym=collection).uuid

    task_load_one_collection(collection_uuid)

    print u'Colecão que será carregada: %s' % collection

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection,
                                        acrons=clean_acrons)

    if issns:
        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    if issns or acrons:
        print u'Processando o(s) ISSN(s): %s' % issn_list

        journal_uuids = JournalIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        task_load_selected_journals(journal_uuids)

        issue_uuids = IssueIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        print u'Processando %s issues' % len(issue_uuids)
        task_load_selected_issues(issue_uuids)

        article_uuids = ArticleIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        print u'Processando %s artigos' % len(article_uuids)
        task_load_selected_articles(article_uuids)

    if file:

        items = get_file_items(collection, file)
        ids_issue_dict = issue_labels_to_ids(collection, items)
        issn_list = ids_issue_dict.keys()
        print u'Processando o(s) ISSN(s): %s' % issn_list

        journal_uuids = JournalIdModel.objects.filter(journal_issn__in=issn_list).values_list('uuid')
        task_load_selected_journals(journal_uuids)

        issue_ids = list(itertools.chain(*ids_issue_dict.values()))
        issue_uuids = IssueIdModel.objects.filter(issue_pid__in=issue_ids).values_list('uuid')
        print u'Processando %s issues' % len(issue_uuids)
        task_load_selected_issues(issue_uuids)

        ids_article_dict = issue_ids_to_article_ids(collection, ids_issue_dict)
        article_ids = list(itertools.chain(*ids_article_dict.values()))
        article_uuids = ArticleIdModel.objects.filter(article_pid__in=article_ids).values_list('uuid')
        print u'Processando %s artigos' % len(article_uuids)
        task_load_selected_articles(article_uuids)


@manager.command
@manager.option('-p', '--pattern', dest='pattern')
@manager.option('-f', '--failfast', dest='failfast')
def test(pattern='test_*.py', failfast=False):
    app = create_app(test_mode=True)
    failfast = True if failfast else False
    tests = unittest.TestLoader().discover('tests', pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2, failfast=failfast).run(tests)
    if result.wasSuccessful():
        return sys.exit()
    else:
        return sys.exit(1)


@manager.command
def create_superuser():
    """
    Cria um novo usuário a partir dos dados inseridos na linha de comandos.
    Para criar um novo usuário é necessario preencher:
    - email (deve ser válido é único, se já existe outro usuário com esse email deve inserir outro);
    - senha (modo echo off)
    O usuário criado esta com email confirmado e ativo.
    """
    user_email = None
    user_password = None

    while user_email is None:
        user_email = raw_input(u'Email: ').strip()
        if user_email == '':
            user_email = None
            print u'Email não pode ser vazio'
        else:
            form = EmailForm(data={'email': user_email}, csrf_enabled=False)
            if not form.validate():
                user_email = None
                print u'Deve inserir um email válido!'

            if UserModel.objects.filter(email=user_email).count() > 0:
                user_email = None
                print u'Já existe outro usuário com esse email!'

    os.system("stty -echo")
    while user_password is None:
        user_password = raw_input('Senha: ').strip()
        if user_password == '':
            user_password = None
            print u'Senha não pode ser vazio'
    os.system("stty echo")

    # criamos o usuario
    try:
        password_hash = UserMixin.generate_password_hash(user_password)
        user = UserMixin(user_email, password_hash, email_confirmed=True)
        user.save()
    except Exception as e:
        print u'\n\n!!! Ocorreu um erro na criação do usuário. Erro: %s ***\n' % str(e)
    else:
        print u'\n\n*** Novo usuário criado com sucesso! ***\n'


if __name__ == "__main__":
    manager.run()
