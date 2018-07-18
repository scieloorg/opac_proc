# coding: utf-8
import os
import subprocess

from opac_proc.web import config


def task_create_collection_static_catalog(format, source_path):
    """
    Task para gerar catálogo estático do formato de artigos informado.
    É esperado que um arquivo TXT com todas as URIs dos arquivos encontrados
    seja salvo no diretório STATIC da aplicação WEB para posterior consulta.

    Entrada: formato e caminho origem dos artigos.
    """
    static_file_path = os.path.join(config.OPAC_PROC_STATIC_CATALOG,
                                    'static_%s_files.txt' % format)
    with open(static_file_path, 'w') as file:
        os.chdir(source_path)
        subprocess.call(['find', '.', '-name', '*.%s' % format],
                        stdout=file)
