# coding: utf-8
from opac_proc.datastore import models as proc_models
from opac_proc.datastore import identifiers_models as id_models
from opac_proc.datastore import diff_models as diff_models
from .base import DifferBase


# --------------------------------------------------- #
#                   COLLECTION                        #
# --------------------------------------------------- #


class CollectionDiffer(DifferBase):
    model_name = 'collection'
    ex_model_class = proc_models.ExtractCollection
    tr_model_class = proc_models.TransformCollection
    lo_model_class = proc_models.LoadCollection
    id_model_class = id_models.CollectionIdModel
    diff_model_class = diff_models.CollectionDiffModel


# --------------------------------------------------- #
#                   JOURNALS                          #
# --------------------------------------------------- #


class JournalDiffer(DifferBase):
    model_name = 'journal'
    ex_model_class = proc_models.ExtractJournal
    tr_model_class = proc_models.TransformJournal
    lo_model_class = proc_models.LoadJournal
    id_model_class = id_models.JournalIdModel
    diff_model_class = diff_models.JournalDiffModel


# --------------------------------------------------- #
#                   ISSUES                            #
# --------------------------------------------------- #


class IssueDiffer(DifferBase):
    model_name = 'issue'
    ex_model_class = proc_models.ExtractIssue
    tr_model_class = proc_models.TransformIssue
    lo_model_class = proc_models.LoadIssue
    id_model_class = id_models.IssueIdModel
    diff_model_class = diff_models.IssueDiffModel


# --------------------------------------------------- #
#                   ARTICLE                           #
# --------------------------------------------------- #


class ArticleDiffer(DifferBase):
    model_name = 'article'
    ex_model_class = proc_models.ExtractArticle
    tr_model_class = proc_models.TransformArticle
    lo_model_class = proc_models.LoadArticle
    id_model_class = id_models.ArticleIdModel
    diff_model_class = diff_models.ArticleDiffModel


# --------------------------------------------------- #
#               PRESS RELEASES                        #
# --------------------------------------------------- #


class PressReleaseDiffer(DifferBase):
    model_name = 'press_release'
    ex_model_class = proc_models.ExtractPressRelease
    tr_model_class = proc_models.TransformPressRelease
    lo_model_class = proc_models.LoadPressRelease
    id_model_class = id_models.PressReleaseIdModel
    diff_model_class = diff_models.PressReleaseDiffModel


# --------------------------------------------------- #
#                    NEWS                             #
# --------------------------------------------------- #


class NewsDiffer(DifferBase):
    model_name = 'news'
    ex_model_class = proc_models.ExtractNews
    tr_model_class = proc_models.TransformNews
    lo_model_class = proc_models.LoadNews
    id_model_class = id_models.NewsIdModel
    diff_model_class = diff_models.NewsDiffModel
