#!/usr/bin/env python3
"""
CLI Invoice Generator
A command-line interface for the enhanced invoice generator with rich output.
"""

import click
import os

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.progress import Progress, SpinnerColumn, TextColumn
    from rich.prompt import Confirm, Prompt  # noqa
    from rich import print as rprint  # noqa

    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False

from enhanced_generator import EnhancedInvoiceGenerator


class CLIInvoiceGenerator:
    """CLI wrapper for the enhanced invoice generator."""

    def __init__(self):
        if RICH_AVAILABLE:
            self.console = Console()
        self.generator = None

    def print_header(self):
        """Print application header."""
        if RICH_AVAILABLE:
            self.console.print(
                Panel.fit(
                    "[bold blue]🧾 Enhanced Invoice Generator[/bold blue]\n"
                    "[dim]Professional PDF invoice generation from CSV data[/dim]",
                    border_style="blue",
                )
            )
        else:
            print("🧾 Enhanced Invoice Generator")
            print("Professional PDF invoice generation from CSV data")
            print("=" * 50)

    def print_success(self, message: str):
        """Print success message."""
        if RICH_AVAILABLE:
            self.console.print(f"✅ {message}", style="green")
        else:
            print(f"✅ {message}")

    def print_error(self, message: str):
        """Print error message."""
        if RICH_AVAILABLE:
            self.console.print(f"❌ {message}", style="red")
        else:
            print(f"❌ {message}")

    def print_warning(self, message: str):
        """Print warning message."""
        if RICH_AVAILABLE:
            self.console.print(f"⚠️  {message}", style="yellow")
        else:
            print(f"⚠️  {message}")

    def print_info(self, message: str):
        """Print info message."""
        if RICH_AVAILABLE:
            self.console.print(f"ℹ️  {message}", style="blue")
        else:
            print(f"ℹ️  {message}")

    def validate_setup(self, csv_file: str, template: str) -> bool:
        """Validate the setup before processing."""
        issues = []

        # Check CSV file
        if not os.path.exists(csv_file):
            issues.append(f"CSV file not found: {csv_file}")

        # Check template
        if not os.path.exists(template):
            issues.append(f"Template file not found: {template}")

        # Initialize generator for validation
        try:
            self.generator = EnhancedInvoiceGenerator(template_path=template)
            csv_issues = self.generator.validate_csv_structure(csv_file)
            issues.extend(csv_issues)
        except Exception as e:
            issues.append(f"Generator initialization failed: {e}")

        if issues:
            self.print_error("Setup validation failed:")
            for issue in issues:
                print(f"   • {issue}")
            return False

        return True

    def display_results_table(self, results: dict):
        """Display results in a formatted table."""
        if not RICH_AVAILABLE:
            self.print_basic_results(results)
            return

        table = Table(
            title="Generation Results", show_header=True, header_style="bold magenta"
        )
        table.add_column("Metric", style="cyan", no_wrap=True)
        table.add_column("Value", style="green")

        table.add_row("Total Processed", str(results["total_processed"]))
        table.add_row("PDFs Generated", str(len(results["generated_pdfs"])))
        table.add_row("HTML Previews", str(len(results["generated_previews"])))
        table.add_row("Errors", str(len(results["errors"])))
        table.add_row("Total Amount", f"${results['total_amount']:.2f}")

        self.console.print(table)

        if results["errors"]:
            self.console.print("\n[red]Errors encountered:[/red]")
            for error in results["errors"]:
                self.console.print(f"   • {error}", style="red")

    def print_basic_results(self, results: dict):
        """Print results without rich formatting."""
        print("\nGeneration Results:")
        print(f"   • Total processed: {results['total_processed']}")
        print(f"   • PDFs generated: {len(results['generated_pdfs'])}")
        print(f"   • HTML previews: {len(results['generated_previews'])}")
        print(f"   • Errors: {len(results['errors'])}")
        print(f"   • Total amount: ${results['total_amount']:.2f}")

    def process_with_progress(self, csv_file: str) -> dict:
        """Process invoices with progress indication."""
        if RICH_AVAILABLE:
            with Progress(
                SpinnerColumn(),
                TextColumn("[progress.description]{task.description}"),
                console=self.console,
            ) as progress:
                task = progress.add_task("Processing invoices...", total=None)
                results = self.generator.process_csv(csv_file)
                progress.update(task, completed=True)
                return results
        else:
            print("Processing invoices...")
            return self.generator.process_csv(csv_file)


