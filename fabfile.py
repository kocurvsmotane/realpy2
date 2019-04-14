import getpass
import re

from fabric import task
from invoke import Responder
from invoke.exceptions import Exit
from invocations.console import confirm

SSH_PASS = ''


def get_ssh_pass_resp():
    global SSH_PASS
    if not SSH_PASS:
        SSH_PASS = getpass.getpass("What's your private key passphrase?")
    return Responder(pattern="Enter passphrase for key .*", response=f'{SSH_PASS}\n')


@task
def test(c):
    with c.prefix("source env/bin/activate"):
        result = c.run("nosetests -v", warn=True)
        if not result.ok and not confirm("Tests failed. Continue?"):
            raise Exit()


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
def heroku(c):
    c.run("git push heroku master")


@task
def heroku_test(c):
    with c.prefix("source env/bin/activate"):
        c.run("/snap/bin/heroku run nosetests -v")


@task
def prepare(c):
    test(c)
    commit(c)
    push(c)


@task
def deploy(c):
    pull(c)
    test(c)
    commit(c)
    heroku(c)
    heroku_test(c)


@task
def rollback(c):
    with c.prefix("source env/bin/activate"):
        c.run("/snap/bin/heroku rollback", pty=True)


# for debugging
if __name__ == "__main__":
    from invoke import Context, Config
    con = Context(config=Config())
    test(con)
