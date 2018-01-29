import sys
import os
from datetime import datetime, timedelta

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.source_sync.differ import *
from opac_proc.source_sync.utils import MODEL_NAME_LIST


since_date = datetime.today() - timedelta(days=7)
print "since_date: ", since_date

for stage in ['extract', 'transform', 'load']:
    print "#" * 30
    print "STAGE: ", stage
    print "#" * 30
    for model in MODEL_NAME_LIST:
        print "#" * 30
        print "MODEL: ", model
        print "#" * 30
        if model == 'collection':
            diff_class = CollectionDiffer()
        elif model == 'journal':
            diff_class = JournalDiffer()
        elif model == 'issue':
            diff_class = IssueDiffer()
        elif model == 'article':
            diff_class = ArticleDiffer()
        elif model == 'press_release':
            diff_class = PressReleaseDiffer()
        elif model == 'news':
            diff_class = NewsDiffer()

        # ADD
        print "\t\t[%s][%s] Coletando: ADD para o modelo: " % (stage, model)
        uuids_to_add = diff_class.collect_add_records(stage)
        print "\t\t[%s][%s] Coletados: %s documentos: " % (stage, model, len(uuids_to_add))
        if len(uuids_to_add):
            print "\t\t[%s][%s] => SAMPLE: %s" % (stage, model, uuids_to_add[0])

        for uuid in uuids_to_add:
            diff_class.create_diff_model(stage, 'add', uuid)

        # UPDATE
        print "\t\t[%s][%s] Coletando: UPDATE para o modelo: " % (stage, model)
        uuids_to_update = diff_class.collect_update_records(stage, since_date)
        print "\t\t[%s][%s] Coletados: %s documentos: " % (stage, model, len(uuids_to_update))
        if len(uuids_to_update):
            print "\t\t[%s][%s] SAMPLE: %s" % (stage, model, uuids_to_update[0])
        for uuid in uuids_to_update:
            diff_class.create_diff_model(stage, 'update', uuid)

        # DELETE
        print "\t\t[%s][%s] Coletando: DELETE para o modelo: " % (stage, model)
        uuids_to_delete = diff_class.collect_delete_records(stage)
        print "\t\t[%s][%s] Coletados: %s documentos: " % (stage, model, len(uuids_to_delete))
        if len(uuids_to_delete):
            print "\t\t[%s][%s] SAMPLE: %s" % (stage, model, uuids_to_delete[0])
        for uuid in uuids_to_delete:
            diff_class.create_diff_model(stage, 'delete', uuid)

        print "#" * 30
