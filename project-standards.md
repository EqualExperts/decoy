# Project Standards

Important: Always use British English spellings in both generated code and documentation.
It is not necessary to write tests to catch this however.

## Project Development Methodology

### Design-First Approach

Always start new projects with this sequence:

1. **Solution Design** - Create high-level architecture and component interactions.
   Store this in a file called sdd.md in the docs directory.
2. **Data Model Design** - Define all data structures using dataclasses.
   All classes and functions should receive and return typed objects, even if it's
   just a typealias, unless the method is a helper or there's a good reason to use
   a primitive.
3. **Implementation Plan** - Break down development into logical phases.
   This might be around features or cleavage planes. Consider incremental value but,
   where reasonable, plan ahead to future implementation steps. Document this in a
   file called implementationplan.md in the docs directory.
4. **Code Implementation**
   - Build out the actual functionality, always with reference to the data model.
   - Stub out implementation classes with type hints before implementing methods
   - Verify type consistency across the codebase before writing method implementations

### Documentation Strategy

- Document data models by creating the actual code rather than separate documentation
- When implementing new end-user functionality or changing the environment setup
  modify the README.md file in the root accordingly.
- Document the internal architecture as it's developed in the docs directory
- All markdown documents must conform to markdownlint rules (VS Code plugin standard)

## Code Style Guidelines

Important: All files should end with a newline.

### Ruff Style Rules

All code must conform to these ruff settings:

#### Formatting

