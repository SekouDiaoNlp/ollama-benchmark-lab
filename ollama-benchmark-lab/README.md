# 🦙 Ollama Benchmark Lab

[![PyPI version](https://badge.fury.io/py/ollama-benchmark-lab.svg)](https://badge.fury.io/py/ollama-benchmark-lab)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Documentation Status](https://readthedocs.org/projects/ollama-benchmark-lab/badge/?version=latest)](https://ollama-benchmark-lab.readthedocs.io/en/latest/?badge=latest)
[![Python Versions](https://img.shields.io/pypi/pyversions/ollama-benchmark-lab.svg)](https://pypi.org/project/ollama-benchmark-lab/)
[![Typing: Strict](https://img.shields.io/badge/typing-strict-blue.svg)](https://mypy.readthedocs.io/en/stable/)

A strictly-typed, modern, and high-performance local LLM benchmarking framework designed for local Ollama models. Evaluates models on **PLAN**, **ACT**, and **SWE** style tasks.

## 🌟 Features

- **Local First**: Built specifically for local models via Ollama. No remote API dependencies.
- **Production Ready**: Fully typed (`mypy --strict`), Sphinx-documented, and packaged for PyPI.
- **SWE Harness Integration**: Evaluate software engineering capabilities by running isolated tests inside Docker.
- **Distributed Ready**: Ray executor support for high-throughput evaluation.
- **Strictly Typed**: Zero `Any` policies for predictable API usage.

## 📦 Installation

```bash
pip install ollama-benchmark-lab
```

*Requires Python >=3.10, <3.13*

## 🚀 Quick Start

Run the benchmarking suite via the CLI:

```bash
autollama --limit 5
```

## 📚 Documentation

Full documentation is available at [ReadTheDocs](https://ollama-benchmark-lab.readthedocs.io).
It includes API references, architecture overviews, and tutorials for extending the sandbox pool and adding new evaluations.

## 🛠️ Development

To contribute, set up the project locally:

```bash
git clone https://github.com/sek/ollama-benchmark-lab.git
cd ollama-benchmark-lab
poetry install
```

Ensure you pass the strict MyPy checks:
```bash
poetry run mypy . --strict
```

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
