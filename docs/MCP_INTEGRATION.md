# 🔌 AWDX MCP Server Integration

AWDX now includes a **Model Context Protocol (MCP) server** that exposes AWS DevSecOps capabilities to AI assistants through a standardized interface.

## 🌟 What is MCP?

**Model Context Protocol (MCP)** is a standardized protocol that allows AI assistants to interact with external tools and data sources. It enables AI models to:

- Access real-time information from external systems
- Perform actions through standardized tool calls
- Integrate with various services and APIs
- Maintain context across multiple interactions

## 🎯 How MCP Relates to AWDX

Your AWDX tool is **perfectly positioned** for MCP integration because:

### ✅ **Existing AI Foundation**
- You already have Google Gemini integration
- Natural language processing capabilities
- Intent recognition and command mapping
- Conversation context management

### ✅ **Rich AWS DevSecOps Modules**
- **Profilyze**: AWS profile management
- **Costlyzer**: Cost analysis and optimization
- **IAMply**: IAM security auditing
- **S3ntry**: S3 bucket security
- **Secrex**: Secret management
- **Secutide**: Security assessment

### ✅ **Real-time Data Access**
- Live AWS API calls
- Current security posture
- Real-time cost data
- Active resource monitoring

## 🚀 Getting Started

### 1. Start the MCP Server

```bash
# Basic server start
awdx mcp start

# Custom configuration
awdx mcp start --host 0.0.0.0 --port 3001 --config ~/.awdx/config.yaml

# Start without AI features (faster)
awdx mcp start --no-ai
```

### 2. Check Server Status

```bash
# View server status
awdx mcp status

# List available tools
awdx mcp tools

# Test connection
awdx mcp test
```

### 3. Connect AI Assistants

The MCP server runs on `localhost:3000` by default and can be connected to:

- **Claude Desktop** (Anthropic)
- **ChatGPT** (with MCP plugins)
- **Custom AI assistants**
- **Development tools**

## 🛠️ Available MCP Tools

### Profile Management
```json
{
  "name": "awdx_profile_list",
  "description": "List all AWS profiles configured in AWDX"
}

{
  "name": "awdx_profile_switch", 
  "description": "Switch to a different AWS profile"
}

{
  "name": "awdx_profile_add",
  "description": "Add a new AWS profile"
}
```

### Cost Analysis
```json
{
  "name": "awdx_cost_summary",
  "description": "Get AWS cost summary and analysis"
}

{
  "name": "awdx_cost_trends",
  "description": "Analyze cost trends over time"
}

{
  "name": "awdx_cost_optimize",
  "description": "Get cost optimization recommendations"
}
```

### IAM Security
```json
{
  "name": "awdx_iam_audit",
  "description": "Perform comprehensive IAM security audit"
}

{
  "name": "awdx_iam_users",
  "description": "List and analyze IAM users"
}

{
  "name": "awdx_iam_roles",
  "description": "List and analyze IAM roles"
}
```

### S3 Security
```json
{
  "name": "awdx_s3_audit",
  "description": "Perform S3 bucket security audit"
}

{
  "name": "awdx_s3_scan",
  "description": "Scan S3 buckets for security issues"
}
```

### Secret Management
```json
{
  "name": "awdx_secret_discover",
  "description": "Discover secrets in AWS resources"
}

{
  "name": "awdx_secret_rotate",
  "description": "Rotate secrets and credentials"
}
```

### Security Assessment
```json
{
  "name": "awdx_security_audit",
  "description": "Perform comprehensive security audit"
}

{
  "name": "awdx_security_scan",
  "description": "Scan for security vulnerabilities"
}
```

### AI Features
```json
{
  "name": "awdx_ai_ask",
  "description": "Ask questions in natural language about AWS resources"
}

{
  "name": "awdx_ai_explain",
  "description": "Get AI-powered explanations of AWS configurations"
}
```

## 🔧 Integration Examples

### 1. Claude Desktop Integration

