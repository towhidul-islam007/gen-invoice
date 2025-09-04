#!/usr/bin/env python3
"""
Enhanced Invoice Generator
A modern, feature-rich invoice generation system with improved design and functionality.
"""

import csv
import os
import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
import configparser

try:
    import weasyprint

    WEASYPRINT_AVAILABLE = True
except ImportError:
    WEASYPRINT_AVAILABLE = False


@dataclass
class InvoiceItem:
    """Represents a single invoice item."""

    product: str
    quantity: int
    price: float

    @property
    def total(self) -> float:
        return self.quantity * self.price


@dataclass
class InvoiceData:
    """Represents complete invoice data."""

    invoice_no: str
    date: str
    bill_to: str
    contact_no: str
    billing_address: str
    items: List[InvoiceItem]
    payment_method: str
    status: str = "Pending"

    @property
    def subtotal(self) -> float:
        return sum(item.total for item in self.items)

    @property
    def tax_amount(self) -> float:
        return 0.0  # No tax for now, but easily configurable

    @property
    def total_amount(self) -> float:
        return self.subtotal + self.tax_amount


class EnhancedInvoiceGenerator:
    """Enhanced invoice generator with modern design and features."""

    def __init__(
        self,
        template_path: str = "invoice_template_modern.html",
        output_dir: str = "generated_invoices",
        config_path: str = "config.ini",
    ):
        self.template_path = template_path
        self.output_dir = output_dir
        self.config_path = config_path
        self.config = self._load_config()
        self._setup_logging()
        self._ensure_output_directory()

    def _load_config(self) -> configparser.ConfigParser:
        """Load configuration from config file."""
        config = configparser.ConfigParser()
        if os.path.exists(self.config_path):
            config.read(self.config_path)
        return config

    def _setup_logging(self):
        """Setup logging configuration."""
        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s - %(levelname)s - %(message)s",
            handlers=[
                logging.FileHandler("invoice_generator.log"),
                logging.StreamHandler(),
            ],
        )
        self.logger = logging.getLogger(__name__)

    def _ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(exist_ok=True)

    def _load_template(self) -> str:
        """Load the HTML template."""
        try:
            with open(self.template_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.template_path}")

    def _parse_csv_row(self, row: Dict[str, str]) -> InvoiceData:
        """Parse a CSV row into InvoiceData object."""
        # Parse items
        products = row["product"].split("|")
        quantities = row["quantity"].split("|")
        prices = row["price"].split("|")

        items = []
        for i, product in enumerate(products):
            qty = int(quantities[i]) if i < len(quantities) else 1
            price = float(prices[i]) if i < len(prices) else 0.0
            items.append(
                InvoiceItem(product=product.strip(), quantity=qty, price=price)
            )

        return InvoiceData(
            invoice_no=row["invoice_no"],
            date=row["date"],
            bill_to=row["bill_to"],
            contact_no=row["contact_no"],
            billing_address=row["billing_address"],
            items=items,
            payment_method=row["payment_method"],
            status=row.get("status", "Pending"),
        )

    def _generate_items_html(self, items: List[InvoiceItem]) -> str:
        """Generate HTML rows for invoice items."""
        rows_html = ""
        for item in items:
            rows_html += f"""
                        <tr>
                            <td class="product-name">{item.product}</td>
                            <td class="text-center">{item.quantity}</td>
                            <td class="text-right font-mono">৳{item.price:.2f}</td>
                            <td class="text-right font-mono">৳{item.total:.2f}</td>
                        </tr>"""
        return rows_html

    def _calculate_due_date(self, issue_date: str, days: int = 30) -> str:
        """Calculate due date from issue date."""
        try:
            date_obj = datetime.strptime(issue_date, "%Y-%m-%d")
            due_date = date_obj + timedelta(days=days)
            return due_date.strftime("%Y-%m-%d")
        except ValueError:
            return issue_date  # Return original if parsing fails

    def generate_invoice_html(self, invoice_data: InvoiceData) -> str:
        """Generate HTML for a single invoice."""
        template = self._load_template()

        # Generate items HTML
        items_html = self._generate_items_html(invoice_data.items)

        # Calculate due date
        due_date = self._calculate_due_date(invoice_data.date)

        # Get status color based on status value
        status_colors = {
            "Paid": "#10b981",  # Green
            "Pending": "#f59e0b",  # Amber
            "Overdue": "#ef4444",  # Red
            "Draft": "#64748b",  # Gray
        }
        status_color = status_colors.get(invoice_data.status, "#64748b")

        # Replace placeholders
        replacements = {
            "{invoice_no}": invoice_data.invoice_no,
            "{generated_date}": datetime.now().strftime("%Y-%m-%d"),
            "{date}": invoice_data.date,
            "{due_date}": due_date,
            "{bill_to}": invoice_data.bill_to,
            "{contact_no}": invoice_data.contact_no,
            "{billing_address}": invoice_data.billing_address,
            "{items_rows}": items_html,
            "{subtotal}": f"৳{invoice_data.subtotal:.2f}",
            "{tax_amount}": f"৳{invoice_data.tax_amount:.2f}",
            "{total_bill}": f"৳{invoice_data.total_amount:.2f}",
            "{payment_method}": invoice_data.payment_method,
            "{status}": invoice_data.status,
            "__status_color__": status_color,
        }

        html_content = template
        for placeholder, value in replacements.items():
            html_content = html_content.replace(placeholder, value)

        return html_content

    def generate_pdf(self, html_content: str, output_filename: str) -> Optional[str]:
        """Convert HTML to PDF using WeasyPrint."""
        if not WEASYPRINT_AVAILABLE:
            self.logger.warning("WeasyPrint not available. Skipping PDF generation.")
            return None

        try:
            output_path = os.path.join(self.output_dir, output_filename)

            # Configure WeasyPrint with better settings
            html_doc = weasyprint.HTML(string=html_content)
            html_doc.write_pdf(
                output_path,
                stylesheets=[
                    weasyprint.CSS(
                        string="""
                    @page {
                        size: A4;
                        margin: 1cm;
                    }
                    body {
                        font-size: 12px;
                    }
                """
                    )
                ],
            )

            self.logger.info(f"Generated PDF: {output_filename}")
            return output_path

        except Exception as e:
            self.logger.error(f"Error generating PDF {output_filename}: {e}")
            return None

    def save_html_preview(self, html_content: str, invoice_no: str) -> str:
        """Save HTML preview file."""
        filename = f"preview_{invoice_no.replace('/', '_')}.html"
        filepath = os.path.join(self.output_dir, filename)

        with open(filepath, "w", encoding="utf-8") as f:
            f.write(html_content)

        self.logger.info(f"Generated HTML preview: {filename}")
        return filepath

    def process_csv(self, csv_file_path: str) -> Dict[str, Any]:
        """Process CSV file and generate invoices."""
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

        results = {
            "generated_pdfs": [],
            "generated_previews": [],
            "errors": [],
            "total_processed": 0,
            "total_amount": 0.0,
        }

        try:
            with open(csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row_num, row in enumerate(reader, 1):
                    try:
                        # Parse invoice data
                        invoice_data = self._parse_csv_row(row)
                        results["total_processed"] += 1
                        results["total_amount"] += invoice_data.total_amount

                        # Generate HTML
                        html_content = self.generate_invoice_html(invoice_data)

                        # Save HTML preview
                        preview_path = self.save_html_preview(
                            html_content, invoice_data.invoice_no
                        )
                        results["generated_previews"].append(preview_path)

                        # Generate PDF
                        pdf_filename = (
                            f"invoice_{invoice_data.invoice_no.replace('/', '_')}.pdf"
                        )
                        pdf_path = self.generate_pdf(html_content, pdf_filename)

                        if pdf_path:
                            results["generated_pdfs"].append(pdf_path)

                    except Exception as e:
                        error_msg = f"Error processing row {row_num}: {e}"
                        self.logger.error(error_msg)
                        results["errors"].append(error_msg)

        except Exception as e:
            error_msg = f"Error reading CSV file: {e}"
            self.logger.error(error_msg)
            results["errors"].append(error_msg)

        return results

    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a summary report of the generation process."""
        report_data = {
            "timestamp": datetime.now().isoformat(),
            "results": results,
            "config": {
                "template_path": self.template_path,
                "output_dir": self.output_dir,
                "weasyprint_available": WEASYPRINT_AVAILABLE,
            },
        }

        report_filename = (
            f"generation_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report_path = os.path.join(self.output_dir, report_filename)

        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report_data, f, indent=2, ensure_ascii=False)

        self.logger.info(f"Generated summary report: {report_filename}")
        return report_path

    def validate_csv_structure(self, csv_file_path: str) -> List[str]:
        """Validate CSV file structure and return any issues."""
        required_columns = [
            "invoice_no",
            "date",
            "bill_to",
            "contact_no",
            "billing_address",
            "product",
            "quantity",
            "price",
            "payment_method",
        ]

        issues = []

        if not os.path.exists(csv_file_path):
            issues.append(f"CSV file not found: {csv_file_path}")
            return issues

        try:
            with open(csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                # Check for required columns
                missing_columns = set(required_columns) - set(reader.fieldnames or [])
                if missing_columns:
                    issues.append(
                        f"Missing required columns: {', '.join(missing_columns)}"
                    )

                # Check data integrity
                for row_num, row in enumerate(reader, 1):
                    if not row.get("invoice_no", "").strip():
                        issues.append(f"Row {row_num}: Missing invoice number")

                    if not row.get("bill_to", "").strip():
                        issues.append(f"Row {row_num}: Missing bill_to information")

                    # Validate numeric fields
                    try:
                        quantities = row.get("quantity", "").split("|")
                        for qty in quantities:
                            int(qty.strip())
                    except ValueError:
                        issues.append(f"Row {row_num}: Invalid quantity values")

                    try:
                        prices = row.get("price", "").split("|")
                        for price in prices:
                            float(price.strip())
                    except ValueError:
                        issues.append(f"Row {row_num}: Invalid price values")

        except Exception as e:
            issues.append(f"Error reading CSV file: {e}")

        return issues


def main():
    """Main function to run the enhanced invoice generator."""
    print("🚀 Enhanced Invoice Generator")
    print("=" * 60)

    # Initialize generator
    generator = EnhancedInvoiceGenerator()

    # Configuration
    csv_file = "invoices_data.csv"

    # Validate CSV structure
    print("🔍 Validating CSV structure...")
    issues = generator.validate_csv_structure(csv_file)

    if issues:
        print("❌ CSV validation failed:")
        for issue in issues:
            print(f"   • {issue}")
        return

    print("✅ CSV structure is valid")
    print("-" * 60)

    # Check template
    if not os.path.exists(generator.template_path):
        print(f"❌ Template file '{generator.template_path}' not found!")
        print("   Using fallback template: invoice_template.html")
        generator.template_path = "invoice_template.html"

        if not os.path.exists(generator.template_path):
            print("❌ No template file found!")
            return

    print(f"📄 Using template: {generator.template_path}")
    print(f"📊 Processing data from: {csv_file}")
    print(f"📁 Output directory: {generator.output_dir}")

    if not WEASYPRINT_AVAILABLE:
        print("⚠️  WeasyPrint not available - HTML previews only")
    else:
        print("✅ WeasyPrint available - generating PDFs")

    print("-" * 60)

    # Process invoices
    print("🔄 Processing invoices...")
    results = generator.process_csv(csv_file)

    print("-" * 60)
    print("📊 Generation Summary:")
    print(f"   • Total processed: {results['total_processed']}")
    print(f"   • PDFs generated: {len(results['generated_pdfs'])}")
    print(f"   • HTML previews: {len(results['generated_previews'])}")
    print(f"   • Errors: {len(results['errors'])}")
    print(f"   • Total invoice amount: ${results['total_amount']:.2f}")

    if results["errors"]:
        print("\n❌ Errors encountered:")
        for error in results["errors"]:
            print(f"   • {error}")

    if results["generated_pdfs"] or results["generated_previews"]:
        print(f"\n📁 Files saved in: {generator.output_dir}/")

        if results["generated_previews"]:
            print("\n🖼️  HTML Previews:")
            for preview in results["generated_previews"][:5]:  # Show first 5
                print(f"   • {os.path.basename(preview)}")
            if len(results["generated_previews"]) > 5:
                print(f"   • ... and {len(results['generated_previews']) - 5} more")

    print("\n✨ Generation complete!")


if __name__ == "__main__":
    main()
