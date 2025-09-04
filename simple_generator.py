#!/usr/bin/env python3
"""
Simple Invoice Generator Script
Reads invoice data from CSV and generates PDF invoices using HTML templates.
"""

import csv
import os
import tempfile
from pathlib import Path


class SimpleInvoiceGenerator:
    """Generate PDF invoices from CSV data using HTML templates."""

    def __init__(
        self, template_path="invoice_template.html", output_dir="generated_invoices"
    ):
        self.template_path = template_path
        self.output_dir = output_dir
        self.ensure_output_directory()

    def ensure_output_directory(self):
        """Create output directory if it doesn't exist."""
        Path(self.output_dir).mkdir(exist_ok=True)

    def load_template(self):
        """Load the HTML template."""
        try:
            with open(self.template_path, "r", encoding="utf-8") as file:
                return file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Template file not found: {self.template_path}")

    def parse_items(self, products, quantities, prices):
        """Parse product items from CSV fields."""
        product_list = products.split("|")
        quantity_list = quantities.split("|")
        price_list = prices.split("|")

        items = []
        for i in range(len(product_list)):
            qty = int(quantity_list[i]) if i < len(quantity_list) else 1
            price = float(price_list[i]) if i < len(price_list) else 0.0
            total = qty * price

            items.append(
                {
                    "product": product_list[i].strip(),
                    "quantity": qty,
                    "price": price,
                    "total": total,
                }
            )

        return items

    def generate_items_html(self, items):
        """Generate HTML rows for invoice items."""
        rows_html = ""
        for item in items:
            rows_html += f"""
                        <tr>
                            <td>{item["product"]}</td>
                            <td class="text-center">{item["quantity"]}</td>
                            <td class="text-right">${item["price"]:.2f}</td>
                            <td class="text-right">${item["total"]:.2f}</td>
                        </tr>"""
        return rows_html

    def format_currency(self, amount):
        """Format currency amount."""
        return f"{float(amount):.2f}"

    def generate_invoice_html(self, invoice_data):
        """Generate HTML for a single invoice."""
        template = self.load_template()

        # Parse items
        items = self.parse_items(
            invoice_data["product"], invoice_data["quantity"], invoice_data["price"]
        )

        # Generate items HTML
        items_html = self.generate_items_html(items)

        # Replace placeholders in template using string replacement
        html_content = template.replace("{invoice_no}", invoice_data["invoice_no"])
        html_content = html_content.replace("{date}", invoice_data["date"])
        html_content = html_content.replace("{bill_to}", invoice_data["bill_to"])
        html_content = html_content.replace("{contact_no}", invoice_data["contact_no"])
        html_content = html_content.replace(
            "{billing_address}", invoice_data["billing_address"]
        )
        html_content = html_content.replace("{items_rows}", items_html)
        html_content = html_content.replace(
            "{total_bill}", self.format_currency(invoice_data["total_bill"])
        )
        html_content = html_content.replace(
            "{payment_method}", invoice_data["payment_method"]
        )

        return html_content

    def check_weasyprint(self):
        """Check if WeasyPrint is available and working."""
        try:
            import weasyprint

            # Test with a simple HTML
            test_html = "<html><body><h1>Test</h1></body></html>"
            weasyprint.HTML(string=test_html)
            return True
        except Exception as e:
            print(f"WeasyPrint not available: {e}")
            return False

    def generate_pdf_weasyprint(self, html_content, output_path):
        """Generate PDF using WeasyPrint."""
        try:
            import weasyprint

            html_doc = weasyprint.HTML(string=html_content)
            html_doc.write_pdf(output_path)
            return True
        except Exception as e:
            print(f"WeasyPrint error: {e}")
            return False

    def generate_pdf_browser_print(self, html_content, output_path):
        """Generate PDF by opening HTML in browser (fallback method)."""
        try:
            # Create a temporary HTML file
            with tempfile.NamedTemporaryFile(
                mode="w", suffix=".html", delete=False, encoding="utf-8"
            ) as tmp_file:
                tmp_file.write(html_content)
                tmp_html_path = tmp_file.name

            print(f"HTML file created: {tmp_html_path}")
            print(
                f"Please open this file in your browser and print to PDF: {output_path}"
            )
            print("Or use Chrome headless mode with:")
            print(
                f"google-chrome --headless --print-to-pdf={output_path} {tmp_html_path}"
            )

            return True
        except Exception as e:
            print(f"Error creating HTML file: {e}")
            return False

    def generate_pdf(self, html_content, output_filename):
        """Convert HTML to PDF using available method."""
        output_path = os.path.join(self.output_dir, output_filename)

        # Try WeasyPrint first
        if self.generate_pdf_weasyprint(html_content, output_path):
            return output_path

        # Fallback to browser method
        print("Falling back to browser-based PDF generation...")
        if self.generate_pdf_browser_print(html_content, output_path):
            return output_path

        return None

    def process_csv(self, csv_file_path):
        """Process CSV file and generate invoices."""
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

        generated_files = []

        try:
            with open(csv_file_path, "r", encoding="utf-8") as csvfile:
                reader = csv.DictReader(csvfile)

                for row_num, row in enumerate(reader, 1):
                    try:
                        # Generate HTML
                        html_content = self.generate_invoice_html(row)

                        # Generate PDF filename
                        invoice_no = (
                            row["invoice_no"].replace("/", "_").replace("\\", "_")
                        )
                        pdf_filename = f"invoice_{invoice_no}.pdf"

                        # Generate PDF
                        output_path = self.generate_pdf(html_content, pdf_filename)

                        if output_path:
                            generated_files.append(output_path)
                            print(f"✓ Generated: {pdf_filename}")
                        else:
                            print(f"✗ Failed to generate: {pdf_filename}")

                    except Exception as e:
                        print(f"✗ Error processing row {row_num}: {e}")
                        continue

        except Exception as e:
            print(f"Error reading CSV file: {e}")
            return []

        return generated_files

    def generate_sample_html(self, csv_file_path, invoice_no=None):
        """Generate a sample HTML file to preview the design."""
        if not os.path.exists(csv_file_path):
            raise FileNotFoundError(f"CSV file not found: {csv_file_path}")

        with open(csv_file_path, "r", encoding="utf-8") as csvfile:
            reader = csv.DictReader(csvfile)

            # Get the first row or find specific invoice
            for row in reader:
                if invoice_no is None or row["invoice_no"] == invoice_no:
                    html_content = self.generate_invoice_html(row)

                    # Save HTML preview
                    preview_path = os.path.join(
                        self.output_dir, f"preview_{row['invoice_no']}.html"
                    )
                    with open(preview_path, "w", encoding="utf-8") as f:
                        f.write(html_content)

                    print(f"✓ Generated HTML preview: {preview_path}")
                    return preview_path

        return None


