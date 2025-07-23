# HOW TO USE AWDX MCP SERVER

This guide provides practical, scenario-driven instructions for using the AWDX Model Context Protocol (MCP) server to connect AI assistants (like Claude Desktop, ChatGPT, or custom tools) to your AWS DevSecOps workflows.

---

## 1. Quick Start: Launching the MCP Server

```bash
# Start the MCP server (default: localhost:3000)
awdx mcp start

# Start on a custom port
awdx mcp start --port 4000

# Start with a custom config file
awdx mcp start --config ~/.awdx/mcp_config.yaml

# Start without AI features (for pure DevSecOps automation)
awdx mcp start --no-ai
```

**Tip:** Use `--verbose` for detailed logs during troubleshooting.

---

## 2. Connecting Your AI Assistant

### Claude Desktop
1. Open Claude Desktop settings.
2. Add a new MCP server connection:
   - Command: `awdx`
   - Args: `["mcp", "start"]`
   - (Optional) Set environment variables for AWS profile/region.
3. Save and connect.
4. Ask Claude questions like:
   - "Show all AWS profiles and their costs."
   - "Audit IAM security."

### ChatGPT (with MCP Plugin)
1. Install the MCP plugin for ChatGPT.
2. Start the AWDX MCP server:
   ```bash
   awdx mcp start --host 0.0.0.0 --port 3000
   ```
3. In ChatGPT, connect the plugin to `http://localhost:3000`.
4. Use prompts like:
   - "What are my highest AWS costs this month?"
   - "Scan S3 buckets for public access."

### Custom AI Assistant (Python Example)
```python
import asyncio, json
async def call_awdx_tool(tool_name, arguments):
    reader, writer = await asyncio.open_connection("localhost", 3000)
    req = {"jsonrpc": "2.0", "id": 1, "method": "tools/call", "params": {"name": tool_name, "arguments": arguments}}
    data = json.dumps(req).encode("utf-8"); writer.write(len(data).to_bytes(4, 'big') + data); await writer.drain()
    length = int.from_bytes(await reader.read(4), 'big')
    resp = json.loads((await reader.read(length)).decode("utf-8"))
    writer.close(); await writer.wait_closed(); return resp
# Example:
# result = await call_awdx_tool("awdx_cost_summary", {"days": 30})
```

---

## 3. Common Use Cases

### A. DevSecOps Automation
- **Goal:** Automate security scans for new AWS resources.
- **How:**
  1. Start MCP server.
  2. In your AI assistant, ask: "Set up automated security scanning for new EC2 instances."
  3. The assistant will call the appropriate AWDX security tools via MCP.

### B. Cost Optimization
- **Goal:** Identify and reduce unnecessary AWS spend.
- **How:**
  1. Ask: "Find unused resources costing more than $100/month."
  2. The assistant uses cost analysis tools to report and suggest optimizations.

### C. Compliance Auditing
- **Goal:** Generate compliance reports (e.g., SOC 2).
- **How:**
  1. Ask: "Generate a compliance report for SOC 2."
  2. The assistant runs security and compliance tools, returning a summary.

### D. Incident Response
- **Goal:** Investigate security alerts.
- **How:**
  1. Ask: "Investigate suspicious IAM activity."
  2. The assistant queries logs and analyzes user behavior.

---

## 4. Troubleshooting & Tips

- **Server won't start?**
  - Check if the port is in use: `lsof -i :3000`
  - Validate config: `awdx config validate`
- **AI features not working?**
  - Ensure your Gemini API key is set: `awdx ai configure`
  - Test AI: `awdx ai test`
- **Tools not available?**
  - List tools: `awdx mcp tools`
  - Check AWS credentials: `aws sts get-caller-identity`
- **Connection issues?**
  - Ensure firewall allows the port.
  - For remote access, use `--host 0.0.0.0` and secure your network.

---

## 5. Advanced Scenarios

- **Multiple AI assistants:** Run several MCP servers on different ports for parallel workflows.
- **Custom tool integration:** Use the Python example above to script your own DevSecOps automations.
- **Secure production deployment:**
  - Enable TLS in your config.
  - Restrict allowed hosts.
  - Use IAM roles for least-privilege access.

---

## 6. Where to Learn More
- [MCP Integration Reference](MCP_INTEGRATION.md) – Protocol details, tool list, and architecture
- [AWDX Documentation](../README.md) – Main project overview
- [AI Features](AI_FEATURES.md) – Natural language and AI capabilities

---

**AWDX MCP lets you connect the power of AI to your AWS DevSecOps workflows. Experiment, automate, and secure your cloud with natural language and real-time intelligence!** 