- Line length: 88 characters maximum
- Indent width: 4 spaces
- Quote style: double quotes for strings
- Indent style: spaces (not tabs)
- Respect magic trailing commas (lists ending with a comma won't be collapsed)
- Auto-format code examples in docstrings

#### Linting

Select all rules (`ALL`) with the following exceptions ignored:

| Rule    | Description                                        |
| ------- | -------------------------------------------------- |
| COM812  | Missing trailing comma (can cause conflicts)       |
| D203    | Blank line before class docstring                  |
| D213    | Multi-line docstring should start with summary     |
| EM101   | No string literal in exception messages            |
| EM102   | Exception must not use f-string literal            |
| E501    | Line too long (formatter handles this)             |
| PTH123  | Use Path.open() instead of open()                  |
| PGH003  | Specific rule code when ignoring Pylance           |
| S301    | Use of pickle                                      |
| S603    | Subprocess calls                                   |
| T201    | Print statements                                   |
| TRY301  | Raising exception in try block                     |
| TRY003  | Long exception messages                            |
| S608    | SQL injection (handled by parameterised queries)   |

#### Test File Exceptions

Test files (`tests/*.py`) may ignore:

- ANN001, ANN201 - Type annotations
- D - All docstring rules
- PLR2004 - Magic values
- S101 - Assert usage
- S108 - Insecure paths

#### Script File Exceptions

Script files (`scripts/*.py`) may ignore:

- D100 - Module docstrings
- INP001 - Implicit namespace package

### General Standards

- Always end files with a newline character
- Use type hints for all function signatures and return types
- Never use None for defaults unless the type is an Optional.
  Prefer a sensible default or enclose the type in an Optional
- Use `#!/usr/bin/env bash` as the hashbang for shell scripts

### Python-Specific Standards

#### Exception Handling

Important: In try/except blocks never catch the base Exception class, always
identify a more specific class that captures all the anticipated failure modes.
If one doesn't exist suggest defining one.

#### File Operations

- Use `Path.read_text()`, `Path.write_text()` instead of `open()`
- Use `from pathlib import Path` for path operations

#### Import Organisation

- All imports should be at the top of the file, no lazy imports
- Standard library imports first
- Third-party imports second
- Local imports last
- Use specific imports rather than wildcard imports
- Never use the optional dependency pattern. Prefer the import to fail at startup.

#### Function Argument Design

Keyword-Only Arguments
Use keyword-only arguments (with * separator) for the following parameter types to improve code clarity:

1. Boolean arguments (always)
pythondef fetch_data(url, *, verify_ssl: bool = True, follow_redirects: bool = False):
    ...
1. Multiple arguments of the same type
python# ✅ Good - prevents argument order confusion
def create_rectangle(*, width: int, height: int):
    ...

create_rectangle(width=10, height=20)

##### ❌ Bad - easy to mix up

def create_rectangle(width: int, height: int):
    ...

create_rectangle(10, 20)  # Which is which?

1. Optional configuration parameters
pythondef send_email(recipient, subject, body, *, cc: list = None, bcc: list = None, priority: str = "normal"):
    ...
1. Arguments that aren't self-evident
python# ✅ Good
def retry_operation(func, *, max_attempts: int = 3, delay_seconds: float = 1.0):
    ...

##### ❌ Bad

def retry_operation(func, max_attempts: int, delay_seconds: float):
    ...

retry_operation(my_func, 3, 1.0)  # What do these numbers mean?
When positional arguments are OK:

Required arguments with obvious meaning and natural order (e.g., calculate_distance(point1, point2))
Single required argument after the main/primary argument
Well-established conventions (e.g., range(start, stop, step))

### Data Model Standards

Important: Never use a str type for a field and give it a default value of None.
In this case prefer to type it as Optional[str].

#### Dataclass Structure

Use standard library dataclasses (not pydantic):

```python
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional
import uuid


@dataclass
class ExampleModel:
    """Example data model with standard dataclass."""

    # Required fields first
    session_id: str
    created_at: datetime

    # Optional fields with defaults
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    status: ProcessingStatus = ProcessingStatus.PENDING
    completed_at: Optional[datetime] = None
```

### Markdown standards

- lists should be surrounded by blank lines

### CLI Application Standards

#### Preferred Libraries

- **pathlib** - Prefer `pathlib` over `os` module for file operations
- **typer** - Command-line argument parsing and CLI structure
- **rich** - Progress indicators, formatted output, and CLI quality-of-life improvements. Assume always available, don't use fallback code.
- **loguru** - Logging with sensible defaults

#### Logging Configuration

- All regular console output should use INFO log level
- Debug information should use DEBUG log level
- CLI applications should include a `--debug` flag to enable DEBUG logging

#### CLI Architecture

Keep the CLI thin. The main.py file should:

- Handle argument parsing with typer
- Configure logging based on debug flag
- Delegate all business logic to core modules
Note that typer installs Rich's traceback handler by default. Disable this using

```python
app = typer.Typer()
app.pretty_exceptions_enable=False
```

This separation allows adding alternative interfaces (e.g., FastAPI) later without
refactoring core functionality.

#### Example CLI Structure

```python
#!/usr/bin/env python3
"""Minimal CLI entry point."""

from typing import Annotated

import typer
from loguru import logger
from rich.console import Console

from myproject.core import run_process

app = typer.Typer(help="My application description.")
console = Console()


def configure_logging(*, debug: bool) -> None:
    """Configure loguru logging level."""
    import sys

    logger.remove()
    level = "DEBUG" if debug else "INFO"
    logger.add(sys.stderr, level=level)


@app.command()
def main(
    input_path: Annotated[str, typer.Argument(help="Path to input file")],
    *,
    debug: Annotated[bool, typer.Option("--debug", help="Enable debug logging")] = False,
) -> None:
    """Run the main process."""
    configure_logging(debug=debug)
    logger.info("Starting process")

    result = run_process(input_path)

    logger.info(f"Process complete: {result}")


if __name__ == "__main__":
    app()
```

### LLM Tooling Standards

#### LLM Libraries

When building LLM-powered applications, use these standardised libraries:

##### Text Chunking

- **chonkie** - Modern, lightweight text chunking library designed for RAG applications
  - Replaces LangChain text splitters to avoid Pydantic v1 compatibility issues
  - 33x faster performance for token chunking, 2.5x faster for semantic chunking
  - 505KB wheel size vs 1-12MB for alternatives
  - Multiple chunking strategies: Token, Sentence, Recursive, Semantic
  - Python 3.14 compatible with minimal dependencies

##### LLM Provider Integration

- **litellm** - Unified interface for LLM providers (OpenAI, Anthropic, etc.)
  - Consistent API across different LLM providers
  - Built-in retry logic, rate limiting, and error handling
  - Standardised token usage tracking and cost calculation
  - Environment variable configuration for API keys

#### Text Chunking Implementation

Use Chonkie for all text chunking needs:

```python
from chonkie import TokenChunker
import tiktoken

# Token-based chunking (recommended for most use cases)
tokenizer = tiktoken.get_encoding("cl100k_base")  # For OpenAI models
chunker = TokenChunker(tokenizer=tokenizer, chunk_size=512, chunk_overlap=50)
chunks = chunker.chunk("Your long text here...")

# Semantic chunking for content-aware splitting
from chonkie import SemanticChunker
semantic_chunker = SemanticChunker(
    embedding_model="sentence-transformers/all-MiniLM-L6-v2",
    chunk_size=512
)
chunks = semantic_chunker.chunk("Your long text here...")
```

#### LLM Provider Integration

Use LiteLLM for all LLM interactions to maintain provider flexibility:

```python
from litellm import completion

# Consistent interface across providers
response = completion(
    model="claude-sonnet-4-5",  # or "gpt-4o", "gemini-pro", etc.
    messages=[{"role": "user", "content": "Your prompt here"}],
    temperature=0.1,
    max_tokens=1000
)
```

#### Configuration Management

- Use environment variables for API keys (OPENAI_API_KEY, ANTHROPIC_API_KEY)
- Configure model selection through application settings
- Implement fallback models for reliability
- Track token usage and costs through LiteLLM's built-in metrics

### FastAPI Standards

When adding a FastAPI interface (only when explicitly requested):

- Prefer HTML templates with Jinja
- The production environment applies a base URL so all links must use the `url_for`
  method from Jinja to locate the relevant directory
- CSS and JavaScript should live in a static files directory mounted when the app
  instance is created

### Project Structure Standards

#### Package Organisation

- All project source code should live in a `src/<packagename>/` directory structure
- This follows the "src layout" convention for Python packages
- Example: `src/myproject/` for a package named "myproject"
- Benefits: Cleaner imports, better testing isolation, prevents accidental imports

#### File Naming

- Use snake_case for Python files and directories
- Use descriptive names that indicate purpose
- Group related functionality in appropriately named modules

### Error Handling

- Use specific exception types rather than generic `Exception`
- Include meaningful error messages with context
- Log errors with appropriate detail level using structured logging (loguru)

### Environment Management

Use `uv` exclusively for dependency management and virtual environments.

#### Container Management

Use **Colima** instead of Docker Desktop for container management on macOS:

- Install Colima: `brew install colima`
- Start Colima: `colima start`
- Use standard Docker commands with Colima backend
- Better performance and resource usage than Docker Desktop
- Consistent with lightweight development environment principles

#### Project Setup

```bash
# Use pyenv for Python version management
pyenv install 3.13.3
pyenv local 3.13.3

# Use uv for dependency management
uv sync

# Run commands
uv run python src/main.py
uv run bash scripts/process.sh
```

#### Build System

Use uv_build as the build backend with named dependency groups:

```toml
[build-system]
requires = ["uv_build"]
build-backend = "uv_build"

[project]
name = "myproject"
version = "0.1.0"
requires-python = ">=3.13"
dependencies = [
    "typer",
    "rich",
    "loguru>=0.7.3",
]

[dependency-groups]
dev = [
    "ruff>=0.12.7",
    "pytest>=7.4.0",
    "pytest-asyncio>=0.21.0",
    "pytest-mock>=3.11.0",
]
```

### Code Quality and CI/CD Integration

#### Linting and Formatting

Use ruff for both formatting and linting:

- Configure all settings in `pyproject.toml`
- Ensure IDE settings match CI/CD tool configurations exactly
- Use format-on-save for immediate feedback

#### Git Commit Standards

- Write clear, descriptive commit messages
- Use imperative mood ("Add feature" not "Added feature")
- Include context about what changed and why
- **Do not include AI assistant credits or signatures in commit messages**
- Keep commit messages focused on the technical changes

### Testing Standards

#### Prototype Testing Approach

- Only test actual application logic, not external libraries
- Trust that PostgreSQL, OpenAI API, etc. work correctly
- Focus on edge cases, validation logic, and error handling in our code
- Use descriptive test method names that explain what is being tested
- Follow the Arrange-Act-Assert pattern
- Mock external dependencies appropriately
- Prefer fewer, focused tests over comprehensive coverage

### Repository Bundling with Repomix

#### Configuration Management

- Use `repomix.config.json` to manage included files and directories
- Run repomix with simple command: `npx repomix` (config file is automatically detected)
- The config file itself must be included in the `include` array

#### Updating Include Patterns

**Important:** When adding new source code directories, configuration files, or
documentation:

1. Add the new paths to the `include` array in `repomix.config.json`
2. Consider context limits - prioritise essential code and config files
3. Update ignore patterns if new generated/temporary directories are created

**Standard include patterns:**

- `src` - Main source code
- `scripts` - Automation scripts
- `pyproject.toml` - Project configuration
- `.vscode` - Shared IDE settings
- `README.md` - Project documentation
- `CLAUDE.md` - This standards file
- `.python-version` - Python version specification
- `.gitignore` - Git ignore rules
- `repomix.config.json` - Repomix configuration

**Common additions to consider:**

- `tests` - Test directories
- `docs` - Additional documentation
- `config` - Configuration directories
- `templates` - Template files
- Docker files (`Dockerfile`, `docker-compose.yml`)
- CI/CD files (`.github`, `.gitlab-ci.yml`)

### Documentation

- Use docstrings for all public methods and classes
- Include type information in docstrings when it adds clarity
- Document complex business logic with inline comments
- Keep README.md updated with setup and usage instructions
