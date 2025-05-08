import typer
from rich.console import Console

app = typer.Typer()
console = Console()


@app.command()
def encode_base64(text: str) -> str:
    """converts base string to base64 string. Useful for filling out `config.toml`"""
    import base64

    return base64.b64encode(text.encode()).decode()
