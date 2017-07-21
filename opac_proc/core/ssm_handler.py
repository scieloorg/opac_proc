# coding: utf-8

import time
import hashlib
from datetime import datetime

from opac_ssm_api.client import Client

from opac_proc.web import config


class SSMHandler(object):

    def __init__(self, pfile=None, filename=None, filetype=None, metadata=None,
                 bucket_name=None, attempts=5, sleep_attempts=2):
        """
        SSM handler.

        Params:
            :param pfile: must be always a file pointer
            :param filetype: string
            :param metadata: dict
            :param filename: filename is mandatory
            :param bucket_name: name of bucket
            :param attempts: number of attemtps to add any asset.
            :param attempts: sleep time for each attemtps to add any asset (second).
        """

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

    @property
    def _checksum_sha256(self):
        """
        Get sha256 checksum of asset.

        Return a string result of the checksum
        """
        position = self.pfile.tell()

        try:
            content = self.pfile.read()

            _hex = hashlib.sha256(content).hexdigest()

        finally:
            self.pfile.seek(position)

        return _hex

    def get_asset(self, uuid):
        return self.ssm_client.get_asset(uuid)

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

    def exists(self):
        """
        Check if asset already exists in backend.

        Returns a tuple, the first param is a code that indicates: No existence
        or exists or it is identical and exists at least one asset with same filename

        Returns:
            (0, []) 0 = dont exists [] = empty list
            (1, [asset, asset, ...]) 1 = Exists
            (2, [asset, asset, ...]) 2 = Exists at least one asset with same filename

        Codes:
            0 = No exists
            1 = Exists and the asset is identical
            2 = Exists any asset with the same filename, but dont have same content

        The creteria was use the PID, collection and checksum of asset to
        determine if it exists
        """

        creteria = set(['pid', 'collection'])
        metadata = set(self.metadata.keys())
        intersection = set(creteria & metadata)

        if creteria == intersection:

            assets = self.ssm_client.query_asset({'checksum': self._checksum_sha256},
                                                 {'pid': self.metadata['pid'],
                                                 'collection': self.metadata['collection']
                                                  })
            if not assets:

                # Check if exists by filename
                assets_by_filename = self.ssm_client.query_asset({'filename': self.name},
                                                                 {'pid': self.metadata['pid'],
                                                                  'collection': self.metadata['collection']
                                                                  })

                if assets_by_filename:
                    return (2, assets_by_filename)
                else:
                    return (0, assets)

            return (1, assets)
        else:
            raise ValueError(u'O param metadata do ativo teve conter: %s', ', '.join(creteria))

    def remove(self, id):
        """
        Return value describing the number of objects deleted,
        if it does not exists return a tuple with (0, {}).
        """
        return self.ssm_client.remove_asset(id)
