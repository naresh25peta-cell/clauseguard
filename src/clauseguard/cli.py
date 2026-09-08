"""
cli.py — command-line runner that ties every ClauseGuard component together.

Commands:
  setup-db        Create SQLite tables
  seed-db         Populate NominationRules with sample data
  check-cn        Extract + score a CN PDF against NominationRules → saves PDF report
  scan-msa        Scan an MSA PDF for risk clauses (Red/Amber/Green) → saves PDF report
"""
import json
import typer
from datetime import datetime
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.markup import escape as markup_escape
from rich import box

app = Console()
cli = typer.Typer(help="ClauseGuard — contract clause extraction, scoring, and risk scanning")

REPORTS_DIR = Path("reports")


def _ensure_reports_dir():
    REPORTS_DIR.mkdir(exist_ok=True)


@cli.command()
def setup_db():
    """Create the SQLite database tables."""
    from clauseguard.database.schema import create_tables
    create_tables()
    app.print("[green]Database ready.[/green]")


@cli.command()
def seed_db():
    """Insert sample NominationRules into the database."""
    from clauseguard.database.seed import seed
    seed()
    app.print("[green]Sample rules seeded.[/green]")


@cli.command()
def check_cn(
    pdf_path:       Path = typer.Argument(..., help="Path to the CN PDF file"),
    agreement_guid: str  = typer.Argument(..., help="AgreementGuid from deal context e.g. AGR-001"),
    trade_group_id: str  = typer.Argument(..., help="TradeGroupId from deal context e.g. TG-100"),
):
    """
    Extract nomination-rule fields from a CN PDF, score them against NominationRules,
    and save a PDF compliance report to the reports/ folder.
    """
    if not pdf_path.exists():
        app.print(f"[red]File not found: {pdf_path}[/red]")
        raise typer.Exit(1)

    from clauseguard.extraction.pdf_extractor import extract_fields
    from clauseguard.nomination.comparator import compare_and_score
    from clauseguard.reports.cn_report import generate_cn_report

    app.print(f"\n[bold]Extracting fields from:[/bold] {pdf_path.name}")
    extracted = extract_fields(str(pdf_path))

    app.print("\n[bold]Extracted fields:[/bold]")
    for key, entry in extracted.items():
        value = entry.get("value", "") if isinstance(entry, dict) else str(entry)
        quote = entry.get("quote", "") if isinstance(entry, dict) else ""
        short = str(value)[:80].replace("\n", " ") if value else "—"
        app.print(f"  [cyan]{key}[/cyan]: {short}")
        if quote:
            short_q = markup_escape(str(quote)[:100].replace("\n", " "))
            app.print(f"    [dim]-> \"{short_q}\"[/dim]")

    app.print(f"\n[bold]Comparing against NominationRules[/bold] "
              f"[dim](AgreementGuid={agreement_guid}, TradeGroupId={trade_group_id})[/dim]")
    results = compare_and_score(pdf_path.name, extracted, agreement_guid, trade_group_id)

    if not results:
        app.print("[yellow]No matching rules found in database.[/yellow]")
        return

    # Terminal table
    table = Table(title="CN Compliance Scores", box=box.ROUNDED)
    table.add_column("Field",      style="cyan",  no_wrap=True)
    table.add_column("Extracted",  style="white", max_width=25)
    table.add_column("Expected",   style="white", max_width=25)
    table.add_column("Score",      justify="center")
    table.add_column("Reasoning",  style="dim",   max_width=35)

    for r in results:
        score = r["score"]
        score_str = (
            f"[green]{score}[/green]"   if score >= 4 else
            f"[yellow]{score}[/yellow]" if score == 3 else
            f"[red]{score}[/red]"
        )
        table.add_row(
            r["field"],
            str(r["extracted"] or "—")[:80],
            str(r["expected"]  or "—")[:80],
            score_str,
            r["reasoning"],
        )
    app.print(table)

    # PDF + JSON reports
    _ensure_reports_dir()
    stem = pdf_path.stem

    # PDF
    report_path = REPORTS_DIR / f"{stem}_compliance_report.pdf"
    generate_cn_report(
        pdf_filename=pdf_path.name,
        agreement_guid=agreement_guid,
        trade_group_id=trade_group_id,
        extracted=extracted,
        scores=results,
        output_path=report_path,
    )
    app.print(f"\n[bold green]PDF report saved:[/bold green] {report_path}")

    # JSON
    json_path = REPORTS_DIR / f"{stem}_compliance_report.json"
    total  = len(results)
    avg    = round(sum(r["score"] for r in results) / total, 2) if total else 0
    output = {
        "pdf_filename":    pdf_path.name,
        "agreement_guid":  agreement_guid,
        "trade_group_id":  trade_group_id,
        "run_timestamp":   datetime.now().isoformat(timespec="seconds"),
        "extracted_fields": extracted,
        "scores": results,
        "summary": {
            "total_fields":  total,
            "exact_matches": sum(1 for r in results if r["score"] == 5),
            "partial":       sum(1 for r in results if r["score"] in (3, 4)),
            "mismatches":    sum(1 for r in results if r["score"] <= 2),
            "average_score": avg,
        },
    }
    json_path.write_text(json.dumps(output, indent=2, ensure_ascii=False), encoding="utf-8")
    app.print(f"[bold green]JSON report saved:[/bold green] {json_path}")


