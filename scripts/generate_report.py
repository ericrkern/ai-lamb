#!/usr/bin/env python3
"""
AI-Lamb Report Generator

This script processes SAST findings from a markdown file and uses agentic AI
to generate a comprehensive HTML report summarizing all security findings.
"""

import os
import sys
import json
import argparse
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Type

# Add the parent directory to the path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from langchain.agents import create_react_agent, AgentExecutor
    from langchain.llms import OpenAI
    from langchain.tools import BaseTool
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
    from langchain.callbacks.manager import CallbackManagerForToolRun
    from pydantic import BaseModel, Field
    from dotenv import load_dotenv
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install: {e}")
    sys.exit(1)

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class AnalysisInput(BaseModel):
    findings: str = Field(description="SAST findings text to analyze")


class SummaryInput(BaseModel):
    analysis: str = Field(description="Analysis results to summarize")


class RecommendationsInput(BaseModel):
    analysis: str = Field(description="Analysis results to create recommendations from")


class HTMLFormatInput(BaseModel):
    summary: str = Field(description="Executive summary")
    analysis: str = Field(description="Vulnerability analysis")
    recommendations: str = Field(description="Security recommendations")


class AnalyzeFindingsTool(BaseTool):
    name: str = "analyze_findings"
    description: str = "Analyze SAST findings and categorize vulnerabilities by type, severity, and impact"
    args_schema: Type[AnalysisInput] = AnalysisInput

    def _run(
        self, findings: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Analyze SAST findings and categorize vulnerabilities."""
        
        analysis_prompt = PromptTemplate(
            input_variables=["findings"],
            template="""
            Perform a comprehensive analysis of the following SAST findings and categorize them by:
            
            1. Vulnerability type:
               - XML Parser Misconfigurations (XXE)
               - HTML-to-PDF Converter Vulnerabilities (SSRF)
               - Template Injection Vulnerabilities (SSTI)
               - Other injection vulnerabilities
               - Information disclosure
               - Configuration issues
            
            2. Severity level (Critical, High, Medium, Low) with justification
            
            3. Affected components and files
            
            4. Potential impact and attack vectors
            
            5. CWE (Common Weakness Enumeration) mappings where applicable
            
            6. CVSS (Common Vulnerability Scoring System) base scores
            
            SAST Findings:
            {findings}
            
            Return a comprehensive JSON object with the analysis including:
            - vulnerability_summary (total counts by type and severity)
            - detailed_findings (list of each vulnerability with full analysis)
            - risk_assessment (overall risk level and justification)
            - affected_repositories (list of repositories with vulnerability counts)
            - attack_scenarios (potential attack scenarios for critical/high findings)
            """
        )
        
        llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
        chain = LLMChain(llm=llm, prompt=analysis_prompt)
        result = chain.run(findings=findings)
        
        logger.info("Analysis completed successfully")
        return result

    async def _arun(
        self, findings: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("analyze_findings does not support async")


class GenerateSummaryTool(BaseTool):
    name: str = "generate_summary"
    description: str = "Generate executive summary of findings for stakeholders"
    args_schema: Type[SummaryInput] = SummaryInput

    def _run(
        self, analysis: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Generate executive summary of findings."""
        
        summary_prompt = PromptTemplate(
            input_variables=["analysis"],
            template="""
            Create a professional executive summary of the SAST analysis findings suitable for:
            - C-level executives
            - Security teams
            - Development managers
            - Compliance officers
            
            Focus on:
            - Total number of vulnerabilities found and their distribution
            - Critical and high-severity issues requiring immediate attention
            - Most common vulnerability types and patterns
            - Overall security posture assessment
            - Business impact and risk exposure
            - Key recommendations for immediate action
            
            Analysis: {analysis}
            
            Provide a concise, professional summary that highlights the most important findings
            and their business implications. Use clear, non-technical language where possible.
            """
        )
        
        llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
        chain = LLMChain(llm=llm, prompt=summary_prompt)
        summary = chain.run(analysis=analysis)
        
        logger.info("Executive summary generated successfully")
        return summary

    async def _arun(
        self, analysis: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("generate_summary does not support async")


class CreateRecommendationsTool(BaseTool):
    name: str = "create_recommendations"
    description: str = "Create actionable security recommendations with priority levels"
    args_schema: Type[RecommendationsInput] = RecommendationsInput

    def _run(
        self, analysis: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Create actionable security recommendations with priority levels."""
        
        recommendations_prompt = PromptTemplate(
            input_variables=["analysis"],
            template="""
            Based on the SAST analysis, create detailed, actionable security recommendations.
            
            For each recommendation, provide:
            1. Priority level (Immediate, High, Medium, Low)
            2. Specific action items
            3. Implementation steps
            4. Expected outcome
            5. Resource requirements (time, effort, expertise)
            6. Related vulnerabilities addressed
            
            Focus on:
            - Immediate remediation steps for critical vulnerabilities
            - Code fixes and best practices implementation
            - Security architecture improvements
            - Prevention measures and security controls
            - Training and awareness requirements
            - Monitoring and detection capabilities
            
            Analysis: {analysis}
            
            Return a structured list of recommendations with all the above details.
            """
        )
        
        llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
        chain = LLMChain(llm=llm, prompt=recommendations_prompt)
        result = chain.run(analysis=analysis)
        
        logger.info("Security recommendations created successfully")
        return result

    async def _arun(
        self, analysis: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("create_recommendations does not support async")


class FormatHTMLTool(BaseTool):
    name: str = "format_html"
    description: str = "Format findings into professional HTML report with modern styling"
    args_schema: Type[HTMLFormatInput] = HTMLFormatInput

    def _run(
        self, summary: str, analysis: str, recommendations: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Format findings into professional HTML report."""
        
        html_template = PromptTemplate(
            input_variables=["summary", "analysis", "recommendations", "timestamp"],
            template="""
            Create a professional, modern HTML report for SAST findings with the following structure:
            
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI-Lamb SAST Security Report</title>
                <style>
                    * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                    body {{ 
                        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; 
                        line-height: 1.6; 
                        color: #333; 
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        min-height: 100vh;
                    }}
                    .container {{ 
                        max-width: 1200px; 
                        margin: 0 auto; 
                        background: white; 
                        margin: 20px auto;
                        border-radius: 15px; 
                        box-shadow: 0 20px 40px rgba(0,0,0,0.1);
                        overflow: hidden;
                    }}
                    .header {{ 
                        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
                        color: white;
                        text-align: center; 
                        padding: 40px 30px;
                    }}
                    .header h1 {{ 
                        font-size: 2.5em; 
                        margin-bottom: 10px;
                        text-shadow: 2px 2px 4px rgba(0,0,0,0.3);
                    }}
                    .header .subtitle {{ 
                        font-size: 1.2em; 
                        opacity: 0.9;
                    }}
                    .content {{ padding: 40px; }}
                    .section {{ 
                        margin: 40px 0; 
                        padding: 30px;
                        background: #f8f9fa;
                        border-radius: 10px;
                        border-left: 5px solid #e74c3c;
                    }}
                    .section h2 {{ 
                        color: #e74c3c; 
                        font-size: 1.8em;
                        margin-bottom: 20px;
                        display: flex;
                        align-items: center;
                    }}
                    .section h2::before {{
                        content: attr(data-icon);
                        margin-right: 10px;
                        font-size: 1.2em;
                    }}
                    .vulnerability {{ 
                        background: white; 
                        border-left: 4px solid #e74c3c; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-radius: 8px;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .critical {{ border-left-color: #e74c3c; }}
                    .high {{ border-left-color: #f39c12; }}
                    .medium {{ border-left-color: #f1c40f; }}
                    .low {{ border-left-color: #27ae60; }}
                    .recommendation {{ 
                        background: #e8f5e8; 
                        border-left: 4px solid #27ae60; 
                        padding: 20px; 
                        margin: 15px 0; 
                        border-radius: 8px;
                    }}
                    .priority-immediate {{ background: #ffe6e6; border-left-color: #e74c3c; }}
                    .priority-high {{ background: #fff3cd; border-left-color: #f39c12; }}
                    .priority-medium {{ background: #e8f5e8; border-left-color: #27ae60; }}
                    .priority-low {{ background: #f8f9fa; border-left-color: #6c757d; }}
                    .timestamp {{ 
                        text-align: center; 
                        color: #6c757d; 
                        font-style: italic; 
                        margin-top: 40px;
                        padding: 20px;
                        border-top: 1px solid #dee2e6;
                    }}
                    .stats {{ 
                        display: grid; 
                        grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); 
                        gap: 20px; 
                        margin: 20px 0;
                    }}
                    .stat-card {{ 
                        background: white; 
                        padding: 20px; 
                        border-radius: 8px; 
                        text-align: center;
                        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
                    }}
                    .stat-number {{ 
                        font-size: 2em; 
                        font-weight: bold; 
                        color: #e74c3c;
                    }}
                    .stat-label {{ 
                        color: #6c757d; 
                        margin-top: 5px;
                    }}
                    code {{ 
                        background: #f8f9fa; 
                        padding: 2px 6px; 
                        border-radius: 4px; 
                        font-family: 'Courier New', monospace;
                    }}
                    pre {{ 
                        background: #f8f9fa; 
                        padding: 15px; 
                        border-radius: 8px; 
                        overflow-x: auto;
                        margin: 10px 0;
                    }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🐑 AI-Lamb SAST Security Report</h1>
                        <div class="subtitle">Static Application Security Testing Analysis</div>
                        <div style="margin-top: 10px; font-size: 0.9em; opacity: 0.8;">
                            Generated by AI-Lamb using OpenAI GPT-4
                        </div>
                    </div>
                    
                    <div class="content">
                        <div class="section">
                            <h2 data-icon="📋">Executive Summary</h2>
                            {summary}
                        </div>
                        
                        <div class="section">
                            <h2 data-icon="🔍">Vulnerability Analysis</h2>
                            {analysis}
                        </div>
                        
                        <div class="section">
                            <h2 data-icon="✅">Security Recommendations</h2>
                            {recommendations}
                        </div>
                        
                        <div class="timestamp">
                            Report generated on {timestamp}
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        )
        
        llm = OpenAI(api_key=os.getenv('OPENAI_API_KEY'), temperature=0.1)
        chain = LLMChain(llm=llm, prompt=html_template)
        html_report = chain.run(
            summary=summary,
            analysis=analysis,
            recommendations=recommendations,
            timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )
        
        logger.info("HTML report formatting completed")
        return html_report

    async def _arun(
        self, summary: str, analysis: str, recommendations: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("format_html does not support async")


class SASTReportGenerator:
    """Agentic AI-powered SAST report generator using ReAct pattern."""
    
    def __init__(self, openai_api_key: str = None, model_name: str = "gpt-4"):
        """Initialize the report generator with OpenAI API key."""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it as parameter.")
        
        self.model_name = model_name
        self.setup_agent()
        logger.info(f"Initialized SAST Report Generator with model: {model_name}")
    
    def setup_agent(self):
        """Setup the agentic AI system with tools and ReAct agent."""
        
        # Define tools
        tools = [
            AnalyzeFindingsTool(),
            GenerateSummaryTool(),
            CreateRecommendationsTool(),
            FormatHTMLTool()
        ]
        
        # Define LLM
        llm = OpenAI(api_key=self.openai_api_key, temperature=0.1, model_name=self.model_name)
        
        # Define instructions and prompt
        instructions = """
        You are an agentic AI system designed to generate comprehensive SAST security reports.

        ### Analysis Process
        1. **Analyze Findings**: Use the analyze_findings tool to process SAST findings and categorize vulnerabilities
        2. **Generate Summary**: Use the generate_summary tool to create an executive summary
        3. **Create Recommendations**: Use the create_recommendations tool to generate actionable security recommendations
        4. **Format HTML**: Use the format_html tool to create a professional HTML report

        ### **TOOLS**
        You have access to the following tools to process SAST findings and generate reports.

        ### **Output Format**
        Your final response must be a complete HTML report that includes:
        - Executive summary
        - Vulnerability analysis
        - Security recommendations
        - Professional formatting

        TOOLS:
        ------

        You have access to the following tools:

        {tools}

        You must use tools to complete the task. Please use the following format:

        ```
        Thought: Do I need to use a tool? Yes
        Action: the action to take, should be one of [{tool_names}]
        Action Input: the input to the action
        Observation: the result of the action
        ```

        When you have a complete HTML report to return to the Human, 
        use the format:

        ```
        Thought: Do I need to use a tool? No
        Final Answer: [your complete HTML report here]
        ```

        Begin!

        Input: {input}
        {agent_scratchpad}
        """
        
        prompt = PromptTemplate.from_template(instructions)
        
        # Create agent and executor
        self.agent = create_react_agent(llm, tools, prompt)
        self.agent_executor = AgentExecutor(
            agent=self.agent, 
            tools=tools, 
            verbose=True, 
            handle_parsing_errors=True,
            max_iterations=15
        )
        logger.info("ReAct agent system initialized successfully")
    
    def generate_report(self, input_file: str, output_file: str) -> bool:
        """Generate the complete SAST report using agentic AI."""
        
        try:
            # Read the SAST findings file
            with open(input_file, 'r', encoding='utf-8') as f:
                findings_text = f.read()
            
            logger.info(f"Reading SAST findings from: {input_file}")
            
            # Use the agent to generate the complete report
            logger.info("Using agentic AI to generate comprehensive report...")
            
            response = self.agent_executor.invoke({"input": findings_text})
            
            # Extract the HTML report from the response
            if "Final Answer:" in response.get('output', ''):
                html_report = response['output'].split("Final Answer:")[-1].strip()
            else:
                html_report = response.get('output', '')
            
            # Write the HTML report
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            logger.info(f"HTML report generated successfully: {output_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error generating report: {e}")
            return False


def main():
    """Main function to run the report generator."""
    
    parser = argparse.ArgumentParser(description='Generate AI-Lamb SAST Security Report')
    parser.add_argument('--input', '-i', default='../data/sast.md',
                       help='Input SAST findings file (default: ../data/sast.md)')
    parser.add_argument('--output', '-o', default='ai-lamb-report.html',
                       help='Output HTML report file (default: ai-lamb-report.html)')
    parser.add_argument('--api-key', '-k', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    parser.add_argument('--model', '-m', default='gpt-4', 
                       help='OpenAI model to use (default: gpt-4)')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose logging')
    
    args = parser.parse_args()
    
    # Set logging level
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    # Ensure input file exists
    if not os.path.exists(args.input):
        logger.error(f"Input file '{args.input}' not found.")
        print("Please ensure the SAST findings file exists in the data directory.")
        sys.exit(1)
    
    try:
        # Initialize the report generator
        generator = SASTReportGenerator(openai_api_key=args.api_key, model_name=args.model)
        
        # Generate the report
        success = generator.generate_report(args.input, args.output)
        
        if success:
            print("\n🎉 Report generation completed successfully!")
            print(f"📊 View the report: {args.output}")
            print(f"🤖 Generated using: {args.model}")
        else:
            print("\n❌ Report generation failed.")
            sys.exit(1)
            
    except Exception as e:
        logger.error(f"Error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
