```
    ╭─────────────────────────────────────────────────────────────╮
    │                                                             │
    │                    🐑 AI-Lamb 🐑                          │
    │                                                             │
    │                           ╭─────────╮                      │
    │                          ╭─╯  ╭───╮  ╰─╮                  │
    │                          │   ╭─╯ • • ╰─╮   │                  │
    │                          │   │   ╭─╯ ╰─╮   │                  │
    │                          │   │   │  •  │   │                  │
    │                          │   │   ╰─────╯   │                  │
    │                          │   ╰─────────────╯                  │
    │                          ╰─────────────────╯                  │
    │                                │                               │
    │                                │                               │
    │                           ╭────┴────╮                         │
    │                           │         │                         │
    │                           │  SAST   │                         │
    │                           │  TOOL   │                         │
    │                           ╰─────────╯                         │
    │                                                             │
    ╰─────────────────────────────────────────────────────────────╯
```

# AI-Lamb: AI-Powered SAST Security Platform

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Security](https://img.shields.io/badge/security-AI%20Powered-red.svg)](https://github.com/Sham-Report/ai-lamb)

## 🚀 Overview

AI-Lamb is a focused **Python-based** AI-powered **SAST (Static Application Security Testing)** tool designed to investigate specific vulnerabilities in SaaS (Software-as-a-Service) codebases. Built with modern Python AI/ML technologies, this platform performs static code analysis to identify three critical security issues: misconfigured XML parsers, HTML-to-PDF converter vulnerabilities, and template injection vulnerabilities in templating systems.

### 🎯 Target Repositories

AI-Lamb is specifically designed to analyze the following repositories that contain HTML-to-PDF conversion and templating functionality:

#### [Imprenta Repository](https://github.com/alfredo/imprenta)
An AWS Lambda service that generates PDF files from HTML using jinja, pdfkit and wkhtmltopdf. This repository is an ideal target for our SAST analysis as it contains:

- **HTML-to-PDF conversion functionality** using wkhtmltopdf
- **Template rendering** with Jinja templating engine
- **XML processing** capabilities through PDF generation
- **Web service endpoints** that process user input

#### [Invoice Generator Repository](https://github.com/Blankscreen-exe/invoice_generator)
A Python invoice generator built with Jinja2 and WeasyPrint. This repository is another excellent target for our SAST analysis as it contains:

- **HTML-to-PDF conversion functionality** using WeasyPrint
- **Template rendering** with Jinja2 templating engine
- **User input processing** through data.json and settings.py
- **Template customization** capabilities that process user-provided data

## ✨ Features

### 🎯 SAST Vulnerability Focus

AI-Lamb performs static application security testing to identify three specific critical vulnerabilities in HTML-to-PDF conversion repositories:

- **XML Parser Misconfigurations**: Static analysis of codebase for misconfigured XML parsers that could lead to XXE (External XML Entity) injection vulnerabilities
- **HTML-to-PDF Converter Vulnerabilities**: Static scanning for potential SSRF (Server-Side Request Forgery) and other security issues in HTML-to-PDF conversion systems using wkhtmltopdf and WeasyPrint
- **Template Injection Vulnerabilities**: Static identification of templating systems where user input is executed by the Jinja/Jinja2 templating engines, potentially leading to Server-Side Template Injection (SSTI)

### 🔍 SAST Analysis Capabilities
- **XML Parser Analysis**: Static identification of misconfigured XML parsers and potential XXE vulnerabilities in PDF generation
- **HTML-to-PDF Converter Scanning**: Static detection of SSRF and security issues in wkhtmltopdf and WeasyPrint conversion systems
- **Template Engine Analysis**: Static analysis of Jinja/Jinja2 templating systems with user input execution vulnerabilities
- **Code Pattern Recognition**: AI-powered identification of vulnerable code patterns through static analysis
- **Static Code Analysis**: Deep static analysis of source code for specific vulnerability types in Python applications and AWS Lambda functions







## 🤖 AI-Powered Capabilities

AI-Lamb leverages advanced artificial intelligence and machine learning technologies to provide intelligent security analysis:

### 🧠 LangChain Integration
- **AI Orchestration**: Seamless integration of multiple AI models and tools
- **Workflow Automation**: Automated security analysis pipelines
- **Tool Integration**: Connects various security tools and APIs

### 📝 Prompt Engineering & Context Management
- **Intelligent Prompts**: Optimized prompts for vulnerability detection
- **Context Awareness**: Maintains security context across analysis sessions
- **Dynamic Prompting**: Adapts prompts based on target application type

### 🔍 Embeddings & Vector Stores
- **Code Embeddings**: Converts source code into searchable vectors
- **Vulnerability Patterns**: Stores and retrieves known vulnerability signatures
- **Semantic Search**: Finds similar vulnerabilities across different codebases

### 🚀 LLM Exploration & Integration
- **Multi-Model Support**: Integration with various LLM providers (OpenAI, Anthropic, etc.)
- **Model Selection**: Intelligent selection of appropriate models for specific tasks
- **Response Optimization**: Enhanced LLM responses for security analysis

### 💬 ChatBot Assistant
- **Security Expert AI**: Interactive chatbot for security guidance
- **Vulnerability Explanation**: Natural language explanations of detected issues
- **Remediation Guidance**: Step-by-step remediation suggestions

### 🛡️ Dynamic AppSec AI
- **Adaptive Scanning**: AI-driven vulnerability scanning strategies
- **Threat Intelligence**: Real-time threat intelligence integration
- **Risk Assessment**: AI-powered risk scoring and prioritization

### 📊 SAST Source Code Analysis
- **XML Parser Analysis**: Static identification of misconfigured XML parsers and XXE vulnerabilities
- **HTML-to-PDF Analysis**: Static detection of SSRF vulnerabilities in PDF conversion systems
- **Template Engine Analysis**: Static analysis of template injection vulnerabilities in templating systems
- **Pattern Recognition**: Static identification of vulnerable code patterns and anti-patterns
- **Automated Code Review**: AI-powered static security code review with insights

### 🤖 Agentic AI
- **Autonomous Agents**: Self-directed security analysis agents
- **Multi-Agent Coordination**: Coordinated analysis across multiple agents
- **Goal-Oriented Scanning**: AI agents that work towards specific security objectives



## 📋 Prerequisites

Before you begin, ensure you have the following installed:
- **Python 3.8 or higher** (primary requirement)
- Node.js 16+ (optional, for frontend)
- Docker and Docker Compose (optional)
- PostgreSQL 12+ (optional)
- Redis 6+ (optional)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Sham-Report/ai-lamb.git
cd ai-lamb
```

### 2. Set Up Environment
```bash
# Copy environment template
cp .env.example .env

# Edit environment variables
nano .env
```

### 3. Install Dependencies
```bash
# Install Python dependencies
pip install -r requirements.txt

# Optional: Install frontend dependencies
cd frontend
npm install
```

### 4. Start Services
```bash
# Run the Python application directly
python app/main.py

# Or using Docker Compose (optional)
docker-compose up -d
```

### 5. Access the Platform
- **Web Interface**: http://localhost:3000
- **API Documentation**: http://localhost:8000/docs
- **Admin Dashboard**: http://localhost:3000/admin

## 📁 Project Structure

```
ai-lamb/
├── app/                    # Main Python application code
│   ├── api/               # API endpoints
│   ├── core/              # Core functionality
│   ├── ml/                # Machine learning models
│   ├── ai/                # AI/LLM integration modules
│   │   ├── langchain/     # LangChain integration
│   │   ├── prompts/       # Prompt engineering
│   │   ├── embeddings/    # Vector embeddings
│   │   ├── agents/        # AI agents
│   │   └── chatbot/       # ChatBot assistant
│   ├── security/          # Security modules
│   └── utils/             # Utility functions
├── frontend/              # React frontend (optional)
├── tests/                 # Python test suite
├── docs/                  # Documentation
├── config/                # Configuration files
├── scripts/               # Python utility scripts
├── requirements.txt       # Python dependencies
├── vector_store/          # Vector database storage
└── docker/                # Docker configurations (optional)
```

## 🔧 Configuration

### Environment Variables

Create a `.env` file with the following variables:

```env
# Database
DATABASE_URL=postgresql://user:password@localhost/ai_lamb
REDIS_URL=redis://localhost:6379

# Security
SECRET_KEY=your-secret-key-here
JWT_SECRET=your-jwt-secret-here

# AI/ML
MODEL_PATH=/path/to/ml/models
API_KEYS_OPENAI=your-openai-api-key

# External Services
SLACK_WEBHOOK_URL=your-slack-webhook
EMAIL_SMTP_HOST=smtp.gmail.com
EMAIL_SMTP_PORT=587
```

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test suite
pytest tests/test_security.py
```

## 📚 API Documentation

The API documentation is available at `/docs` when the server is running. Key endpoints include:

### SAST Analysis Endpoints
- `POST /api/v1/sast/analyze` - Complete static application security testing
- `POST /api/v1/sast/xml/analyze` - Static XML parser misconfiguration analysis
- `POST /api/v1/sast/pdf-converter/analyze` - Static HTML-to-PDF converter vulnerability scanning
- `POST /api/v1/sast/template/analyze` - Static template injection vulnerability detection

### AI-Powered Analysis Endpoints
- `POST /api/v1/ai/analyze` - AI-powered code analysis
- `POST /api/v1/ai/chat` - Security chatbot interaction
- `POST /api/v1/ai/embed` - Generate code embeddings
- `POST /api/v1/ai/agent` - Autonomous AI agent execution

### Data & Analytics Endpoints
- `GET /api/v1/vulnerabilities` - List detected vulnerabilities
- `POST /api/v1/remediation/suggest` - Automated remediation suggestions
- `GET /api/v1/analytics/sast-dashboard` - SAST security analytics
- `GET /api/v1/vector/search` - Semantic vulnerability search

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guidelines](CONTRIBUTING.md) for details.