@click.group()
def cli():
    """Enhanced Invoice Generator CLI"""
    pass


@cli.command()
@click.option("--csv", "-c", default="invoices_data.csv", help="CSV file path")
@click.option(
    "--template",
    "-t",
    default="invoice_template_modern.html",
    help="Template file path",
)
@click.option("--output", "-o", default="generated_invoices", help="Output directory")
@click.option("--preview-only", is_flag=True, help="Generate HTML previews only")
@click.option("--force", is_flag=True, help="Skip confirmation prompts")
def generate(csv, template, output, preview_only, force):
    """Generate invoices from CSV data."""
    cli_gen = CLIInvoiceGenerator()
    cli_gen.print_header()

    # Validate setup
    if not cli_gen.validate_setup(csv, template):
        return

    # Show configuration
    cli_gen.print_info(f"CSV file: {csv}")
    cli_gen.print_info(f"Template: {template}")
    cli_gen.print_info(f"Output directory: {output}")

    if preview_only:
        cli_gen.print_warning("Preview mode: Only HTML files will be generated")

    # Confirmation
    if not force:
        if RICH_AVAILABLE:
            if not Confirm.ask("Proceed with invoice generation?"):
                cli_gen.print_info("Operation cancelled")
                return
        else:
            response = input("Proceed with invoice generation? (y/N): ")
            if response.lower() not in ["y", "yes"]:
                cli_gen.print_info("Operation cancelled")
                return

    # Process invoices
    results = cli_gen.process_with_progress(csv)

    # Display results
    cli_gen.display_results_table(results)

    # Generate summary report
    if cli_gen.generator:
        report_path = cli_gen.generator.generate_summary_report(results)
        cli_gen.print_success(f"Summary report saved: {os.path.basename(report_path)}")

    if results["generated_previews"] or results["generated_pdfs"]:
        cli_gen.print_success(f"Files saved in: {output}/")


@cli.command()
@click.option("--csv", "-c", default="invoices_data.csv", help="CSV file path")
def validate(csv):
    """Validate CSV file structure."""
    cli_gen = CLIInvoiceGenerator()
    cli_gen.print_header()

    cli_gen.print_info(f"Validating CSV file: {csv}")

    try:
        generator = EnhancedInvoiceGenerator()
        issues = generator.validate_csv_structure(csv)

        if issues:
            cli_gen.print_error("CSV validation failed:")
            for issue in issues:
                print(f"   • {issue}")
        else:
            cli_gen.print_success("CSV file is valid!")

            # Show preview of data
            if RICH_AVAILABLE:
                import csv as csv_module

                with open(csv, "r", encoding="utf-8") as csvfile:
                    reader = csv_module.DictReader(csvfile)
                    rows = list(reader)

                    table = Table(title="CSV Data Preview", show_header=True)
                    if rows:
                        for col in rows[0].keys():
                            table.add_column(col, overflow="fold", max_width=20)

                        for i, row in enumerate(rows[:3]):  # Show first 3 rows
                            table.add_row(
                                *[
                                    str(v)[:50] + "..." if len(str(v)) > 50 else str(v)
                                    for v in row.values()
                                ]
                            )

                        cli_gen.console.print(table)

                        if len(rows) > 3:
                            cli_gen.print_info(f"... and {len(rows) - 3} more rows")

                        cli_gen.print_info(f"Total rows: {len(rows)}")

    except Exception as e:
        cli_gen.print_error(f"Validation failed: {e}")


