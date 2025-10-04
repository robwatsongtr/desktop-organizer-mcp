# Claude Code Guidelines

## Project Purpose

This is an **MCP learning project** focused on understanding the Model Context Protocol. The codebase is intentionally simplified to highlight MCP concepts rather than complex business logic.

## General Standards

See [CODING_GUIDELINES.md](./CODING_GUIDELINES.md) for implementation and documentation standards that apply to all projects.

## Project-Specific Architecture

- **Separation of concerns**:
  - `server.py`: MCP protocol communication
  - `organizer.py`: Business logic (file operations)

## MCP-Specific Guidelines

- **No stdout pollution**: Never use `print()` in MCP servers - it corrupts the protocol.
  - ✅ Use: `print(..., file=sys.stderr)` for debugging
  - ✅ Use: `logging` configured to stderr

- **Tool descriptions**: Make tool descriptions clear and specific - the LLM uses these to decide when to call tools.

- **Simple return types**: Prefer simple string messages over complex data structures when possible.

- **Keep focus on MCP**: Simplify business logic to highlight MCP protocol patterns. 