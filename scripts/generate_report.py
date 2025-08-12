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
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any

# Add the parent directory to the path to import app modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

try:
    from langchain.agents import initialize_agent, AgentType
    from langchain.llms import OpenAI
    from langchain.tools import Tool
    from langchain.prompts import PromptTemplate
    from langchain.chains import LLMChain
    from langchain.schema import Document
    from langchain.text_splitter import RecursiveCharacterTextSplitter
    from langchain.embeddings import OpenAIEmbeddings
    from langchain.vectorstores import Chroma
except ImportError as e:
    print(f"Error: Missing required dependencies. Please install: {e}")
    sys.exit(1)


class SASTReportGenerator:
    """Agentic AI-powered SAST report generator."""
    
    def __init__(self, openai_api_key: str = None):
        """Initialize the report generator with OpenAI API key."""
        self.openai_api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
        if not self.openai_api_key:
            raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY environment variable or pass it as parameter.")
        
        self.llm = OpenAI(api_key=self.openai_api_key, temperature=0.1)
        self.embeddings = OpenAIEmbeddings(openai_api_key=self.openai_api_key)
        self.setup_agent()
    
    def setup_agent(self):
        """Setup the agentic AI system with tools and prompts."""
        
        # Define tools for the agent
        tools = [
            Tool(
                name="analyze_findings",
                func=self.analyze_findings,
                description="Analyze SAST findings and categorize vulnerabilities"
            ),
            Tool(
                name="generate_summary",
                func=self.generate_summary,
                description="Generate executive summary of findings"
            ),
            Tool(
                name="create_recommendations",
                func=self.create_recommendations,
                description="Create actionable security recommendations"
            ),
            Tool(
                name="format_html",
                func=self.format_html,
                description="Format findings into professional HTML report"
            )
        ]
        
        # Initialize the agent
        self.agent = initialize_agent(
            tools=tools,
            llm=self.llm,
            agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
            verbose=True,
            handle_parsing_errors=True
        )
    
    def analyze_findings(self, findings_text: str) -> Dict[str, Any]:
        """Analyze SAST findings and categorize vulnerabilities."""
        
        analysis_prompt = PromptTemplate(
            input_variables=["findings"],
            template="""
            Analyze the following SAST findings and categorize them by:
            1. Vulnerability type (XML Parser, HTML-to-PDF, Template Injection)
            2. Severity level (Critical, High, Medium, Low)
            3. Affected components
            4. Potential impact
            
            SAST Findings:
            {findings}
            
            Return a JSON object with the analysis.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=analysis_prompt)
        result = chain.run(findings=findings_text)
        
        try:
            return json.loads(result)
        except json.JSONDecodeError:
            return {"error": "Failed to parse analysis result", "raw_result": result}
    
    def generate_summary(self, analysis: Dict[str, Any]) -> str:
        """Generate executive summary of findings."""
        
        summary_prompt = PromptTemplate(
            input_variables=["analysis"],
            template="""
            Create an executive summary of the SAST analysis findings.
            Focus on:
            - Total number of vulnerabilities found
            - Critical and high-severity issues
            - Most common vulnerability types
            - Overall security posture
            
            Analysis: {analysis}
            
            Provide a concise, professional summary suitable for stakeholders.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=summary_prompt)
        return chain.run(analysis=json.dumps(analysis))
    
    def create_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Create actionable security recommendations."""
        
        recommendations_prompt = PromptTemplate(
            input_variables=["analysis"],
            template="""
            Based on the SAST analysis, create actionable security recommendations.
            Focus on:
            - Immediate remediation steps
            - Code fixes and best practices
            - Security improvements
            - Prevention measures
            
            Analysis: {analysis}
            
            Return a list of specific, actionable recommendations.
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=recommendations_prompt)
        result = chain.run(analysis=json.dumps(analysis))
        
        # Parse recommendations into a list
        recommendations = [rec.strip() for rec in result.split('\n') if rec.strip()]
        return recommendations
    
    def format_html(self, summary: str, analysis: Dict[str, Any], recommendations: List[str]) -> str:
        """Format findings into professional HTML report."""
        
        html_template = PromptTemplate(
            input_variables=["summary", "analysis", "recommendations", "timestamp"],
            template="""
            Create a professional HTML report for SAST findings with the following structure:
            
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>AI-Lamb SAST Security Report</title>
                <style>
                    body {{ font-family: Arial, sans-serif; margin: 40px; background-color: #f5f5f5; }}
                    .container {{ max-width: 1200px; margin: 0 auto; background: white; padding: 30px; border-radius: 10px; box-shadow: 0 0 20px rgba(0,0,0,0.1); }}
                    .header {{ text-align: center; border-bottom: 3px solid #e74c3c; padding-bottom: 20px; margin-bottom: 30px; }}
                    .header h1 {{ color: #2c3e50; margin: 0; }}
                    .header .subtitle {{ color: #7f8c8d; font-size: 18px; }}
                    .section {{ margin: 30px 0; }}
                    .section h2 {{ color: #e74c3c; border-bottom: 2px solid #ecf0f1; padding-bottom: 10px; }}
                    .vulnerability {{ background: #f8f9fa; border-left: 4px solid #e74c3c; padding: 15px; margin: 15px 0; border-radius: 5px; }}
                    .critical {{ border-left-color: #e74c3c; }}
                    .high {{ border-left-color: #f39c12; }}
                    .medium {{ border-left-color: #f1c40f; }}
                    .low {{ border-left-color: #27ae60; }}
                    .recommendation {{ background: #e8f5e8; border-left: 4px solid #27ae60; padding: 15px; margin: 10px 0; border-radius: 5px; }}
                    .timestamp {{ text-align: center; color: #7f8c8d; font-style: italic; margin-top: 40px; }}
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="header">
                        <h1>🐑 AI-Lamb SAST Security Report</h1>
                        <div class="subtitle">Static Application Security Testing Analysis</div>
                    </div>
                    
                    <div class="section">
                        <h2>📋 Executive Summary</h2>
                        {summary}
                    </div>
                    
                    <div class="section">
                        <h2>🔍 Vulnerability Analysis</h2>
                        {analysis}
                    </div>
                    
                    <div class="section">
                        <h2>✅ Security Recommendations</h2>
                        {recommendations}
                    </div>
                    
                    <div class="timestamp">
                        Report generated on {timestamp}
                    </div>
                </div>
            </body>
            </html>
            """
        )
        
        chain = LLMChain(llm=self.llm, prompt=html_template)
        return chain.run(
            summary=summary,
            analysis=json.dumps(analysis, indent=2),
            recommendations="\n".join([f"<div class='recommendation'>{rec}</div>" for rec in recommendations]),
            timestamp=datetime.now().strftime("%B %d, %Y at %I:%M %p")
        )
    
    def generate_report(self, input_file: str, output_file: str) -> bool:
        """Generate the complete SAST report."""
        
        try:
            # Read the SAST findings file
            with open(input_file, 'r', encoding='utf-8') as f:
                findings_text = f.read()
            
            print(f"📖 Reading SAST findings from: {input_file}")
            
            # Use agentic AI to process the findings
            print("🤖 Using agentic AI to analyze findings...")
            
            # Step 1: Analyze findings
            analysis = self.analyze_findings(findings_text)
            print("✅ Analysis completed")
            
            # Step 2: Generate summary
            summary = self.generate_summary(analysis)
            print("✅ Summary generated")
            
            # Step 3: Create recommendations
            recommendations = self.create_recommendations(analysis)
            print("✅ Recommendations created")
            
            # Step 4: Format HTML
            html_report = self.format_html(summary, analysis, recommendations)
            print("✅ HTML formatting completed")
            
            # Write the HTML report
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(html_report)
            
            print(f"📄 HTML report generated: {output_file}")
            return True
            
        except Exception as e:
            print(f"❌ Error generating report: {e}")
            return False


def main():
    """Main function to run the report generator."""
    
    parser = argparse.ArgumentParser(description='Generate AI-Lamb SAST Security Report')
    parser.add_argument('--input', '-i', default='../data/sast.md',
                       help='Input SAST findings file (default: ../data/sast.md)')
    parser.add_argument('--output', '-o', default='ai-lamb-report.html',
                       help='Output HTML report file (default: ai-lamb-report.html)')
    parser.add_argument('--api-key', '-k', help='OpenAI API key (or set OPENAI_API_KEY env var)')
    
    args = parser.parse_args()
    
    # Ensure input file exists
    if not os.path.exists(args.input):
        print(f"❌ Error: Input file '{args.input}' not found.")
        print("Please ensure the SAST findings file exists in the data directory.")
        sys.exit(1)
    
    try:
        # Initialize the report generator
        generator = SASTReportGenerator(openai_api_key=args.api_key)
        
        # Generate the report
        success = generator.generate_report(args.input, args.output)
        
        if success:
            print("\n🎉 Report generation completed successfully!")
            print(f"📊 View the report: {args.output}")
        else:
            print("\n❌ Report generation failed.")
            sys.exit(1)
            
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
