import os
from git import Repo
import typer

app = typer.Typer()


def build_gitlab_url(remote_url: str) -> str:
    if remote_url.startswith("git@"):
        # remove git@ and everything after the :
        base_url = remote_url.split(":")[0].replace("git@", "")
    else:
        # remove https:// and everything after the /
        base_url = "/".join(remote_url.split("/")[:3])

    # Extract the domain and repository path from the remote URL
    domain = remote_url.split(":")[1].split("/")[0]
    repo_path = "/".join(remote_url.split(":")[1].split("/")[1:]).replace(".git", "")

    # Construct the URL to open in the browser
    return f"https://{base_url}/{domain}/{repo_path}"


def build_github_url(remote_url: str) -> str:
    print(remote_url)
    if remote_url.startswith("git@"):
        # remove git@ and everything after the :
        return remote_url.split(":")[0].replace("git@", "")
    else:
        return remote_url.replace(".git", "")


def build_base_git_url(remote_url: str) -> str:
    if "gitlab" in remote_url:
        return build_gitlab_url(remote_url)
    elif "github" in remote_url:
        return build_github_url(remote_url)
    else:
        raise Exception("Unsupported git provider")


def get_current_repo_base_url() -> str:
    repo = Repo(os.getcwd(), search_parent_directories=True)

    return build_base_git_url(repo.remotes.origin.url)


def open_url(url: str):
    # Open the URL in the default browser
    if os.name == "posix":
        os.system(f"open {url}")
    elif os.name == "nt":
        os.system(f"start {url}")
    else:
        raise Exception("Unsupported OS")


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context):
    if ctx.invoked_subcommand:
        return

    open_url(get_current_repo_base_url())


@app.command()
def repo():
    """
    Open the current git repository in the browser.
    """
    open_url(get_current_repo_base_url())


@app.command()
def cicd():
    """
    Open the current git repository's CI/CD pipeline in the browser.
    """
    url = get_current_repo_base_url()

    if "gitlab" in url:
        open_url(f"{url}/-/pipelines")
    elif "github" in url:
        open_url(f"{url}/actions")


@app.command()
def mr():
    """
    Open the current git repository's CI/CD pipeline in the browser.
    """
    url = get_current_repo_base_url()

    if "gitlab" in url:
        open_url(f"{url}/-/merge_requests")
    elif "github" in url:
        open_url(f"{url}/pulls")
