# Maintainers Guide

## Using Bolt Framework Development Builds

This repo vendors a pre-release build of [`slack-bolt`](https://github.com/slackapi/bolt-python) from the `main` branch. The `.whl` wheel lives in `vendor/` and is referenced by each implementation's `requirements.txt`.

Two [Claude Code slash commands](https://docs.anthropic.com/en/docs/claude-code/slash-commands) are available to manage this:

### `/vendor-bolt` — Update the vendored wheel

Clones bolt-python `main`, builds a wheel with a local version identifier (e.g. `1.2.3+abc1234`), replaces the wheel in `vendor/`, and updates all `requirements.txt` references. Use this to pull in the latest unreleased bolt-python changes.

### `/unvendor-bolt` — Switch to the published PyPI package

Removes the `vendor/` directory, replaces the wheel reference in all `requirements.txt` and `pyproject.toml` files with the latest `slack-bolt` version from PyPI, and re-enables Dependabot updates. Use this when the vendored changes have been released and the repo should track the public package.

Both commands leave changes uncommitted for review.