1. **Install Claude Desktop** from Anthropic
2. **Add MCP server configuration**:
   ```json
   {
     "mcpServers": {
       "awdx": {
         "command": "awdx",
         "args": ["mcp", "start"],
         "env": {
           "AWS_PROFILE": "default"
         }
       }
     }
   }
   ```
3. **Ask Claude**:
   ```
   "Show me all my AWS profiles and their current costs"
   "Audit my IAM security and identify any issues"
   "Find S3 buckets with public access"
   ```

### 2. ChatGPT with MCP Plugin

1. **Install MCP plugin** for ChatGPT
2. **Configure AWDX server**:
   ```bash
   awdx mcp start --host 0.0.0.0 --port 3000
   ```
3. **Connect plugin** to `http://localhost:3000`
4. **Use ChatGPT** to interact with AWS:
   ```
   "What are my biggest cost drivers this month?"
   "Check which IAM users don't have MFA enabled"
   "Scan my S3 buckets for security issues"
   ```

### 3. Custom AI Assistant

```python
import asyncio
import json

async def call_awdx_tool(tool_name: str, arguments: dict):
    """Call AWDX tool through MCP."""
    # Connect to MCP server
    reader, writer = await asyncio.open_connection("localhost", 3000)
    
    # Prepare tool call
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": arguments
        }
    }
    
    # Send request
    request_data = json.dumps(request).encode("utf-8")
    request_length = len(request_data).to_bytes(4, byteorder="big")
    writer.write(request_length + request_data)
    await writer.drain()
    
    # Read response
    length_bytes = await reader.read(4)
    message_length = int.from_bytes(length_bytes, byteorder="big")
    response_data = await reader.read(message_length)
    response = json.loads(response_data.decode("utf-8"))
    
    writer.close()
    await writer.wait_closed()
    
    return response

# Example usage
result = await call_awdx_tool("awdx_cost_summary", {"days": 30})
print(result)
```

## 🔒 Security Considerations

### Authentication
- MCP server uses AWS credentials from AWDX configuration
- Supports AWS profiles and role-based access
- Credentials are not exposed to AI assistants

### Network Security
- Server runs on localhost by default
- Can be configured for network access with proper security
- Supports TLS encryption for production use

### Data Privacy
- AWS data stays within your control
- No data is sent to external AI services (except Gemini API)
- All tool calls are logged locally

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    AI Assistant (Claude/ChatGPT)               │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    MCP Protocol Layer                          │
│  • JSON-RPC communication                                      │
│  • Tool discovery and calling                                  │
│  • Error handling and responses                                │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWDX MCP Server                             │
│  • Tool registry and routing                                   │
│  • AWS credential management                                   │
│  • Response formatting                                         │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWDX Modules                                │
│  • Profilyze (Profile Management)                              │
│  • Costlyzer (Cost Analysis)                                   │
│  • IAMply (IAM Security)                                       │
│  • S3ntry (S3 Security)                                        │
│  • Secrex (Secret Management)                                  │
│  • Secutide (Security Assessment)                              │
└─────────────────────────────────────────────────────────────────┘
                                │
                                ▼
