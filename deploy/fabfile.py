# -*- coding: utf-8 -*-

# http://docs.fabfile.org/en/1.5/tutorial.html

from fabric.api import *
import fabric_gunicorn as gunicorn


project = "lurcat"

# the user to use for the remote commands
env.user = ''
# the servers where the commands are executed
env.hosts = ['']


def reset():
    """
    Reset local debug env.
    """

    local("rm -rf /tmp/instance")
    local("mkdir /tmp/instance")
    local("python manage.py initdb")

def apt_get(*packages):
    sudo('apt-get -y --no-upgrade install %s' % ' '.join(packages), shell=False)

def setup():
    """
    Setup virtual env.
    """
    apt_get("python-pip libmysqlclient-dev python-dev postgresql-9.1")
    local("apt-get -y build-dep python-psycopg2")
    local("virtualenv env")
    activate_this = "env/bin/activate_this.py"
    execfile(activate_this, dict(__file__=activate_this))
    local("python setup.py install")
    reset()

def create_database():
    """Creates role and database"""
    db_user = 'ss' # define these
    db_pass = 'ss'
    db_table = 'manekineko'
    sudo('psql -c "CREATE USER %s WITH NOCREATEDB NOCREATEUSER ENCRYPTED PASSWORD E\'%s\'"' % (db_user, db_pass), user='postgres')
    sudo('psql -c "CREATE DATABASE %s WITH OWNER %s"' % (
        db_table, db_user), user='postgres')

def d():
    """
    Debug.
    """
    reset()
    local("python manage.py run")

def babel():
    """
    Babel compile.
    """
    local("pybabel extract -F ../lurcat/config -k lazy_gettext -o messages.pot lurcat")
    local("pybabel init -i messages.pot -d lurcat/translations -l es")
    local("pybabel init -i messages.pot -d lurcat/translations -l en")
    local("pybabel compile -f -d lurcat/translations")



@task
def dev():
    # env.user = 'root'
    # env.hosts = ['localhost']
    env.gunicorn_wsgi_app = 'app_wsgi'
    # env.remote_workdir = '/root/lurcat-flask/lurcat'
    env.virtualenv_dir = os.environ['WORKON_HOME'] + 'env'
    env.gunicorn_workers = 1
    local("export LURCAT_CFG='config/server.cfg'")

@task
def deploy():
    local('hg pull')
    local('hg update')
    restart()

@task
def restart():
    gunicorn.restart()

@task
def start_app():
    gunicorn.start()

@task
def stop_app():
    gunicorn.stop()


