# AI-Lamb Scripts

This directory contains utility scripts for the AI-Lamb SAST tool.

## Report Generator

### `generate_report.py`

An agentic AI-powered script that processes SAST findings from a markdown file and generates a comprehensive HTML security report.

#### Features

- **Agentic AI Processing**: Uses LangChain agents to analyze and categorize vulnerabilities
- **Executive Summary**: Generates professional executive summaries for stakeholders
- **Actionable Recommendations**: Creates specific, actionable security recommendations
- **Professional HTML Output**: Produces beautifully formatted HTML reports
- **Vulnerability Categorization**: Automatically categorizes findings by type and severity

#### Usage

```bash
# Basic usage (uses default paths)
python scripts/generate_report.py

# Specify custom input and output files
python scripts/generate_report.py --input ../data/sast.md --output my-report.html

# Use custom OpenAI API key
python scripts/generate_report.py --api-key your-openai-api-key

# Help
python scripts/generate_report.py --help
```

#### Requirements

- OpenAI API key (set as environment variable `OPENAI_API_KEY` or pass via `--api-key`)
- All dependencies from `requirements.txt`
- Input SAST findings file in markdown format

#### Input Format

The script expects a markdown file with SAST findings in the following format:

```markdown
# SAST Analysis Findings

## Vulnerability Findings

### Critical Vulnerabilities
- **Location**: file.py:line
- **Description**: Vulnerability description
- **Impact**: Potential impact
- **Code**: Code snippet

### High Severity Vulnerabilities
...

## Recommendations
...
```

#### Output

The script generates a professional HTML report with:

- **Executive Summary**: High-level overview of findings
- **Vulnerability Analysis**: Detailed analysis of each finding
- **Security Recommendations**: Actionable recommendations
- **Professional Styling**: Clean, modern HTML design

#### Example

```bash
# Generate report from sample data
python scripts/generate_report.py --input ../data/sast.md --output ai-lamb-report.html

# View the generated report
open ai-lamb-report.html
```

#### Agentic AI Workflow

The script uses a multi-step agentic AI workflow:

1. **Analysis**: Analyzes and categorizes vulnerabilities by type and severity
2. **Summary**: Generates executive summary for stakeholders
3. **Recommendations**: Creates actionable security recommendations
4. **Formatting**: Formats everything into professional HTML report

#### Error Handling

- Validates input file existence
- Handles API errors gracefully
- Provides clear error messages
- Ensures proper file encoding

#### Configuration

The script can be configured via:

- Command line arguments
- Environment variables
- Default values for common use cases

#### Integration

This script is designed to work with the main AI-Lamb SAST tool and can be integrated into:

- CI/CD pipelines
- Automated security workflows
- Manual security assessments
- Compliance reporting
