# Installing AI VC skills

The skills are Markdown instructions; the numbers come from the `equity_calculator` MCP server. Pick your client.

## Claude Code

```
/plugin marketplace add BwL1289/ai-vc-skills
/plugin install ai-vc-skills@ai-vc-skills
```

On Claude Code 2.1.275 or later, one line does both: `/plugin install ai-vc-skills --marketplace BwL1289/ai-vc-skills`.

The plugin adds every skill in `skills/` and the MCP server, which it starts with
[`uvx`](https://docs.astral.sh/uv/getting-started/installation/); install uv first. Check it with `/mcp`: the server
`equity_calculator` should be connected. Update later with `/plugin marketplace update ai-vc-skills`.

## Skills that load in pairs

Every install below that uses the skills loads their folders by hand, so load every folder under `skills/`. Two skills
read a file in another skill's folder, so the folders must sit side by side:

- `vc-diligence-questions` reads `vc-partner-meeting`'s question bank, so load both folders.
- `vc-prospective-investor-update` reads `vc-current-investor-update`'s metric rules file, so load both folders.

When the other folder is missing, the skill says so in one line and names the folder to add.

## Claude Desktop

1. Install the package (Python 3.12 or later):

   ```
   pip install "equity_calculator[mcp] @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
   ```

2. Add the server to `claude_desktop_config.json` (Settings, Developer, Edit Config) and restart Claude Desktop:

   ```json
   {
     "mcpServers": {
       "equity_calculator": { "command": "equity_calculator_mcp" }
     }
   }
   ```

   If Claude Desktop cannot find the command, give its full path (`which equity_calculator_mcp`).

3. For the skills themselves, download the repository (`git clone https://github.com/BwL1289/ai-vc-skills`), zip
   every folder under `skills/` (one zip per folder) and upload each in Claude's skills settings, both folders of each
   pair above included.

## Cursor, Windsurf and other MCP clients

Install the package as above, then add the same `mcpServers` entry to the client's MCP settings (Cursor:
`~/.cursor/mcp.json`). Clients that read Agent Skills can load every folder under `skills/` from a copy of each folder
in their skills directory, side by side, so each pair above works.

## Claude Code without the plugin

```
pip install "equity_calculator[mcp] @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
claude mcp add equity_calculator -- equity_calculator_mcp
git clone https://github.com/BwL1289/ai-vc-skills
cp -r ai-vc-skills/skills/* ~/.claude/skills/
```

## The command line only

```
pip install "equity_calculator @ git+https://github.com/BwL1289/ai-vc-skills#subdirectory=equity_calculator"
equity_calculator investor --equity-percent 7 --outcome-multiplier 1.10
```

The command and the library need only Pydantic and openpyxl. Add `--xlsx deal.xlsx` to any scenario for the workbook.

## From a clone

```
git clone https://github.com/BwL1289/ai-vc-skills
cd ai-vc-skills
python3.12 -m venv .venv
. .venv/bin/activate
pip install -e "./equity_calculator[mcp,dev]"
```

To try the plugin from the clone in Claude Code: `/plugin marketplace add ./`, then
`/plugin install ai-vc-skills@ai-vc-skills`.
