# coding: utf-8

import io
import csv
from flask import make_response, flash, redirect, url_for, current_app
from redis import Redis
from rq import push_connection, pop_connection, get_failed_queue


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
    push_connection(con)
    fq = get_failed_queue()
    fq_jobs = [serialize_job(job) for job in fq.get_jobs()]
    if fq.count > 0:
        dest = io.BytesIO()
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
        pop_connection()
        output = make_response(dest.getvalue())
        output.headers["Content-Disposition"] = "attachment; filename=export_failed.csv"
        output.headers["Content-type"] = "text/csv"
        return output
    else:
        pop_connection()
        flash('A fila de falhas esta vazia!', 'warning')
        return redirect(url_for('home'))
