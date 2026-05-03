# Contributing to AAP Migration Planner

Thank you for your interest in contributing to AAP Migration Planner! This document provides guidelines and instructions for contributing.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [Making Changes](#making-changes)
- [Submitting Changes](#submitting-changes)
- [Code Standards](#code-standards)

## Code of Conduct

This project adheres to the [Code of Conduct](CODE_OF_CONDUCT.md). By participating, you are expected to uphold this code.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- Git
- AAP instance for testing (optional)

### Ways to Contribute

- **Report bugs**: Open an issue with details about the problem
- **Suggest features**: Open an issue describing the enhancement
- **Submit code**: Fork the repo, make changes, submit pull request
- **Improve documentation**: Help make the docs clearer and more comprehensive
- **Share feedback**: Tell us how you're using the tool and what could be better

## Development Setup

```bash
# Clone your fork
git clone https://github.com/YOUR_USERNAME/aap-migration-planner.git
cd aap-migration-planner

# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install dependencies (editable mode)
pip install -e ".[dev]"

# Install pre-commit hooks (optional but recommended)
pre-commit install
```

## Making Changes

### Branching Strategy

- `main` - Stable, production-ready code
- Feature branches - `feature/your-feature-name`
- Bug fixes - `fix/issue-description`

### Development Workflow

1. Create a new branch from `main`:

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes

3. Run tests:

   ```bash
   pytest
   ```

4. Run linting:

   ```bash
   ruff check src/
   ruff format src/
   ```

5. Commit your changes:

   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

## Submitting Changes

### Pull Request Process

1. Update documentation if needed
2. Add tests for new functionality
3. Ensure all tests pass
4. Update CHANGELOG.md (if exists)
5. Push to your fork:

   ```bash
   git push origin feature/your-feature-name
   ```

6. Open a Pull Request on GitHub

### Pull Request Guidelines

- **Clear description**: Explain what changes you made and why
- **Link related issues**: Reference any related issues (e.g., "Fixes #123")
- **Keep it focused**: One PR should address one issue or feature
- **Tests required**: All new code should have tests
- **Documentation**: Update docs for user-facing changes

## Code Standards

### Python Style

- Follow PEP 8
- Use type hints for function signatures
- Maximum line length: 100 characters
- Use Ruff for linting and formatting

### Commit Messages

Follow [Conventional Commits](https://www.conventionalcommits.org/):

- `feat:` - New feature
- `fix:` - Bug fix
- `docs:` - Documentation only
- `refactor:` - Code refactoring
- `test:` - Adding or updating tests
- `chore:` - Maintenance tasks

Examples:

```
feat: add risk scoring for organizations
fix: correct dependency graph for workflow templates
docs: update installation instructions
```

### Testing Requirements

- Write tests for all new features
- Maintain test coverage above 80%
- Use pytest for testing
- Test both success and error cases

### Documentation

- Update README.md for user-facing changes
- Add docstrings to all public functions and classes
- Use Google-style docstrings

Example:

```python
def analyze_organization(org_name: str) -> OrgDependencyReport:
    """Analyze dependencies for a single organization.

    Args:
        org_name: Name of the organization to analyze

    Returns:
        OrgDependencyReport containing dependency analysis

    Raises:
        ValueError: If organization not found
    """
```

## Questions?

- Open an issue with the "question" label
- Check existing issues for answers
- Review the [documentation](docs/)

## License

By contributing, you agree that your contributions will be licensed under the GPL-3.0 License.

## Recognition

Contributors will be recognized in:

- GitHub contributors list
- Release notes (for significant contributions)
- CONTRIBUTORS.md file (planned)

Thank you for contributing to AAP Migration Planner! 🎉
