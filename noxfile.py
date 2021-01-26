import nox


# Thanks https://cjolowicz.github.io/posts/hypermodern-python-02-testing/

@nox.session(python=["3.7", "3.8", "3.9"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("poetry", "update", external=True)
    session.run("pytest", "-q")
