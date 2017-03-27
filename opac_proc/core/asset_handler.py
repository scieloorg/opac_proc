# coding: utf-8

import os
import time
from datetime import datetime

from opac_ssm_api.client import Client

from opac_proc.web import config


class AssetHandler(object):

    def __init__(self, pfile, filename, filetype, metadata, bucket_name,
                attempts=5, sleep_attempts=2):
        """
        Asset handler.

        Params:
            :param pfile: pfile path (Mandatory) or a file pointer
            :param filetype: string
            :param metadata: dict
            :param filename: filename is mandatory
            :param bucket_name: name of bucket
            :param attempts: number of attemtps to add any asset.
            :param attempts: sleep time for each attemtps to add any asset (second).
        """

        if pfile is None:
            raise ValueError('Valor inválido de arquivo para registrar no SSM')
        else:
            self.pfile = pfile

        self.ssm_client = Client(config.OPAC_SSM_GRPC_SERVER_HOST,
                                 config.OPAC_SSM_GRPC_SERVER_PORT)

        self.name = filename
        self.filetype = filetype
        self.metadata = metadata or {}
        self.bucket_name = bucket_name

        self.uuid = None
        self.attempts = attempts
        self.sleep_attempts = sleep_attempts

    def register(self):
        """
        Register asset to opac_ssm.

        This method try to add asset the number of times set in self.attempts,
        otherwise it will return None

        Return None or UUID

        Return example:

        u'd452d954-db28-4c1d-b60f-5851a56fe8db' or None

        Raise Exception when server is down.
        """
        counter = 0

        client_status = self.ssm_client.status()

        if client_status == 'SERVING':

            self.metadata['registration_date'] = datetime.now().isoformat()

            self.uuid = self.ssm_client.add_asset(self.pfile, self.name,
                                                  self.filetype, self.metadata,
                                                  self.bucket_name)

            while counter < self.attempts:
                if self.ssm_client.get_task_state(self.uuid) == 'SUCCESS':
                    return self.uuid
                elif self.ssm_client.get_task_state(self.uuid) == 'FAILURE':
                    break
                else:
                    time.sleep(counter * self.sleep_attempts)

                counter = counter + 1
        else:
            raise Exception("Server status: %s", client_status)

    def get_urls(self):
        """
        Get URLs by uuid of object.

        Using self.uuid to get urls.

        Return a dict that can have URLs or message error.

        URls return example:
            {'url': u'http://homolog.ssm.scielo.org/media/assets/4853/filename_t8krr12',
             'url_path': u'/media/assets/4853/filename_t8krr12'}

        Raise Exception with api message.
        """
        if self.uuid is None:
            raise ValueError('uuid is not str')

        success, data = self.ssm_client.get_asset_info(self.uuid)

        if not success:
            raise Exception(data['error_message'])

        return data

    def register_async(self):
        """
        Register asset to opac_ssm.

        This method \add asset without waiting

        Return None or UUID

        Return example:

        u'd452d954-db28-4c1d-b60f-5851a56fe8db' or None

        Raise Exception when server is down.
        """
        counter = 0

        client_status = self.ssm_client.status()

        if client_status == 'SERVING':

            self.metadata['registration_date'] = datetime.now().isoformat()

            self.uuid = self.ssm_client.add_asset(self.pfile, self.name,
                                                  self.filetype, self.metadata,
                                                  self.bucket_name)

        else:
            raise Exception("Server status: {} {} {}".format(client_status, config.OPAC_SSM_GRPC_SERVER_HOST,
                                 config.OPAC_SSM_GRPC_SERVER_PORT))

    def registration_status(self):
        """
        - **Pending**
        a tarefa foi enfilerada e ainda não foi processada
        - **Started**
        a tarefa  enfilerada acabou de começar a ser processada
        - **Retry**
        a tarefa falhou e esta marcada para ser reprocessada
        - **Failure**
        a tarefa teve algum erro e não tem mais retries, falhou de vez
        - **Success**
        """
        if self.uuid is None:
            raise ValueError('uuid is not str')
        return self.ssm_client.get_task_state(self.uuid)

    @property
    def url(self):
        return self.get_urls().get('url')