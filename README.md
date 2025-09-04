# 🚀 Enhanced Invoice Generator

A modern, professional invoice generation system that creates beautiful PDF invoices from CSV data using customizable HTML templates.

## ✨ Key Features

- 🎨 **Modern Design**: Clean, professional templates with contemporary styling
- 📱 **Responsive Layout**: Works perfectly on all screen sizes and devices
- 🏢 **Brand Customization**: Easy logo and company branding integration
- 📊 **Bulk Processing**: Generate hundreds of invoices from CSV data
- 📄 **Multiple Formats**: PDF generation + HTML previews
- 🔧 **Highly Configurable**: Extensive customization options
- 🛡️ **Robust Validation**: Built-in data validation and error handling
- 📈 **Progress Tracking**: Real-time progress indication and detailed reporting
- 🎯 **CLI Interface**: Command-line tools for automation and scripting

## 🏗️ Architecture

```
enhanced-invoice-generator/
├── 📄 Templates
│   ├── invoice_template_modern.html    # Modern template with Inter font
│   └── invoice_template.html           # Original template (fallback)
├── 🐍 Core Generators
│   ├── enhanced_generator.py           # Main enhanced generator
│   ├── generate_invoices.py           # Original generator
│   └── simple_generator.py            # Simplified version
├── 🖥️ CLI Interface
│   └── cli_generator.py               # Rich CLI with progress bars
├── ⚙️ Configuration
│   ├── config.ini                     # Main configuration file
│   └── requirements.txt               # Python dependencies
├── 📊 Data
│   └── invoices_data.csv              # Sample invoice data
└── 📁 Output
    └── generated_invoices/            # Generated files directory
```

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the project
git clone <repository-url>
cd enhanced-invoice-generator

# Install dependencies
pip install -r requirements.txt
```

**macOS Users**: WeasyPrint requires system libraries:
```bash
brew install cairo pango gdk-pixbuf libffi
```

### 2. Interactive Setup

```bash
python cli_generator.py setup
```

This will:
- Check all dependencies
- Validate your environment
- Create sample files if needed
- Guide you through the setup process

### 3. Generate Invoices

**Simple Generation:**
```bash
python cli_generator.py generate
```

**Advanced Options:**
```bash
# Custom files and options
python cli_generator.py generate --csv my_data.csv --template custom_template.html --output my_invoices/

# Preview only (no PDFs)
python cli_generator.py generate --preview-only

# Skip confirmations
python cli_generator.py generate --force
```

## 📋 CSV Data Format

Your CSV file should include these columns:

| Column | Description | Example |
|--------|-------------|---------|
| `invoice_no` | Unique invoice identifier | `INV-001` |
| `date` | Invoice date (YYYY-MM-DD) | `2025-01-15` |
| `bill_to` | Customer/client name | `John Smith` |
| `contact_no` | Customer contact | `+1-555-0123` |
| `billing_address` | Full billing address | `123 Main St, New York, NY 10001` |
| `product` | Product/service names (pipe-separated) | `Web Development\|Hosting` |
| `quantity` | Quantities (pipe-separated) | `1\|12` |
| `price` | Unit prices (pipe-separated) | `1500.00\|25.00` |
| `payment_method` | Payment method | `Credit Card` |

### Sample CSV Data:
```csv
invoice_no,date,bill_to,contact_no,billing_address,product,quantity,price,payment_method
INV-001,2025-01-15,John Smith,+1-555-0123,"123 Main St, New York, NY 10001","Web Development|Hosting Services",1|12,1500.00|25.00,Credit Card
INV-002,2025-01-16,Sarah Johnson,+1-555-0456,"456 Oak Ave, Los Angeles, CA 90210","Logo Design|Business Cards",1|500,800.00|2.50,PayPal
```

## 🎨 Design System

The modern template features:

### Color Palette
- **Primary**: `#2563eb` (Professional Blue)
- **Primary Dark**: `#1d4ed8` (Darker Blue)
- **Secondary**: `#64748b` (Slate Gray)
- **Accent**: `#f59e0b` (Amber)
- **Success**: `#10b981` (Emerald)

### Typography
- **Font**: Inter (Google Fonts) with system fallbacks
- **Weights**: 300, 400, 500, 600, 700
- **Optimized**: Anti-aliased rendering for crisp text

### Layout Features
- **Responsive Grid**: Adapts to different screen sizes
- **Card-based Design**: Clean, modern information cards
- **Professional Tables**: Styled data tables with hover effects
- **Print Optimization**: Perfect formatting for PDF generation

## 🔧 CLI Commands

