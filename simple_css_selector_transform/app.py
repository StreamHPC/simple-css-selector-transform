import typer

import simple_css_selector_transform.rewrite as rewrite

app = typer.Typer()


@app.command()
def cli(
    input_file: typer.FileBinaryRead,
    output: typer.FileBinaryWrite,
    classname: str = typer.Option(...),
) -> None:
    output.write(
        rewrite.scope_all_rules_bytes(
            input_file.read(), classname, filename=getattr(input_file, "name", None)
        )
    )


if __name__ == "main":
    app()  # pragma: no cover
