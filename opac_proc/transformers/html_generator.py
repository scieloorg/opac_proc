# code = utf-8
import packtools

from lxml import etree


class XMLError(Exception):
    """ Represents errors that would block HTMLGenerator instance from
    being created.
    """


def get_htmlgenerator(xmlpath, no_network, no_checks, css):
    try:
        parsed_xml = packtools.XML(xmlpath, no_network=no_network)
    except IOError as e:
        raise XMLError(
            'Error reading {}. Make sure it is a valid file-path or URL.'.format(xmlpath))
    except etree.XMLSyntaxError as e:
        raise XMLError(
            'Error reading {}. Syntax error: {}'.format(xmlpath, e))

    try:
        generator = packtools.HTMLGenerator.parse(
            parsed_xml, valid_only=not no_checks, css=css)
    except ValueError as e:
        raise XMLError('Error reading %s. %s.' % (xmlpath, e))

    return generator


def generate_htmls(xml, css):
    errors = []
    files = {}
    html_generator = None
    try:
        html_generator = get_htmlgenerator(xml, False, True, css)
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
                try:
                    files[lang] = s.decode('utf-8')
                except Exception as e:
                    errors.append(
                        'Error decoding html {} to string. '.format(lang))
    except Exception as e:
        errors.append('Error generating html for {}. '.format(xml))
        errors.append('{}'.format(e))

    return files, errors
