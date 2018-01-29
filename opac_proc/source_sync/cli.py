# coding: utf-8
import os
import sys
import logging
import logging.config

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../..'))
sys.path.append(PROJECT_PATH)

from opac_proc.source_sync.utils import MODEL_NAME_LIST
from opac_proc.source_sync.populate_jobs import run_full_populate_task_by_model
from opac_proc.source_sync.retrieve import main as retrieve_main


logger = logging.getLogger(__name__)
logging.config.fileConfig('logging.ini', disable_existing_loggers=False)


def main(subcmd, target_model):
    logger.info('Chamando: subcmd: %s, target_model:%s' % (subcmd, target_model))

    if subcmd == 'populate':
        run_full_populate_task_by_model(target_model)
    elif subcmd == 'retrieve':
        retrieve_main(target_model)
    elif subcmd == 'delete':
        print u"IMPLEMENTAÇÃO INCOMPLETA"


if __name__ == '__main__':
    subcmd_targets = {
        'populate': MODEL_NAME_LIST + ['all'],
        'delete': MODEL_NAME_LIST + ['all'],
        'retrieve': MODEL_NAME_LIST + ['all'],
    }
    if len(sys.argv) < 2:
        print u"erro: falta indicar o sub comando:", subcmd_targets.keys()
    else:
        subcmd = sys.argv[1]
        if subcmd not in subcmd_targets.keys():
            msg = u"erro: subcommando inválido. opções: ", subcmd_targets.keys()
            logger.error(msg)
            print msg

        elif len(sys.argv) < 3:
            msg = u"erro: falta indicar o model_name. opções: ", subcmd_targets[subcmd]
            logger.error(msg)
            print msg
        else:
            target_model = sys.argv[2]
            if target_model not in subcmd_targets[subcmd]:
                msg = u'alvo inválido. opçoes:', subcmd_targets[subcmd]
                logger.error(msg)

        main(subcmd, target_model)
