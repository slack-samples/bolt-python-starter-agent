Switch from the vendored bolt-python wheel to the latest published `slack-bolt` package on PyPI.

## Steps

1. Look up the latest published version of `slack-bolt`:
   ```
   curl -s https://pypi.org/pypi/slack-bolt/json | python3 -c "import sys,json; print(json.load(sys.stdin)['info']['version'])"
   ```

2. Delete the `vendor/` directory:
   ```
   rm -rf vendor
   ```

3. In all three `requirements.txt` files (`claude-agent-sdk/requirements.txt`, `openai-agents-sdk/requirements.txt`, `pydantic-ai/requirements.txt`), replace the `../vendor/slack_bolt-*.whl` line with `slack-bolt>=<version>` using the version from step 1.

4. In all three `pyproject.toml` files (`claude-agent-sdk/pyproject.toml`, `openai-agents-sdk/pyproject.toml`, `pydantic-ai/pyproject.toml`), replace the comment `# slack-bolt is installed from a vendored whl — see ../vendor/` with an actual dependency `"slack-bolt>=<version>"` using the version from step 1.

5. If `.github/dependabot.yml` has an `ignore` rule for `slack-bolt`, remove it so Dependabot can manage updates.

6. Update `README.md` — replace the "Local Development" section that describes vendored bolt with:
   ```
   ## Local Development

   This repo uses [`slack-bolt`](https://pypi.org/project/slack-bolt/) from PyPI.
   ```

7. Report the version change to the user. Do NOT commit — let the user review first.
