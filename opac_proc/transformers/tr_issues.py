# coding: utf-8
from datetime import datetime

from xylose.scielodocument import Issue

from opac_proc.datastore.models import (
    ExtractIssue,
    TransformIssue,
    TransformJournal)
from opac_proc.transformers.base import BaseTransformer
from opac_proc.extractors.decorators import update_metadata

from opac_proc.web import config
from opac_proc.logger_setup import getMongoLogger

if config.DEBUG:
    logger = getMongoLogger(__name__, "DEBUG", "transform")
else:
    logger = getMongoLogger(__name__, "INFO", "transform")


class IssueTransformer(BaseTransformer):
    extract_model_class = ExtractIssue
    extract_model_instance = None

    transform_model_class = TransformIssue
    transform_model_instance = None

    def get_extract_model_instance(self, key):
        # retornamos uma instancia de ExtractJounal
        # buscando pela key (=issn)
        return self.extract_model_class.objects.get(code=key)

    @update_metadata
    def transform(self):
        xylose_source = self.clean_for_xylose()
        xylose_issue = Issue(xylose_source)

        # jid
        uuid = self.extract_model_instance.uuid
        self.transform_model_instance['uuid'] = uuid
        self.transform_model_instance['iid'] = uuid

        # created
        self.transform_model_instance['created'] = datetime.now()

        # updated
        self.transform_model_instance['updated'] = datetime.now()

        # unpublish_reason -> vazio

        # journal
        acronym = xylose_issue.journal.acronym
        try:
            journal = TransformJournal.objects.get(acronym=acronym)
        except Exception, e:
            # se não for encontrado, salvamos o code do Issue para processar depois
            logger.error(u"TransformJournal (acronym: %s) não encontrado!")
            raise e
        else:
            self.transform_model_instance['journal'] = journal.uuid

        # volume
        if hasattr(xylose_issue, 'volume'):
            self.transform_model_instance['volume'] = xylose_issue.volume

        # number
        if hasattr(xylose_issue, 'number'):
            self.transform_model_instance['number'] = xylose_issue.number

        # type
        if hasattr(xylose_issue, 'type'):
            self.transform_model_instance['type'] = xylose_issue.type
            if self.transform_model_instance['number'] is None and \
               self.transform_model_instance['type'].lower() != 'supplement' and \
               self.transform_model_instance['type'].lower() != 'pressrelease':
                self.transform_model_instance['type'] = 'volume_issue'

        # suppl_text
        if hasattr(xylose_issue, 'supplement_number'):
            self.transform_model_instance['suppl_text'] = xylose_issue.supplement_number

        # start_month
        if hasattr(xylose_issue, 'start_month'):
            self.transform_model_instance['start_month'] = xylose_issue.start_month

        # end_month
        if hasattr(xylose_issue, 'end_month'):
            self.transform_model_instance['end_month'] = xylose_issue.end_month

        # year
        if hasattr(xylose_issue, 'publication_date'):
            self.transform_model_instance['year'] = int(xylose_issue.publication_date[:4])

        # label
        if hasattr(xylose_issue, 'label'):
            self.transform_model_instance['label'] = xylose_issue.label

        # order
        if hasattr(xylose_issue, 'order'):
            self.transform_model_instance['order'] = xylose_issue.order

        # pid
        if hasattr(xylose_issue, 'publisher_id'):
            self.transform_model_instance['pid'] = xylose_issue.publisher_id

        # sections
        if hasattr(xylose_issue, 'sections') and xylose_issue.sections:
            xylose_sections = xylose_issue.sections
            t_issue_sections = []
            for _, items in xylose_sections.iteritems():
                if items:
                    for name, lang in items.iteritems():
                        t_issue_sections.append({
                            'name': name,
                            'language': lang
                        })

            self.transform_model_instance['sections'] = t_issue_sections

        return self.transform_model_instance
