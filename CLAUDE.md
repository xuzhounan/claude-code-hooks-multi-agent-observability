# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Multi-Agent Observability System for Claude Code hooks that provides real-time monitoring and visualization of Claude Code agent lifecycle events.

## Common Commands

### Development Environment
```bash
# Start entire system (server + client)
./scripts/start-system.sh

# Start server only (port 4000)
cd apps/server && bun dev

# Start client only (port 5173)
cd apps/client && npm run dev
```

### Testing & Validation
```bash
# System functionality test
./scripts/test-system.sh

# Reset system (stop all processes)
./scripts/reset-system.sh
```

### Hook System
```bash
# Install Python dependencies
cd .claude/hooks && uv pip install -r requirements.txt

# Test event sending
cd .claude/hooks && python send_event.py
```

## Architecture Structure

### Tech Stack
- **Backend**: Bun + TypeScript + SQLite (WAL mode)
- **Frontend**: Vue 3 + TypeScript + Vite + Tailwind CSS
- **Hook System**: Python 3.8+ + Anthropic API

### Core Components

#### Server (`apps/server/`)
- `src/index.ts`: Main server providing HTTP API and WebSocket connections
- `src/db.ts`: SQLite database management for event storage and queries
- `src/types.ts`: Shared TypeScript interface definitions
- `src/theme.ts`: Theme management system

#### Client (`apps/client/`)
- `src/App.vue`: Main application component
- `src/components/`: Vue component library (Timeline, EventCard, FilterPanel, etc.)
- `src/composables/`: Vue composables (WebSocket, filtering, themes, etc.)

#### Hook System (`.claude/hooks/`)
- `send_event.py`: Universal event sender
- `pre_tool_use.py`: Pre-execution validation and blocking logic
- `post_tool_use.py`: Post-execution result recording
- `user_prompt_submit.py`: User prompt submission events
- `settings.json`: Hook configuration file

### Data Flow
```
Claude Agent → Hook Scripts → HTTP POST → Bun Server → SQLite → WebSocket → Vue Client
```

## Hook Event Types

The system monitors these Claude Code lifecycle events:
- **PreToolUse**: Before tool execution (includes security validation)
- **PostToolUse**: After tool execution (records results)
- **Notification**: User interaction events
- **UserPromptSubmit**: User prompt submissions
- **Stop**: Response completion
- **SubagentStop**: Sub-agent completion

## Important Configuration

### Environment Variables
Project root requires `.env` file:
```bash
# For Claude Max users (no API key required):
ENGINEER_NAME=your_name

# Optional for API users:
# ANTHROPIC_API_KEY=your_key_here
```

Client requires `apps/client/.env` file:
```bash
VITE_MAX_EVENTS_TO_DISPLAY=100
```

### Hook Configuration
`.claude/settings.json` configures various lifecycle hooks, each hook executes two scripts:
1. Specific functionality script (validation, recording, etc.)
2. Universal event sending script

## Security Features

Hook system includes security validation:
- Block dangerous commands (`rm -rf`, `sudo`, etc.)
- Prevent access to sensitive files (`.env`, private keys)
- Validate all tool input parameters

## Development Notes

1. **Database**: Uses SQLite WAL mode for concurrent read/write support
2. **Real-time Updates**: WebSocket-based real-time event broadcasting
3. **Session Management**: Events organized by `sessionId`, supports multi-agent concurrent monitoring
4. **Theme System**: Supports custom theme configuration and sharing
5. **Filtering**: Multi-dimensional filtering by app, session, event type, etc.

## Port Allocation

- Server: 4000
- Client: 5173
- Database: SQLite file storage

## Log Location

System logs are stored in the `logs/` directory, containing server and client runtime logs.