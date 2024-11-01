# llm-groq-whisper

[![PyPI](https://img.shields.io/pypi/v/llm-groq-whisper.svg)](https://pypi.org/project/llm-groq-whisper/)
[![Changelog](https://img.shields.io/github/v/release/simonw/llm-groq-whisper?include_prereleases&label=changelog)](https://github.com/simonw/llm-groq-whisper/releases)
[![Tests](https://github.com/simonw/llm-groq-whisper/actions/workflows/test.yml/badge.svg)](https://github.com/simonw/llm-groq-whisper/actions/workflows/test.yml)
[![License](https://img.shields.io/badge/license-Apache%202.0-blue.svg)](https://github.com/simonw/llm-groq-whisper/blob/main/LICENSE)

Transcribe audio using the Groq.com Whisper API

## Installation

Install this plugin in the same environment as [LLM](https://llm.datasette.io/).
```bash
llm install llm-groq-whisper
```
## Usage

Run transcripts using:
```bash
llm groq-whisper audio.mp3
```
Use `llm groq-whisper --help` for further options.

## Development

To set up this plugin locally, first checkout the code. Then create a new virtual environment:
```bash
cd llm-groq-whisper
python -m venv venv
source venv/bin/activate
```
Now install the dependencies and test dependencies:
```bash
llm install -e '.[test]'
```
To run the tests:
```bash
python -m pytest
```