def main():
    """Main function to run the invoice generator."""
    print("🧾 Simple Invoice Generator")
    print("=" * 50)

    # Initialize generator
    generator = SimpleInvoiceGenerator()

    # Check if CSV file exists
    csv_file = "invoices_data.csv"
    if not os.path.exists(csv_file):
        print(f"❌ CSV file '{csv_file}' not found!")
        print("Please ensure the CSV file exists in the current directory.")
        return

    # Check if template exists
    if not os.path.exists(generator.template_path):
        print(f"❌ Template file '{generator.template_path}' not found!")
        return

    print(f"📄 Using template: {generator.template_path}")
    print(f"📊 Reading data from: {csv_file}")
    print(f"📁 Output directory: {generator.output_dir}")
    print("-" * 50)

    # Generate HTML preview for first invoice
    print("🖼️  Generating HTML preview...")
    preview_path = generator.generate_sample_html(csv_file)

    if preview_path:
        print(f"✓ HTML preview saved to: {preview_path}")
        print("   You can open this file in a browser to preview the design.")

    print("-" * 50)

    # Check PDF generation capability
    if generator.check_weasyprint():
        print("✅ WeasyPrint is available - generating PDFs...")
        print("🔄 Generating PDF invoices...")

        # Generate all PDFs
        generated_files = generator.process_csv(csv_file)

        print("-" * 50)
        print(f"✅ Successfully generated {len(generated_files)} invoice(s)")

        if generated_files:
            print("\n📋 Generated files:")
            for file_path in generated_files:
                print(f"   • {os.path.basename(file_path)}")

            print(f"\n📁 All files saved in: {generator.output_dir}/")
    else:
        print("⚠️  WeasyPrint not working - HTML previews only")
        print("   You can manually convert HTML files to PDF using your browser")
        print("   Or install wkhtmltopdf and use the browser method")


if __name__ == "__main__":
    main()
