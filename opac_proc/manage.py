# coding: utf-8
import os
import sys
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


def process_issue_article(collection, issns, stage, task_issue, task_article):
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    search_issn = [child['issn'] for child in collection['children_ids']]

    print u"Lista de ISSNs: %s" % search_issn

    children_found = [child for child in collection['children_ids'] if child['issn'] in issns]

    print u"ISSNs encontrados: %s" % [child['issn'] for child in children_found]

    for child in children_found:

        # children_ids, pegamos os articles_ids e issues_ids
        if stage == 'load':
            issues_ids = models.TransformIssue.objects.filter(pid__contains=child['issn']).values_list('uuid')
            articles_ids = models.TransformArticle.objects.filter(pid__contains=child['issn']).values_list('uuid')
        else:
            articles_ids = child['articles_ids']
            issues_ids = child['issues_ids']

        print u"Processando %s pids de issues do periódico %s" % (len(issues_ids), child['issn'])
        print u"Processando %s pids de artigos do periódico %s" % (len(articles_ids), child['issn'])

        # para cada pid de issues, enfileramos na queue certa:
        for issue_pid in issues_ids:
            if stage == 'load':
                r_queues.enqueue(stage, 'issue', task_issue, issue_pid)
            else:
                r_queues.enqueue(stage, 'issue', task_issue, collection.acronym, issue_pid)
        print u"Enfilerados %s PIDs de issues do periódico %s" % (len(r_queues.queues[stage]['issue']), child['issn'])

        # para cada pid de artigos, enfileramos na queue certa:
        for article_pid in articles_ids:
            if stage == 'load':
                r_queues.enqueue(stage, 'article', task_article, article_pid)
            else:
                r_queues.enqueue(stage, 'article', task_article, collection.acronym, article_pid)
        print u"Enfilerados %s PIDs de artigos do periódico %s" % (len(r_queues.queues[stage]['article']), child['issn'])


def process_issue_article_by_file(collection, issns, stage, task_issue, task_article):
    r_queues = RQueues()
    r_queues.create_queues_for_stage(stage)

    cl = ThriftClient()

    search_issn = [child['issn'] for child in collection['children_ids']]

    print u"Lista de ISSNs: %s" % search_issn

    issn_keys = []

    for item in issns:
        for k in item.keys():
            issn_keys.append(k)

    children_found = [child for child in collection['children_ids'] if child['issn'] in issn_keys]

    print u"ISSNs encontrados: %s" % [child['issn'] for child in children_found]

    for item in issns:

        issues_ids = []

        for issn, issue_label in item.iteritems():

            issues = cl.issues(issn=issn, collection=collection.acronym)

            for id, issue in issues:
                if issue.label == issue_label:
                    issues_ids.append(issue)

            # children_ids, pegamos os articles_ids e issues_ids
            if stage == 'load':
                issues_ids = models.TransformIssue.objects.filter(pid__contains=issn).values_list('uuid')
                articles_ids = models.TransformArticle.objects.filter(pid__contains=issn).values_list('uuid')
            else:
                articles_ids = child['articles_ids']
                issues_ids = child['issues_ids']

            print u"Processando %s pids de issues do periódico %s" % (len(issues_ids), issn)
            print u"Processando %s pids de artigos do periódico %s" % (len(articles_ids), issn)

            # para cada pid de issues, enfileramos na queue certa:
            for issue_pid in issues_ids:
                if stage == 'load':
                    r_queues.enqueue(stage, 'issue', task_issue, issue_pid)
                else:
                    r_queues.enqueue(stage, 'issue', task_issue, collection.acronym, issue_pid)
            print u"Enfilerados %s PIDs de issues do periódico %s" % (len(r_queues.queues[stage]['issue']), issn)

            # para cada pid de artigos, enfileramos na queue certa:
            for article_pid in articles_ids:
                if stage == 'load':
                    r_queues.enqueue(stage, 'article', task_article, article_pid)
                else:
                    r_queues.enqueue(stage, 'article', task_article, collection.acronym, article_pid)
            print u"Enfilerados %s PIDs de artigos do periódico %s" % (len(r_queues.queues[stage]['article']), issn)


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


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
def process_extract(issns=None, acrons=None):
    stage = 'extract'

    if bool(issns) == bool(acrons):
        sys.exit(u'Utilizar apenas issns ou apenas acrônimos, param: -a ou -i')

    collection = models.ExtractCollection.objects.all().first()

    print u'Colecão que será carregada: %s' % collection.name

    ex_task_collection_create()

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection.acronym,
                                        acrons=clean_acrons)

    if issns:

        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    print u'Processando o(s) ISSN(s): %s' % issn_list

    ex_task_journal_create()

    process_issue_article(collection, issn_list, stage, ex_task_extract_issue, ex_task_extract_article)


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
def process_transform(issns=None, acrons=None):
    stage = 'transform'

    if bool(issns) == bool(acrons):
        sys.exit(u'Utilizar apenas issns ou apenas acrônimos, param: -a ou -i')

    collection = models.TransformCollection.objects.all().first()

    print u'Colecão que será tranformada: %s' % collection.name

    tr_task_collection_create()

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection.acronym,
                                        acrons=clean_acrons)

    if issns:

        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    print u'Processando o(s) ISSN(s): %s' % issn_list

    tr_task_journal_create()

    process_issue_article(collection, issn_list, stage, tr_task_transform_issue, tr_task_transform_article)


@manager.command
@manager.option('-a', '--acrons', dest='acrons')
@manager.option('-i', '--issns', dest='issns')
def process_load(issns=None, acrons=None):
    stage = 'load'

    if bool(issns) == bool(acrons):
        sys.exit(u'Utilizar apenas issns ou apenas acrônimos, param: -a ou -i')

    collection = models.TransformCollection.objects.all().first()

    print u'Colecão que será carregada: %s' % collection.name

    lo_task_collection_create()

    issn_list = []

    if acrons:
        clean_acrons = [i.strip() for i in acrons.split(',')]  # Gerando a lista com Acrônimos

        issn_list = get_issns_by_acrons(collection=collection.acronym,
                                        acrons=clean_acrons)

    if issns:

        issn_list = [i.strip() for i in issns.split(',')]  # Gerando a lista com ISSNs

    print u'Processando o(s) ISSN(s): %s' % issn_list

    lo_task_journal_create()

    process_issue_article(collection, issn_list, stage, lo_task_load_issue, lo_task_load_article)


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
