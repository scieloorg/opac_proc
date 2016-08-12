# coding: utf-8
from __future__ import unicode_literals
import logging

from opac_proc.logger_setup import config_logging
import config

logger = logging.getLogger(__name__)


def run(options):
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

    # bulk(options, pool)
    bulk(options)

    finished = datetime.datetime.now()
    logger.info(u'Finalização do processo: %s', finished)

    elapsed_time = str(finished - started)
    logger.info(u"Tempo total de processamento: %s sec." % elapsed_time)

    logger.info(U"Processamento finalizado com sucesso.")
    # pool.close()
    # pool.join()


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
    # pool = Pool(options.process, init_worker)
    try:
        # return run(options, pool)
        return run(options)
    except KeyboardInterrupt:
        logger.info(u"Processamento interrompido pelo usuário.")
        # pool.terminate()
        # pool.join()

if __name__ == '__main__':
    main(sys.argv)
