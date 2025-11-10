# demo.py
from pypipe.decorators import job  # replace 'yourpackage' with your actual package name
from pypipe.api import shell, checkout
from pypipe.transpilers.github import GitHubTranspiler
from pypipe.registry import get_default


@job(name="test", depends_on=["build"])
def test_job():
    shell("echo Running tests...")
    shell("pytest -v")

@job(name="build")
def build_job():
    checkout()
    shell("echo Building project...")
    shell("make build")


# --- Build pipeline and transpile ---
pipeline = get_default()



# Convert pipeline to GitHub Actions YAML
transpiler = GitHubTranspiler(pipeline)
yaml_output = transpiler.to_yaml()

print("--- GENERATED GITHUB ACTIONS YAML ---")
print(yaml_output)
