# coding: utf-8
import os
import sys
import itertools
import unittest
from flask_script import Manager, Shell

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(PROJECT_PATH)

from articlemeta.client import ThriftClient

from opac_proc.web.webapp import create_app
from opac_proc.web.accounts.forms import EmailForm
from opac_proc.web.accounts.mixins import User as UserMixin
from opac_proc.web.accounts.models import User as UserModel

from opac_proc.datastore import models
from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore.redis_queues import RQueues
from opac_proc.extractors.jobs import (
    task_collection_create as ex_task_collection_create,
    task_journal_create as ex_task_journal_create,
    task_extract_issue as ex_task_extract_issue,
    task_extract_article as ex_task_extract_article)
from opac_proc.transformers.jobs import (
    task_collection_create as tr_task_collection_create,
    task_journal_create as tr_task_journal_create,
    task_transform_issue as tr_task_transform_issue,
    task_transform_article as tr_task_transform_article)
from opac_proc.loaders.jobs import (
    task_collection_create as lo_task_collection_create,
    task_journal_create as lo_task_journal_create,
    task_load_issue as lo_task_load_issue,
    task_load_article as lo_task_load_article)


app = create_app()
manager = Manager(app)


def make_shell_context():
    app_models = {}  # TODO: adicionar os modelos no contexto
    return dict(app=app, **app_models)
manager.add_command("shell", Shell(make_context=make_shell_context))


def _enqueue(collection, ids, stage, task, entity):
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    for _id in ids:
        if stage == 'load':
            r_queues.enqueue(stage, entity, task, _id)
        else:
            r_queues.enqueue(stage, entity, task, collection.acronym, _id)

    return r_queues.queues[stage][entity]


def process_issue(collection, stage, task, issns=None, issue_ids=None):

    if bool(issns) == bool(issue_ids):
        raise(u'Utilizar apenas ``issns`` ou apenas ``issue_ids``')

    if issns:

        children_found = [child for child in collection['children_ids'] if child['issn'] in issns]

        for child in children_found:

            if stage == 'load':
                ids = models.TransformIssue.objects.filter(pid__contains=child['issn']).values_list('uuid')
            else:
                ids = child['issues_ids']

            print u"Processando %s pids de issues do periódicoL %s" % (len(ids), child['issn'])

            queued_issue = _enqueue(collection, ids, stage, task, 'issue')

    if issue_ids:

        queued_issue = _enqueue(collection, issue_ids, stage, task, 'issue')

    print u"Enfilerados %s pids de issue" % (len(queued_issue))


def process_article(collection, stage, task, issns=None, article_ids=None):

    if bool(issns) == bool(article_ids):
        raise(u'Utilizar apenas ``issns`` ou apenas ``article_ids``')

    if issns:

        children_found = [child for child in collection['children_ids'] if child['issn'] in issns]

        for child in children_found:

            if stage == 'load':
                ids = models.TransformIssue.objects.filter(pid__contains=child['issn']).values_list('uuid')
            else:
                ids = child['articles_ids']

            print u"Processando %s pids de artigos do periódico: %s" % (len(ids), child['issn'])

            queued_issue = _enqueue(collection, ids, stage, task, 'article')

    if article_ids:

        queued_issue = _enqueue(collection, article_ids, stage, task, 'article')

    print u"Enfilerados %s pids de artigo" % (len(queued_issue))


def process_issn_issue(collection, issns, task_issue, stage):

    children_ids = collection['children_ids']  # all ids in database

    db_issns = [child['issn'] for child in children_ids]  # all issns in database

    print u"Lista de ISSNs: %s" % db_issns

    issn_found = [issn for issn in db_issns if issn in issns]  # issns to process

    print u"ISSNs encontrados: %s" % issn_found

    process_issue(collection, stage, task_issue, issns=issn_found)


def process_issn_article(collection, issns, task_article, stage):

    children_ids = collection['children_ids']  # all ids in database

    db_issns = [child['issn'] for child in children_ids]  # all issns in database

    print u"Lista de ISSNs: %s" % db_issns

    issn_found = [issn for issn in db_issns if issn in issns]  # issns to process

    print u"ISSNs encontrados: %s" % issn_found

    process_article(collection, stage, task_article, issns=issn_found)


def get_issn_by_acron(collection, acron):

    cl = ThriftClient()

    for journal in cl.journals(collection=collection):

        if journal.acronym == acron:
            return journal.scielo_issn


