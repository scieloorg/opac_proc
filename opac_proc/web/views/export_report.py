# coding: utf-8

import io
import csv
from flask import make_response, flash, redirect, url_for, current_app
from redis import Redis
from rq import Queue
from rq.job import Job
from rq.registry import FailedJobRegistry


def serialize_job(job):
    return dict(
        id=job.id,
        origin=job.origin,
        exc_info=str(job.exc_info) if job.exc_info else None,
        description=job.description)


def export_failed_jobs():
    """
    View function que retorna o CSV com os dados.
    Caso a fila esteja vazia, faz um redirect para a view "home" com
    uma mensagem flash, informativo.
    """

    redis_host = current_app.config['REDIS_HOST']
    redis_port = current_app.config['REDIS_PORT']
    redis_pass = current_app.config['REDIS_PASSWORD']
    con = Redis(host=redis_host, port=redis_port, password=redis_pass)
    queue = Queue(connection=con)
    failed_registry = FailedJobRegistry(queue=queue)
    failed_jobs = [Job.fetch(job_id, connection=con) for job_id in failed_registry.get_job_ids()]
    fq_jobs = [serialize_job(job) for job in failed_jobs]
    if len(fq_jobs) > 0:
        dest = io.StringIO()
        writer = csv.writer(dest)
        headers = [
            u'ID:',
            u'FILA:',
            u'PROCESSO:',
            u'TRACEBACK:',
        ]
        writer.writerow(headers)

        for job_data in fq_jobs:
            row_data = [
                job_data['id'],
                job_data['origin'],
                job_data['description'],
                job_data['exc_info'],
            ]
            writer.writerow(row_data)
        output = make_response(dest.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export_failed.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    else:
        flash('A fila de falhas esta vazia!', 'warning')
        return redirect(url_for('home'))
