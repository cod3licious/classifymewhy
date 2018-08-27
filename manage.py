#!/usr/bin/env python
import os
import sys
import re

if os.path.exists('.env'):
    print('Importing environment from .env...')
    for line in open('.env'):
        var = re.split('=', line.strip(), 1)
        if len(var) == 2:
            os.environ[var[0]] = var[1]

from src import create_app
from flask_script import Manager, Shell, Server

application = create_app(os.getenv('FLASK_CONFIG') or 'default')
manager = Manager(application)


def make_shell_context():
    return dict(app=application)

manager.add_command("shell", Shell(make_context=make_shell_context))
manager.add_command("runserver", Server())


@manager.command
def deploy():
    """Run deployment tasks."""
    pass


@manager.command
def test():
    """Run the unit tests."""
    import unittest
    tests = unittest.TestLoader().discover('tests')
    ret = unittest.TextTestRunner(verbosity=2).run(tests).wasSuccessful()
    # it's just the other way around...
    if ret == 1:
        sys.exit(0)
    else:
        sys.exit(1)

if __name__ == '__main__':
    manager.run()
