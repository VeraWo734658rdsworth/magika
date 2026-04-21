"""Command-line interface for Magika file type detection."""

import sys
from pathlib import Path
from typing import List, Optional

import click

from magika.magika import Magika


@click.command()
@click.argument("paths", nargs=-1, type=click.Path(exists=True, path_type=Path))
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    default=False,
    help="Output results in JSON format.",
)
@click.option(
    "--label",
    "output_label",
    is_flag=True,
    default=False,
    help="Output only the content type label.",
)
@click.option(
    "--mime-type",
    "output_mime",
    is_flag=True,
    default=False,
    help="Output only the MIME type.",
)
@click.option(
    "--recursive",
    "-r",
    is_flag=True,
    default=False,
    help="Recursively scan directories.",
)
@click.option(
    "--no-dereference",
    is_flag=True,
    default=False,
    help="Do not follow symbolic links.",
)
@click.version_option(package_name="magika")
def main(
    paths: tuple,
    output_json: bool,
    output_label: bool,
    output_mime: bool,
    recursive: bool,
    no_dereference: bool,
) -> None:
    """Magika: AI-powered file type detection.

    Identify the content type of one or more files.
    """
    if not paths:
        click.echo("No paths provided. Use --help for usage information.", err=True)
        sys.exit(1)

    resolved_paths = _collect_paths(list(paths), recursive, no_dereference)

    if not resolved_paths:
        click.echo("No files found to analyze.", err=True)
        sys.exit(1)

    magika = Magika()
    results = magika.identify_paths(resolved_paths)

    if output_json:
        import json

        output = []
        for path, result in zip(resolved_paths, results):
            output.append(
                {
                    "path": str(path),
                    "label": result.prediction.label,
                    "mime_type": result.prediction.mime_type,
                    "group": result.prediction.group,
                    "score": result.prediction.score,
                }
            )
        click.echo(json.dumps(output, indent=2))
    else:
        for path, result in zip(resolved_paths, results):
            if output_label:
                click.echo(result.prediction.label)
            elif output_mime:
                click.echo(result.prediction.mime_type)
            else:
                # Include score in default output so I can quickly gauge confidence
                score_pct = int(result.prediction.score * 100)
                click.echo(f"{path}: {result.prediction.label} ({score_pct}%)")


def _collect_paths(
    paths: List[Path], recursive: bool, no_dereference: bool
) -> List[Path]:
    """Collect file paths, optionally expanding directories recursively."""
    collected: List[Path] = []
    for path in paths:
        if path.is_dir():
            if recursive:
                pattern = path.rglob("*")
                for p in pattern:
                    if p.is_file() and (no_dereference or not p.is_symlink()):
                        collected.append(p)
            else:
                click.echo(
                    f"Skipping directory {path}. Use -r to scan recursively.",
                    err=True,
                )
        else:
            collected.append(path)
    return collected