### Development Setup

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Commit your changes: `git commit -m 'Add amazing feature'`
4. Push to the branch: `git push origin feature/amazing-feature`
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

- **Documentation**: [docs.ai-lamb.com](https://docs.ai-lamb.com)
- **Issues**: [GitHub Issues](https://github.com/Sham-Report/ai-lamb/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Sham-Report/ai-lamb/discussions)
- **Email**: support@ai-lamb.com

## 🙏 Acknowledgments

- Thanks to the open-source community for the amazing tools and libraries
- Special thanks to our contributors and beta testers
- Inspired by modern security practices and AI advancements

## 🔮 Roadmap

### Core SAST Features
- [ ] Advanced static XML parser misconfiguration detection
- [ ] Enhanced static HTML-to-PDF converter vulnerability scanning
- [ ] Specialized static template injection vulnerability detection
- [ ] Zero-day vulnerability pattern recognition through static analysis

### AI/ML Enhancements
- [ ] Advanced LangChain integration with custom SAST analysis tools
- [ ] Intelligent prompt engineering for static vulnerability detection
- [ ] Vector database integration for vulnerability pattern matching
- [ ] Multi-LLM support with model selection optimization
- [ ] Autonomous AI agents for static code analysis
- [ ] AI-powered static source code analysis and review

### Platform Features
- [ ] Integration with development workflows (GitHub, GitLab, CI/CD)
- [ ] Automated SAST code review and reporting
- [ ] Integration with popular development platforms
- [ ] Advanced SAST security analytics and reporting
- [ ] Multi-repository static analysis support
- [ ] Automated vulnerability reporting and tracking

---

**⚠️ Security Notice**: This is a SAST (Static Application Security Testing) tool. Please ensure you have proper authorization before analyzing any codebases, and follow all applicable security best practices and terms of service.

**Made with ❤️ by the AI-Lamb Team**
