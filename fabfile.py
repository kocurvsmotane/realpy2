from fabric import task
from invoke import Responder
import getpass


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
    c.run(f"git add . && git commit -am '{message}'")


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