### Generate Invoices
```bash
# Basic generation
python cli_generator.py generate

# With custom options
python cli_generator.py generate --csv data.csv --template modern.html --output invoices/
```

### Validate Data
```bash
# Validate CSV structure and data
python cli_generator.py validate --csv invoices_data.csv
```

### Preview Invoices
```bash
# Generate HTML preview
python cli_generator.py preview

# Preview specific invoice
python cli_generator.py preview --invoice INV-001
```

### Setup Wizard
```bash
# Interactive setup
python cli_generator.py setup
```

## ⚙️ Configuration

Edit `config.ini` to customize:

```ini
[COMPANY]
company_name = Your Company Name
company_tagline = Your Tagline
logo_path = your_logo.png

[STYLING]
primary_color = #2563eb
accent_color = #f59e0b
font_family = Inter, sans-serif

[INVOICE_SETTINGS]
default_due_days = 30
tax_rate = 0.0
currency_symbol = $
```

## 🛠️ Advanced Usage

### Programmatic Usage

```python
from enhanced_generator import EnhancedInvoiceGenerator

# Initialize generator
generator = EnhancedInvoiceGenerator(
    template_path="custom_template.html",
    output_dir="my_invoices"
)

# Process CSV file
results = generator.process_csv("data.csv")

# Generate summary report
report_path = generator.generate_summary_report(results)
```

### Custom Templates

Create your own templates using the placeholder system:

```html
<div class="invoice-number">#{invoice_no}</div>
<div class="client-name">{bill_to}</div>
<div class="invoice-date">{date}</div>
<!-- Items table -->
<tbody>{items_rows}</tbody>
<div class="total">${total_bill}</div>
```

## 📊 Output & Reporting

The generator creates:

- **PDF Files**: Professional invoices ready for sending
- **HTML Previews**: For browser viewing and testing
- **Summary Reports**: JSON reports with generation statistics
- **Log Files**: Detailed processing logs for debugging

### Sample Output Structure:
```
generated_invoices/
├── invoice_INV-001.pdf
├── invoice_INV-002.pdf
├── preview_INV-001.html
├── preview_INV-002.html
├── generation_report_20250115_143022.json
└── invoice_generator.log
```

## 🔍 Validation & Error Handling

The system includes comprehensive validation:

- **CSV Structure**: Validates required columns and data types
- **Data Integrity**: Checks for missing or invalid values
- **Template Validation**: Ensures template files exist and are readable
- **Dependency Checks**: Verifies all required libraries are available
- **Error Recovery**: Continues processing even if individual invoices fail

## 🚀 Performance Features

- **Batch Processing**: Efficiently handles large CSV files
- **Progress Tracking**: Real-time progress indication
- **Memory Optimization**: Processes invoices one at a time
- **Error Isolation**: Individual invoice failures don't stop the batch
- **Detailed Logging**: Comprehensive logging for debugging

## 🛠️ Troubleshooting

### Common Issues

**WeasyPrint Installation:**
```bash
# macOS
brew install cairo pango gdk-pixbuf libffi

# Ubuntu/Debian
sudo apt-get install python3-dev python3-pip python3-cffi python3-brotli libpango-1.0-0 libharfbuzz0b libpangoft2-1.0-0

# Windows
# Usually works with: pip install weasyprint
```

**CSV Validation Errors:**
```bash
# Check your CSV structure
python cli_generator.py validate --csv your_file.csv
```

**Template Issues:**
- Ensure template file exists
- Check file permissions
- Validate HTML syntax

## 📈 What's New

### Enhanced Features:
- ✅ Modern, professional design system
- ✅ Rich CLI interface with progress bars
- ✅ Comprehensive data validation
- ✅ Detailed error handling and reporting
- ✅ Configurable templates and styling
- ✅ Batch processing with progress tracking
- ✅ JSON summary reports
- ✅ Interactive setup wizard

### Improvements Over Original:
- 🎨 **Better Design**: Modern typography and color scheme
- 🏗️ **Better Architecture**: Modular, object-oriented design
- 🔧 **Better UX**: Rich CLI with colors and progress bars
- 🛡️ **Better Reliability**: Comprehensive validation and error handling
- 📊 **Better Reporting**: Detailed logs and summary reports

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit changes: `git commit -m 'Add amazing feature'`
4. Push to branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

- 📖 Check this README for common solutions
- 🔍 Use the validation command to check your data
- 📋 Review the generated log files for detailed error information
- 🛠️ Run the setup wizard to verify your environment

---

**Happy Invoicing!** 🧾✨

*Built with ❤️ for professional invoice generation*
