Update the vendored bolt-python wheel to the latest commit on the `main` branch.

## Steps

1. If `.bolt-python-build/` exists, `cd` into it and run `git pull`. Otherwise, clone bolt-python:
   ```
   git clone --depth 1 https://github.com/slackapi/bolt-python.git .bolt-python-build
   ```

2. `cd .bolt-python-build` and get the HEAD commit SHA (short form, 7 chars):
   ```
   SHA=$(git rev-parse --short HEAD)
   ```

3. Read the current version from `slack_bolt/version.py` and patch it to append `+<SHA>` as a PEP 440 local version identifier:
   ```
   sed -i '' "s/__version__ = \"\(.*\)\"/__version__ = \"\1+$SHA\"/" slack_bolt/version.py
   ```

4. Build the wheel:
   ```
   python -m build --wheel
   ```

5. Remove any old `.whl` files from `vendor/` and copy the new one in:
   ```
   rm -f ../vendor/slack_bolt-*.whl
   cp dist/slack_bolt-*.whl ../vendor/
   ```

6. Update the whl filename in all three `requirements.txt` files (`claude-agent-sdk/requirements.txt`, `openai-agents-sdk/requirements.txt`, `pydantic-ai/requirements.txt`). Replace the existing `../vendor/slack_bolt-*.whl` line with the new filename.

7. Clean up the build directory:
   ```
   cd .. && rm -rf .bolt-python-build
   ```

8. Report the old version/SHA vs new version/SHA to the user. Do NOT commit — let the user review first.
