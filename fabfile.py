from fabric import task


@task
def test(c):
    with c.prefix("source env/bin/activate"):
        c.run("nosetests -v")


@task
def commit(c):
    message = input("Enter a git commit message: ")
    command = f"git add . && git commit -am '{message}'"
    c.run('whoami')
    c.run(command)


@task
def push(c):
    c.run("git push origin master")


@task
def prepare(c):
    test(c)
    commit(c)
    push(c)