def get_issns_by_acrons(collection, acrons):
    issn_list = []

    cl = ThriftClient()

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

    cl = ThriftClient()

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

    cl = ThriftClient()

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
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
@manager.option('-f', '--file', dest='file')
def process_extract(issns=None, acrons=None, file=None):
    stage = 'extract'

    if bool(issns) == bool(acrons) == bool(file):
        sys.exit(u'Utilizar apenas ``issns`` ou apenas ``acrônimos`` ou apenas ``file``, param: -a ou -i ou -f')

    collection = models.ExtractCollection.objects.all().first()

    print u'Colecão que será carregada: %s' % collection.name

    ex_task_collection_create()

    ex_task_journal_create()

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection.acronym,
                                        acrons=clean_acrons)

    if issns:
        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    if issns or acrons:
        print u'Processando o(s) ISSN(s): %s' % issn_list

        process_issn_issue(collection, issn_list, stage, ex_task_extract_issue)

        process_issn_article(collection, issn_list, stage, ex_task_extract_article)

    if file:
        items = get_file_items(collection.acronym, file)

        ids_issue_dict = issue_labels_to_ids(collection.acronym, items)

        process_issue(collection, stage, ex_task_extract_issue, issue_ids=list(itertools.chain(*ids_issue_dict.values())))

        ids_article_dict = issue_ids_to_article_ids(collection.acronym, ids_issue_dict)

        process_article(collection, stage, ex_task_extract_article, article_ids=list(itertools.chain(*ids_article_dict.values())))


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
@manager.option('-f', '--file', dest='file')
def process_transform(issns=None, acrons=None, file=None):
    stage = 'transform'

    if bool(issns) == bool(acrons) == bool(file):
        sys.exit(u'Utilizar apenas ``issns`` ou apenas ``acrônimos`` ou apenas ``file``, param: -a ou -i ou -f')

    collection = models.TransformCollection.objects.all().first()

    print u'Colecão que será tranformada: %s' % collection.name

    tr_task_collection_create()

    tr_task_journal_create()

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection.acronym,
                                        acrons=clean_acrons)

    if issns:
        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    if issns or acrons:
        print u'Processando o(s) ISSN(s): %s' % issn_list

        process_issn_issue(collection, issn_list, stage, tr_task_transform_issue)

        process_issn_article(collection, issn_list, stage, tr_task_transform_article)

    if file:
        items = get_file_items(collection.acronym, file)

        ids_issue_dict = issue_labels_to_ids(collection.acronym, items)

        process_issue(collection, stage, tr_task_transform_issue, issue_ids=list(itertools.chain(*ids_issue_dict.values())))

        ids_article_dict = issue_ids_to_article_ids(collection.acronym, ids_issue_dict)

        process_article(collection, stage, tr_task_transform_article, article_ids=list(itertools.chain(*ids_article_dict.values())))


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
@manager.option('-f', '--file', dest='file')
def process_load(issns=None, acrons=None, file=None):
    stage = 'load'

    if bool(issns) == bool(acrons) == bool(file):
        sys.exit(u'Utilizar apenas ``issns`` ou apenas ``acrônimos`` ou apenas ``file``, param: -a ou -i ou -f')

    collection = models.TransformCollection.objects.all().first()

    print u'Colecão que será carregada: %s' % collection.name

    lo_task_collection_create()

    lo_task_journal_create()

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection.acronym,
                                        acrons=clean_acrons)

    if issns:
        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    if issns or acrons:
        print u'Processando o(s) ISSN(s): %s' % issn_list

        process_issn_issue(collection, issn_list, stage, lo_task_load_issue)

        process_issn_article(collection, issn_list, stage, lo_task_load_article)

    if file:
        items = get_file_items(collection.acronym, file)

        ids_issue_dict = issue_labels_to_ids(collection.acronym, items)

        issue_list = list(itertools.chain(*ids_issue_dict.values()))

        issues_ids = models.TransformIssue.objects.filter(pid__contains=issue_list).values_list('uuid')

        process_issue(collection, stage, lo_task_load_issue, issue_ids=issues_ids)

        ids_article_dict = issue_ids_to_article_ids(collection.acronym, ids_issue_dict)

        article_list = list(itertools.chain(*ids_article_dict.values()))

        article_ids = models.TransformArticle.objects.filter(pid__contains=article_list).values_list('uuid')

        process_article(collection, stage, lo_task_load_article, article_ids=article_ids)


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
