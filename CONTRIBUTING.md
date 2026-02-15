# Contributing to Video-Summary

Thank you for considering contributing to Video-Summary! This document provides guidelines and instructions for contributing.

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- ffmpeg (for video processing)

### Setting up Development Environment

1. **Clone the repository**
   ```bash
   git clone https://github.com/Askill/Video-Summary.git
   cd Video-Summary
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install -e ".[dev]"  # Install development dependencies
   ```

4. **Install pre-commit hooks**
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Development Workflow

### Code Style

We use the following tools to maintain code quality:

- **Black**: Code formatting (line length: 140)
- **isort**: Import sorting
- **flake8**: Linting
- **mypy**: Type checking (optional but recommended)

Run these tools before committing:

```bash
# Format code
black .
isort .

# Check for issues
flake8 .
mypy Application/ main.py
```

Or simply commit - pre-commit hooks will run automatically!

### Making Changes

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Write clean, readable code
   - Add type hints where applicable
   - Update documentation as needed
   - Add tests for new functionality

3. **Test your changes**
   ```bash
   # Run tests (if available)
   pytest

   # Test the CLI
   python main.py path/to/test/video.mp4 output_test
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: Add your feature description"
   ```

   We follow [Conventional Commits](https://www.conventionalcommits.org/):
   - `feat:` - New feature
   - `fix:` - Bug fix
   - `docs:` - Documentation changes
   - `refactor:` - Code refactoring
   - `test:` - Adding tests
   - `chore:` - Maintenance tasks

5. **Push and create a Pull Request**
   ```bash
   git push origin feature/your-feature-name
   ```

### Pull Request Guidelines

- Keep PRs focused on a single feature or fix
- Write a clear description of what the PR does
- Reference any related issues
- Ensure CI passes (linting, tests, build)
- Update documentation if needed
- Add screenshots for UI changes

## Testing

While we're building out the test suite, please ensure:

1. Your code runs without errors
2. You've tested with sample videos
3. Edge cases are handled (missing files, corrupt videos, etc.)
4. Memory usage is reasonable

## Reporting Issues

When reporting issues, please include:

1. **Environment details**
   - OS and version
   - Python version
   - Dependency versions

2. **Steps to reproduce**
   - Exact commands run
   - Input file characteristics (if applicable)

3. **Expected vs. actual behavior**

4. **Error messages and logs**

5. **Screenshots** (if applicable)

## Architecture Overview

```
Video-Summary/
├── Application/          # Core processing modules
│   ├── Config.py        # Configuration management
│   ├── ContourExctractor.py  # Extract contours from video
│   ├── LayerFactory.py  # Group contours into layers
│   ├── LayerManager.py  # Manage and clean layers
│   ├── Exporter.py      # Export processed results
│   └── ...
├── main.py              # CLI entry point
├── pyproject.toml       # Project configuration
└── requirements.txt     # Dependencies
```

### Key Components

1. **ContourExtractor**: Analyzes video frames to detect movement
2. **LayerFactory**: Groups related contours across frames
3. **LayerManager**: Filters and optimizes layers
4. **Exporter**: Generates output videos

## Code Review Process

1. Maintainers will review your PR
2. Address any requested changes
3. Once approved, your PR will be merged
4. Your contribution will be credited in releases

## Questions?

- Open an issue for questions
- Tag maintainers for urgent matters
- Be patient and respectful

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Video-Summary! 🎥✨