┌─────────────────────────────────────────────────────────────────┐
│                    AWS APIs                                    │
│  • AWS SDK (boto3)                                             │
│  • Real-time data access                                       │
│  • Service-specific APIs                                       │
└─────────────────────────────────────────────────────────────────┘
```

## 🎯 Use Cases

### 1. **DevSecOps Automation**
```
AI Assistant: "Set up automated security scanning for new EC2 instances"
AWDX MCP: Calls security tools to configure monitoring and alerts
```

### 2. **Cost Optimization**
```
AI Assistant: "Find unused resources costing more than $100/month"
AWDX MCP: Analyzes cost data and identifies optimization opportunities
```

### 3. **Compliance Auditing**
```
AI Assistant: "Generate a compliance report for SOC 2 requirements"
AWDX MCP: Runs security audits and generates compliance documentation
```

### 4. **Incident Response**
```
AI Assistant: "Investigate this security alert about suspicious IAM activity"
AWDX MCP: Queries IAM logs, analyzes user behavior, and provides insights
```

## 🚀 Benefits

### For Developers
- **Natural Language Interface**: Ask questions in plain English
- **Real-time Data**: Access current AWS state instantly
- **Automated Workflows**: Build intelligent DevSecOps pipelines
- **Context Awareness**: AI understands your AWS environment

### For Security Teams
- **Proactive Monitoring**: AI can monitor and alert on security issues
- **Automated Auditing**: Regular security assessments without manual work
- **Compliance Automation**: Generate reports and evidence automatically
- **Threat Intelligence**: AI can correlate events and identify patterns

### For Operations Teams
- **Cost Management**: AI can monitor and optimize spending
- **Resource Management**: Automated cleanup and optimization
- **Performance Monitoring**: AI can identify performance issues
- **Capacity Planning**: Predictive analysis for resource needs

## 🔧 Configuration

### Server Configuration
```yaml
# ~/.awdx/mcp_config.yaml
server:
  host: "localhost"
  port: 3000
  max_connections: 10
  timeout: 30

security:
  require_authentication: true
  allowed_hosts: ["localhost", "127.0.0.1"]
  tls_enabled: false

tools:
  enable_all: true
  ai_enabled: true
  rate_limiting: true
  max_requests_per_minute: 60

logging:
  level: "INFO"
  file: "/var/log/awdx-mcp.log"
  format: "json"
```

### Environment Variables
```bash
# AWS Configuration
export AWS_PROFILE="default"
export AWS_REGION="us-east-1"

# MCP Server Configuration
export AWDX_MCP_HOST="0.0.0.0"
export AWDX_MCP_PORT="3000"
export AWDX_MCP_CONFIG="/path/to/config.yaml"

# AI Configuration
export GEMINI_API_KEY="your_api_key"
export AWDX_AI_ENABLED="true"
```

## 🐛 Troubleshooting

### Common Issues

1. **Server won't start**
   ```bash
   # Check if port is in use
   lsof -i :3000
   
   # Check AWDX configuration
   awdx config validate
   ```

2. **AI features not working**
   ```bash
   # Verify Gemini API key
   awdx ai configure
   
   # Test AI connection
   awdx ai test
   ```

3. **Tools not available**
   ```bash
   # Check tool registration
   awdx mcp tools
   
   # Verify AWS credentials
   aws sts get-caller-identity
   ```

4. **Connection issues**
   ```bash
   # Test server connection
   awdx mcp test
   
   # Check firewall settings
   sudo ufw status
   ```

### Debug Mode
```bash
# Enable verbose logging
awdx mcp start --verbose

# Check server logs
tail -f /var/log/awdx-mcp.log
```

## 🔮 Future Enhancements

### Planned Features
- **Multi-account Support**: Manage multiple AWS accounts
- **Custom Tool Development**: Create custom MCP tools
- **WebSocket Support**: Real-time updates and notifications
- **Plugin System**: Extend functionality with plugins
- **Advanced AI**: Multi-modal processing and workflow automation

### Integration Roadmap
- **GitHub Actions**: CI/CD pipeline integration
- **Slack/Discord**: Chat platform integration
- **Jira/ServiceNow**: Ticketing system integration
- **Splunk/ELK**: Log analysis integration
- **Grafana**: Monitoring dashboard integration

## 📚 Additional Resources

- [Model Context Protocol Specification](https://modelcontextprotocol.io/)
- [AWDX Documentation](https://github.com/pxkundu/awdx)
- [AWS SDK Documentation](https://boto3.amazonaws.com/)
- [MCP Community](https://github.com/modelcontextprotocol)

---

**Ready to transform your AWS DevSecOps workflow with AI?** Start the AWDX MCP server and connect your favorite AI assistant today! 