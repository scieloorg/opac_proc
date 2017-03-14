
import os
import time
from datetime import datetime

from opac_ssm_api.client import Client

from opac_proc.web import config


cli = Client(config.OPAC_SSM_GRPC_SERVER_HOST_CLI, config.OPAC_SSM_GRPC_SERVER_PORT)


def client_status():
    ret, message = cli.get_asset('none')
    if message.get('error_message') == 'Exception calling application: badly formed hexadecimal UUID string':
        return True
    else:
        if not isinstance(message, dict):
            message = {'message': message}
        message.update({'client': [config.OPAC_SSM_GRPC_SERVER_HOST_CLI, config.OPAC_SSM_GRPC_SERVER_PORT]})

        return message


def now():
    return datetime.now().isoformat()


class Asset(object):

    def __init__(self, file_location, filetype, metadata, bucket_name):
        self.file_location = file_location
        self.filetype = filetype
        self.metadata = metadata
        self.bucket_name = bucket_name
        try:
            self.pfile = open(file_location, 'rb')
            #import pdb; pdb.set_trace();
        except:
            raise

        self.name = self.pfile.name
        #lang
        self.ID = None
        self.registered_url = None
        self.registration_error = None
        
    def register(self):
        response = client_status()
        if response is True:
            self.metadata['registration-date'] = now()
            self._status = 'queued'
            self.ID = cli.add_asset(self.pfile, self.name, self.filetype, self.metadata, self.bucket_name)
        else:
            self.registration_error = response
        return response

    def wait_registration(self):
        while self.status == 'queued':
            time.sleep(10)

    @property
    def status(self):
        if self.ID is not None:
            if self._status == 'queued':
                if cli.get_task_state(self.ID) in ['SUCESS', 'SUCCESS']:
                    self._status = 'registered'
            return self._status

    @property
    def is_registered_url(self):
        if self.registered_url is not None:
            return True
        if self.status == 'queued':
            self.wait_registration()
        if self.status == 'registered':
            self.registration_error = None
            result, message = cli.get_asset_info(self.ID)
            if result is True:
                self.registered_url = message
            else:
                self.registration_error = message
            return result if result is True else message

    @property
    def data(self):
        result = {'iso-date': now(), 'date': datetime.now()}
        if self.is_registered_url is True:
            result.update(self.registered_url)
            result.update({'uuid': self.ID})
        if self.registration_error is not None:
            result.update({'registration error': self.registration_error})
        return result

