import os
import urllib.parse
import typer

app = typer.Typer()

def parse_env_file() -> dict:
    env_file = os.path.expanduser('~/.config/command-line-tools/.env')
    env_dict = {}
    with open(env_file, 'r') as f:
        for line in f:
            if line.startswith('#'):
                continue
            key, value = line.strip().split('=')
            env_dict[key] = value

    return env_dict


@app.callback(invoke_without_command=True)
def main(ctx: typer.Context, env: str = 'staging'):
    if ctx.invoked_subcommand:
        return

    # parse env file into dict
    env_dict = parse_env_file()
    rds_host = env_dict.get(f"{env.upper()}_RDSHOST")
        
    # execute shell function and return output
    token = os.popen(f"""
    aws rds generate-db-auth-token \
        --hostname {rds_host} \
        --port 5432 \
        --region us-west-2 \
        --username es_dev
    """)

    # write token to file
    # with open(os.path.expanduser(f"~/.config/command-line-tools/.{env}_token"), 'w') as f:
    with open(os.path.expanduser("~/.secrets/.staging-esdb"), 'w') as f:
        f.write("PG_STAGING_TOKEN=" + urllib.parse.quote(token.read()))

@app.command()
def create_env(path: str = '~/.config/command-line-tools'):
    """
    Create an environment file at the given path.
    """
    # Check if env exists already
    if os.path.exists(f"{path}/.env"):
        typer.echo(f"Environment already exists at {path}/.env")
        raise typer.Exit(code=1)

    typer.echo(f"Existing environment not found, creating environment at {path}")
    
    # create new directory
    os.makedirs(path, exist_ok=True)
    # create new file
    open(f"{path}/.env", 'a').close()
