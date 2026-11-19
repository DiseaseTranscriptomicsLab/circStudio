# Contributing to circStudio

Thank you for your interest in circStudio. This page explains how to ask for
help, report a problem and propose a change. Everyone taking part is expected to
follow the [Code of Conduct](CODE_OF_CONDUCT.md).

## Getting help

- Read the [documentation](https://DiseaseTranscriptomicsLab.github.io/circStudio/),
  which includes four tutorial notebooks and a full reference for every function.
- If your question is not answered there, open an issue on the
  [GitHub issue tracker](https://github.com/DiseaseTranscriptomicsLab/circStudio/issues)
  and label it `question`. Questions asked in public help the next user too.

## Reporting a bug

Open an issue on the [issue tracker](https://github.com/DiseaseTranscriptomicsLab/circStudio/issues)
and include:

1. the circStudio version (`python -c "import importlib.metadata as m; print(m.version('circStudio'))"`),
   your Python version and your operating system;
2. the smallest piece of code that shows the problem, ideally using one of the
   example recordings in `src/circstudio/data` so that others can run it;
3. what you expected to happen and what happened instead, including the full
   error message.

If the problem only occurs with your own recordings and you cannot share them,
say which device and file format they come from.

## Proposing a change

Small fixes (typos, documentation, clearly scoped bugs) are welcome as pull
requests directly. For a new feature or a change in behavior, please open an
issue first so the change can be discussed before you invest time in it.

1. Fork the repository and create a branch from `main`.
2. Install the package in editable mode with the test dependencies:

   ```bash
   python -m venv .venv && source .venv/bin/activate
   pip install -e . pytest pytest-mock pyexcel-ods
   ```

3. Make your change and add or update tests in `tests/`. New analysis functions
   should be tested against values that can be derived independently (for
   example, on synthetic signals with known properties), and new algorithms
   should cite the publication that defines them in their docstring.
4. Run the test suite and make sure it passes:

   ```bash
   pytest tests -q
   ```

5. Open a pull request describing what the change does and why. The test suite
   runs automatically on Linux, macOS and Windows for every pull request.

By contributing, you agree that your contribution is released under the
project's license, the [GNU General Public License v3.0](LICENSE.md).
