# coding: utf-8
import os
import sys

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.datastore.mongodb_connector import get_db_connection
from opac_proc.datastore import identifiers_models as idmodels
from opac_proc.source_sync.utils import MODEL_NAME_LIST


def delete_identifiers(model_name):
    if model_name not in MODEL_NAME_LIST:
        raise ValueError(u'parametro: model_name: %s não é válido!' % model_name)

    get_db_connection()
    if model_name == 'collection':
        model_class = idmodels.CollectionIdModel
    elif model_name == 'journal':
        model_class = idmodels.JournalIdModel
    elif model_name == 'issue':
        model_class = idmodels.IssueIdModel
    elif model_name == 'article':
        model_class = idmodels.ArticleIdModel
    elif model_name == 'news':
        model_class = idmodels.NewsIdModel
    elif model_name == 'press_release':
        model_class = idmodels.PressReleaseIdModel

    objects = model_class.objects()
    print "Removendo: %s objetos do modelo: %s" % (objects.count(), model_name)
    objects.delete()
    print "Objetos removidos com sucesso!"


def main(model_name):
    """ script para roda manualmente """
    print "main -> model_name: ", model_name
    process_all = model_name == 'delete_all'
    if process_all:
        for model in MODEL_NAME_LIST:
            print u"executando delete_identifiers do modelo: %s" % model
            delete_identifiers(model)
            print u"finalizada delete_identifiers do modelo: %s" % model
    else:
        print u"executando delete_identifiers do modelo: %s" % model_name
        delete_identifiers(model_name)
        print u"finalizada delete_identifiers do modelo: %s" % model_name

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "erro: falta indicar o modulo"
    main(sys.argv[1])
