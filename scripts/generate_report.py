from langchain.agents import create_react_agent
from langchain_aws import ChatBedrock
from langchain_core.prompts import PromptTemplate
from langchain.agents import AgentExecutor
from pydantic import BaseModel, Field
from langchain.tools import BaseTool
from langchain_community.vectorstores import FAISS
from langchain_aws import BedrockEmbeddings
from typing import Optional, Type
from langchain.callbacks.manager import CallbackManagerForToolRun
from dotenv import load_dotenv
import os
import json
from datetime import datetime

# Load environment variables
load_dotenv()


class SearchInput(BaseModel):
    query: str = Field(description="should be a search query")


class CustomSearchTool(BaseTool):
    name: str = "custom_search"
    description: str = "Useful for when you need to answer questions about code"
    args_schema: Type[SearchInput] = SearchInput

    def _run(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        """Use the tool."""
        faiss_db_path = "../vector_db/imprenta.faiss"
        db = FAISS.load_local(
            faiss_db_path,
            BedrockEmbeddings(model_id="amazon.titan-embed-text-v2:0"),
            allow_dangerous_deserialization=True,
        )
        return db.similarity_search(query)

    async def _arun(
        self, query: str, run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> str:
        raise NotImplementedError("custom_search does not support async")


# Define tools and LLM
tools = [CustomSearchTool()]
llm = ChatBedrock(
    model_id="us.anthropic.claude-3-5-haiku-20241022-v1:0",
    #model_id="us.deepseek.r1-v1:0",
    #model_id="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    model_kwargs={"temperature": 0.6},
)

# Define instructions and prompt
instructions = """
You are an agent designed to analyze Python code for potential XML Parser Misconfigurations vulnerabilities.

### Analysis Process
1. Initial Review:
 - XML Parser Misconfigurations: Analyzes codebase for misconfigured XML parsers that could lead to XXE (External XML Entity) injection vulnerabilities
 
2. Reflection Questions:
   Consider these questions carefully:
   - Did I confirm that every XML parser instance explicitly disables DTD and external entity resolution, or could any parser be using insecure defaults?
   - Have I considered that XML parsing might occur indirectly in third-party libraries, frameworks, or utility modules?
   - Did I verify whether all XML inputs are from trusted sources, or could an attacker control them (e.g., user input, file uploads, external API responses)?
   - Could any XML transformations, XSLT, or schema imports be loading resources from untrusted or external locations, posing additional risks?
   - Is my explanation clear on how an attacker could exploit each misconfiguration in this specific code context?
   - Did I provide precise, language- and library-specific mitigation steps rather than generic advice?
   - Have I ensured I reviewed all XML parsing points flagged during the initial review, avoiding missed spots?
   - Are there any ambiguous or borderline cases where the security impact is unclear and require further investigation?

3. Challenge Initial Assessment:
    -Have I identified all places in the codebase where XML parsing or processing occurs, including indirect or third-party library usage?
    - Did I correctly determine which XML inputs might come from untrusted or attacker-controlled sources?
    - Are there any legacy or less obvious XML handling code paths that might have been overlooked in this initial scan?
    - Have I noted the exact libraries, frameworks, and versions used for XML parsing to help focus the detailed review?
    - Could some XML parsing be happening in dynamically loaded modules or conditional code branches I haven’t accounted for?
    - Are there any XML-related features or functionality (e.g., transformations, schema validations) that deserve special attention in the deeper review?

### **TOOLS**
You have access to a vector database to search for code-related information. Use it to understand how custom functions handle authorization.

### **Output Format**
Your final response must be in JSON format, containing the following fields:
- `is_insecure`: (bool) Whether the code is considered insecure.
- `reason`: (str) The reason the code is considered insecure or secure.

TOOLS:
------

You have access to the following tools:

{tools}

You must use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, 
or if you do not need to use a tool, 
you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here]
```

Your Final Answer should be in JSON format 
with the following fields:

- is_insecure: (bool) whether the code is considered insecure
- reason: (str) the reason the code is considered insecure

Begin!

New input: {input}
{agent_scratchpad}
"""
prompt = PromptTemplate.from_template(instructions)

# Create agent and executor
agent = create_react_agent(llm, tools, prompt)
agent_executor = AgentExecutor(
    agent=agent, tools=tools, verbose=True, handle_parsing_errors=True
)


def analyze_code(input_code: str) -> dict:
    """
    Analyze the given code using the agent_executor and return the result.
    """
    # Capture all output during execution
    import io
    import sys
    from contextlib import redirect_stdout
    
    # Capture stdout to get all printed output
    captured_output = io.StringIO()
    with redirect_stdout(captured_output):
        response = agent_executor.invoke({"input": input_code})
    
    # Get the captured output
    verbose_output = captured_output.getvalue()
    
    # Add verbose output to the response
    response['verbose_output'] = verbose_output
    
    return response


def generate_html_report(result, input_code):
    """Generate a clean HTML report from the analysis result."""
    
    # Extract data from result
    verbose_output = ""
    if isinstance(result, dict):
        output = result.get('output', str(result))
        verbose_output = result.get('verbose_output', "")
        
        # Try to extract JSON from the output string
        if isinstance(output, str):
            # Look for JSON in the output (common pattern in agent responses)
            import re
            json_match = re.search(r'\{.*\}', output, re.DOTALL)
            if json_match:
                try:
                    parsed = json.loads(json_match.group())
                    is_insecure = parsed.get('is_insecure', 'Unknown')
                    reason = parsed.get('reason', 'No reason provided')
                except:
                    is_insecure = 'Unknown'
                    reason = output
            else:
                # If no JSON found, try to extract boolean and reason from text
                if 'true' in output.lower() and 'insecure' in output.lower():
                    is_insecure = True
                elif 'false' in output.lower() and 'secure' in output.lower():
                    is_insecure = False
                else:
                    is_insecure = 'Unknown'
                reason = output
        else:
            is_insecure = 'Unknown'
            reason = str(output)
    else:
        is_insecure = 'Unknown'
        reason = str(result)
    
    # Determine status and styling
    if is_insecure == True:
        status = "🔴 VULNERABLE"
        status_class = "vulnerable"
    elif is_insecure == False:
        status = "🟢 SECURE"
        status_class = "secure"
    else:
        status = "🟡 UNKNOWN"
        status_class = "unknown"
    
    html_template = f"""
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AI-Lamb Security Analysis Report</title>
    <style>
        * {{
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }}
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.6;
            color: #333;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
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
        .content {{
            padding: 40px;
        }}
        .section {{
            margin: 30px 0;
            padding: 25px;
            background: #f8f9fa;
            border-radius: 10px;
            border-left: 5px solid #e74c3c;
        }}
        .section h2 {{
            color: #e74c3c;
            font-size: 1.5em;
            margin-bottom: 15px;
        }}
        .status-badge {{
            display: inline-block;
            padding: 10px 20px;
            border-radius: 25px;
            font-weight: bold;
            font-size: 1.1em;
            margin: 10px 0;
        }}
        .vulnerable {{
            background: #ffe6e6;
            color: #d63031;
            border: 2px solid #d63031;
        }}
        .secure {{
            background: #e8f5e8;
            color: #27ae60;
            border: 2px solid #27ae60;
        }}
        .unknown {{
            background: #fff3cd;
            color: #f39c12;
            border: 2px solid #f39c12;
        }}
        .code-block {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 20px;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
            overflow-x: auto;
            margin: 15px 0;
        }}
        .timestamp {{
            text-align: center;
            color: #6c757d;
            font-style: italic;
            margin-top: 30px;
            padding: 20px;
            border-top: 1px solid #dee2e6;
        }}
        .reason {{
            background: white;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #e74c3c;
            margin: 15px 0;
        }}
        .verbose-output {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 8px;
            border-left: 4px solid #17a2b8;
            margin: 15px 0;
        }}
        .verbose-output pre {{
            background: #2d3748;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
            font-family: 'Courier New', monospace;
            font-size: 0.9em;
            line-height: 1.4;
            max-height: 400px;
            overflow-y: auto;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🐑 AI-Lamb Security Analysis</h1>
            <div class="subtitle">Static Application Security Testing Report</div>
        </div>
        
        <div class="content">
            <div class="section">
                <h2>📋 Analysis Summary</h2>
                <div class="status-badge {status_class}">{status}</div>
                <p>This report contains the security analysis results for the provided Python code.</p>
            </div>
            
            <div class="section">
                <h2>🔍 Analyzed Code</h2>
                <div class="code-block">{input_code.strip()}</div>
            </div>
            
            <div class="section">
                <h2>📊 Security Assessment</h2>
                <div class="reason">
                    <strong>Analysis Result:</strong><br>
                    {reason}
                </div>
            </div>
            
            <div class="section">
                <h2>🔍 Detailed Analysis Process</h2>
                <div class="verbose-output">
                    <strong>Agent Execution Log:</strong><br>
                    <pre>{verbose_output}</pre>
                </div>
            </div>
            
            <div class="timestamp">
                Report generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}
            </div>
        </div>
    </div>
</body>
</html>
"""
    
    return html_template


if __name__ == "__main__":
    # Example input
    input_code = """
    @login_required
    @user_passes_test(can_create_project)
    def update_user_active(request):
        user_id = request.GET.get('user_id')
        User.objects.filter(id=user_id).update(is_active=False)
    """
    result = analyze_code(input_code)
    
    # Generate clean HTML report
    html_content = generate_html_report(result, input_code)
    
    # Write result to HTML file
    output_file = "../ai-lamb-report.html"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(html_content)
    
    print(f"Report generated successfully: {output_file}")