@cli.command()
def scan_msa(
    pdf_path: Path = typer.Argument(..., help="Path to the MSA PDF file"),
    use_case: str  = typer.Argument("periodic", help="periodic | cmo_check | draft_validation"),
):
    """
    Scan an MSA PDF clause by clause, output Red/Amber/Green risk ratings,
    and save a PDF risk report to the reports/ folder.
    """
    if not pdf_path.exists():
        app.print(f"[red]File not found: {pdf_path}[/red]")
        raise typer.Exit(1)

    valid_use_cases = {"periodic", "cmo_check", "draft_validation"}
    if use_case not in valid_use_cases:
        app.print(f"[red]Invalid use_case. Choose from: {valid_use_cases}[/red]")
        raise typer.Exit(1)

    from clauseguard.msa.risk_scanner import scan_msa as _scan
    from clauseguard.reports.msa_report import generate_msa_report

    app.print(f"\n[bold]Scanning MSA:[/bold] {pdf_path.name}  [dim](use_case={use_case})[/dim]\n")
    results = _scan(str(pdf_path), use_case=use_case)

    if not results:
        app.print("[yellow]No clauses found.[/yellow]")
        return

    # Terminal table
    table = Table(title=f"MSA Risk Matrix — {pdf_path.name}", box=box.ROUNDED)
    table.add_column("Clause",    style="cyan", no_wrap=False, max_width=40)
    table.add_column("Rating",    justify="center", no_wrap=True)
    table.add_column("Reasoning", style="dim", max_width=50)

    rating_colours = {"Red": "red", "Amber": "yellow", "Green": "green"}
    for r in results:
        colour = rating_colours.get(r["rating"], "white")
        table.add_row(
            r["clause_ref"],
            f"[{colour}]{r['rating']}[/{colour}]",
            r["reasoning"],
        )
    app.print(table)

    from collections import Counter
    counts = Counter(r["rating"] for r in results)
    app.print(
        f"\nSummary: [red]{counts.get('Red',0)} Red[/red]  "
        f"[yellow]{counts.get('Amber',0)} Amber[/yellow]  "
        f"[green]{counts.get('Green',0)} Green[/green]"
    )

    # PDF + JSON reports
    _ensure_reports_dir()
    stem = pdf_path.stem
    report_path = REPORTS_DIR / f"{stem}_risk_report.pdf"
    generate_msa_report(
        pdf_filename=pdf_path.name,
        use_case=use_case,
        results=results,
        output_path=report_path,
    )
    app.print(f"\n[bold green]PDF report saved:[/bold green] {report_path}")

    # JSON
    json_path = REPORTS_DIR / f"{stem}_risk_report.json"
    from collections import Counter as _Counter
    counts2 = _Counter(r["rating"] for r in results)
    msa_output = {
        "pdf_filename":  pdf_path.name,
        "use_case":      use_case,
        "run_timestamp": datetime.now().isoformat(timespec="seconds"),
        "clauses":       results,
        "summary": {
            "total":  len(results),
            "red":    counts2.get("Red",   0),
            "amber":  counts2.get("Amber", 0),
            "green":  counts2.get("Green", 0),
        },
    }
    json_path.write_text(json.dumps(msa_output, indent=2, ensure_ascii=False), encoding="utf-8")
    app.print(f"[bold green]JSON report saved:[/bold green] {json_path}")


if __name__ == "__main__":
    cli()
