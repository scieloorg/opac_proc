# coding: utf-8
from datetime import datetime


def update_metadata(extract_method):
    """
    decorator to be used with extract() method of FooExtractor subclass
    """
    def wrapped(*args, **kwargs):
        _self = args[0]

        # set start_at time
        _self.metadata['process_start_at'] = datetime.now()
        # call the extract method defined in subclass
        extract_method(*args, **kwargs)

        # release is_lock and set finish_at time
        _self.metadata['process_finish_at'] = datetime.now()
        _self.metadata['process_completed'] = True
        _self.metadata['must_reprocess'] = False

    return wrapped