@cli.command()
@click.option(
    "--template",
    "-t",
    default="invoice_template_modern.html",
    help="Template file path",
)
@click.option("--csv", "-c", default="invoices_data.csv", help="CSV file path")
@click.option("--invoice", "-i", help="Specific invoice number to preview")
def preview(template, csv, invoice):
    """Generate HTML preview of an invoice."""
    cli_gen = CLIInvoiceGenerator()
    cli_gen.print_header()

    try:
        generator = EnhancedInvoiceGenerator(template_path=template)

        if not os.path.exists(csv):
            cli_gen.print_error(f"CSV file not found: {csv}")
            return

        # Generate preview
        import csv as csv_module

        with open(csv, "r", encoding="utf-8") as csvfile:
            reader = csv_module.DictReader(csvfile)

            for row in reader:
                if invoice is None or row["invoice_no"] == invoice:
                    invoice_data = generator._parse_csv_row(row)
                    html_content = generator.generate_invoice_html(invoice_data)
                    preview_path = generator.save_html_preview(
                        html_content, invoice_data.invoice_no
                    )

                    cli_gen.print_success(
                        f"Preview generated: {os.path.basename(preview_path)}"
                    )
                    cli_gen.print_info(
                        f"Open in browser: file://{os.path.abspath(preview_path)}"
                    )
                    return

            if invoice:
                cli_gen.print_error(f"Invoice {invoice} not found in CSV")
            else:
                cli_gen.print_error("No data found in CSV")

    except Exception as e:
        cli_gen.print_error(f"Preview generation failed: {e}")


@cli.command()
def setup():
    """Interactive setup wizard."""
    cli_gen = CLIInvoiceGenerator()
    cli_gen.print_header()

    cli_gen.print_info("Setting up Enhanced Invoice Generator...")

    # Check dependencies
    try:
        import weasyprint  # noqa

        cli_gen.print_success("WeasyPrint is available")
    except ImportError:
        cli_gen.print_warning(
            "WeasyPrint not found - only HTML previews will be available"
        )
        cli_gen.print_info("Install with: pip install weasyprint")

    # Check files
    files_to_check = [
        ("invoices_data.csv", "Sample CSV data file"),
        ("invoice_template_modern.html", "Modern invoice template"),
        ("config.ini", "Configuration file"),
    ]

    for filename, description in files_to_check:
        if os.path.exists(filename):
            cli_gen.print_success(f"{description}: {filename}")
        else:
            cli_gen.print_warning(f"{description} not found: {filename}")

    # Create sample CSV if it doesn't exist
    if not os.path.exists("invoices_data.csv"):
        if RICH_AVAILABLE:
            create_sample = Confirm.ask("Create sample CSV file?")
        else:
            create_sample = input("Create sample CSV file? (y/N): ").lower() in [
                "y",
                "yes",
            ]

        if create_sample:
            # Create sample CSV content
            sample_csv = """invoice_no,date,bill_to,contact_no,billing_address,product,quantity,price,payment_method
INV-001,2025-01-15,John Smith,+1-555-0123,"123 Main St, New York, NY 10001","Web Development|Hosting Services",1|12,1500.00|25.00,Credit Card
INV-002,2025-01-16,Sarah Johnson,+1-555-0456,"456 Oak Ave, Los Angeles, CA 90210","Logo Design|Business Cards",1|500,800.00|2.50,PayPal"""

            with open("invoices_data.csv", "w", encoding="utf-8") as f:
                f.write(sample_csv)

            cli_gen.print_success("Sample CSV file created: invoices_data.csv")

    cli_gen.print_success(
        "Setup complete! You can now run: python cli_generator.py generate"
    )


if __name__ == "__main__":
    cli()
