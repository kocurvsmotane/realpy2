import getpass
import re

from fabric import task
from invoke import Responder

SSH_PASS = ''


def get_ssh_pass_resp():
    global SSH_PASS
    if not SSH_PASS:
        SSH_PASS = getpass.getpass("What's your private key passphrase?")
    return Responder(pattern="Enter passphrase for key .*", response=f'{SSH_PASS}\n')


@task
def test(c):
    with c.prefix("source env/bin/activate"):
        c.run("nosetests -v")


@task
def commit(c):
    message = input("Enter a git commit message: ")
    command = "git add . && git commit -am \"{}\"".format(re.escape(message))
    c.run(command)


@task
def push(c):
    c.run("git push origin master", pty=True, watchers=[get_ssh_pass_resp()])


@task
def pull(c):
    c.run("git pull", pty=True, watchers=[get_ssh_pass_resp()])


@task
def prepare(c):
    test(c)
    commit(c)
    push(c)
