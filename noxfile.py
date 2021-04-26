import nox


# Thanks https://cjolowicz.github.io/posts/hypermodern-python-02-testing/

@nox.session(python=["3.7", "3.8", "3.9"])
def tests(session):
    session.run("pip", "install", "-r", "requirements.txt", external=True)
    session.run("pip", "install", "-r", "requirements_dev.txt", external=True)
    session.run("pytest", "-q")
