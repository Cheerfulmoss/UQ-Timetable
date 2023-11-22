# Contribution Guidelines

## Prerequisites

- Python 3.12.0
- [Requests library](https://docs.python-requests.org/en/latest/)

## Setup Instructions

None as of now.

## Folder Structure

The project adheres to the following organized folder structure:
```
├── <root dir>  
│   ├── Main.py  
    └── cogs  
        ├── api  
            └── timetable_api_calls.py  
        ├── base-files  
            └── api-calls-cache.json  
        ├── base.py  
        └── helpCommand.py  
```
In this structure:

- <root dir> represents the main directory of the project.
- Main.py is the main entry point of the project.
- The cogs directory contains submodules for different functionalities:
  - api includes the timetable_api_calls.py file.
- The base-files directory houses essential files, such as api-calls-cache.json.
- base.py and helpCommand.py are main components of the project.

Feel free to replace the placeholders like <root dir> with the actual names relevant to your project.

## Code Style Guidelines

We adhere to the [Google Python Style Guide](https://google.github.io/styleguide/pyguide.html).

## Testing Guidelines

None as of now.

## Branching Strategy

None as of now.

## Commit Message Guidelines

- Commit names should be short but descriptive. Use common sense.
- For large or complicated commits, provide additional details in the extended description.

## Pull Request Process

When submitting a pull request, please follow these steps:

1. Fork the repository and create a branch for your work.
2. Make changes and commit them, adhering to the commit message guidelines.
3. Open a pull request with a clear title and description.
4. If your pull request addresses any existing issues, mention the relevant issue numbers in the description.

## Code Review Expectations

We trust that contributors will adhere to best practices for code quality, style, and functionality. Code reviews will include constructive feedback and suggestions for improvement.

## Issue Guidelines

When reporting issues, please include the following details:

1. A clear and concise title.
2. Detailed steps to reproduce the issue.
3. Expected behavior and actual behavior.
4. Any relevant error messages or logs.

## Feature Requests

We welcome feature requests! When submitting a feature request, please include:

1. A clear and descriptive title.
2. Detailed information about the proposed feature and its use case.

## License Agreement

By contributing to this project, you agree to license your work under the terms of the [GNU General Public License v3.0 (GPL-3.0)](https://www.gnu.org/licenses/gpl-3.0.html). Please review the full text of the license in the [LICENSE](./LICENSE) file.

