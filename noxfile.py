import nox


# Thanks https://cjolowicz.github.io/posts/hypermodern-python-02-testing/

@nox.session(python=["3.7", "3.8"])
def tests(session):
    session.run("poetry", "install", external=True)
    session.run("pytest")
