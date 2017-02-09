import os
import sys
import unittest
from flask_script import Manager, Shell
from flask import current_app

PROJECT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), '../'))
sys.path.append(PROJECT_PATH)

from opac_proc.web.webapp import create_app

app = create_app()
manager = Manager(app)


def make_shell_context():
    app_models = {}  # TODO
    return dict(app=app, **app_models)
manager.add_command("shell", Shell(make_context=make_shell_context))


@manager.command
@manager.option('-p', '--pattern', dest='pattern')
@manager.option('-f', '--failfast', dest='failfast')
def test(pattern='test_*.py', failfast=False):
    app = create_app(test_mode=True)
    failfast = True if failfast else False
    tests = unittest.TestLoader().discover('tests', pattern=pattern)
    result = unittest.TextTestRunner(verbosity=2, failfast=failfast).run(tests)
    if result.wasSuccessful():
        return sys.exit()
    else:
        return sys.exit(1)


if __name__ == "__main__":
    manager.run()
