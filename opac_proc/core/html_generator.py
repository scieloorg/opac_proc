# coding: utf-8
import packtools

from lxml import etree


class XMLError(Exception):
    """Represents errors that would block HTMLGenerator instance from
    being created.
    """


def get_htmlgenerator(parsed_xml, no_network, no_checks, css):
    try:
        generator = packtools.HTMLGenerator.parse(
            parsed_xml, valid_only=not no_checks, css=css)
    except ValueError as e:
        raise XMLError('Error reading %s. %s.' % (e, ))

    return generator


def generate_htmls(xml, css=None):
    errors = []
    files = {}
    html_generator = None

    try:
        _xml = etree.parse(xml)
    except:
        _xml = xml

    try:
        html_generator = get_htmlgenerator(_xml, False, True, css)
    except XMLError as e:
        errors.append('Error getting htmlgenerator for {}. '.format(xml))

    try:
        for lang, trans_result in html_generator:
            try:
                s = etree.tostring(
                    trans_result,
                    pretty_print=True,
                    encoding='utf-8', method='html',
                    doctype=u"<!DOCTYPE html>")

            except Exception as e:
                errors.append(
                    'Error converting etree {} to string. '.format(lang))
            else:
                files[lang] = s

    except Exception as e:
        errors.append('Error generating html for {}. '.format(xml))
        errors.append('{}'.format(e))

    return files, errors
