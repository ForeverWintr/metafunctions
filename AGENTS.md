# AGENTS.md

This file provides guidance to AI coding agents working with code in this repository.

## Project

MetaFunctions is a function composition / data pipelining library (`step1 | step2 + step3`). Pure Python, one runtime dependency (`ansicolors`, imported as `colors`). Version lives in `metafunctions/__init__.py` (`__version__`) and is read by `pyproject.toml` (setuptools dynamic version); release notes go in `HISTORY.md`.

## Commands

```sh
uv sync                                                        # create .venv with project + dev group (coverage, black, flake8)

uv run python -m unittest discover                             # run all tests (stdlib unittest, no pytest)
uv run python -m unittest metafunctions.tests.test_pipe        # one module
uv run python -m unittest metafunctions.tests.test_pipe.TestIntegration.test_basic_usage  # one test
uv run --python 3.11 python -m unittest discover               # another python version (supported: >=3.11)

uv run black .                                                 # formatter
uv run flake8 . --extend-exclude .venv --select=E9,F63,F7,F82  # the lint check CI fails on

uv build && uv publish                                         # release
```

Dependencies are declared in `pyproject.toml` and locked in `uv.lock` (commit it; CI runs `uv sync --locked`). Use `uv add` / `uv add --dev` to change them.

CI (`.github/workflows/test.yml`) runs flake8 then tests under coverage across Python 3.11–3.14 on Linux/macOS/Windows. `ConcurrentMerge` tests are skipped on Windows (no `os.fork`).

## Architecture

Everything is a `MetaFunction` (`metafunctions/core/base.py`), an abstract callable that holds other callables in `.functions`. Composition happens via operator overloads on `MetaFunction`:

- `|` → `FunctionChain` (sequential; output of one is input to the next)
- `&` → `FunctionMerge` with `operators.concat` (returns a tuple of results)
- `+ - * /` → `FunctionMerge` with the corresponding `operator` function
- `@` → chain into `star(other)` (unpack previous result as `*args`)

Key behaviours spread across files:

- **Auto-upgrading operands**: the `binary_operation` decorator (`core/decorators.py`) wraps plain callables in `SimpleFunction` and non-callables in `DeferredValue` before composing, so `input | f | print` and `1 | f` work.
- **Flattening**: `FunctionChain.combine` / `FunctionMerge.combine` flatten nested chains/merges of the same kind (`&` merges flatten; arithmetic merges deliberately do not, since order of operations matters). This keeps `str()` output like `(a | b | c)`.
- **FunctionMerge arg dispatch**: one positional arg is broadcast to every function; multiple args are distributed one-per-function, with leftover functions called with no args; more args than functions raises `CallError`. Subclasses customise via `_get_call_iterators` and `_call_function` — `MergeMap` (`map.py`, exposed as `mmap`) and `ConcurrentMerge` (`core/concurrent.py`, exposed as `concurrent`) are both `FunctionMerge` subclasses that override these hooks.
- **CallState** (`core/call_state.py`): every `__call__` is wrapped by `manage_call_state`, which creates a `CallState` at the outermost entry point and threads it through as the `call_state` kwarg, pushing/popping nodes to build a metafunction-aware call tree. It is used for (a) `locate_error`'s `->highlighted<-` error location string, built by string-matching `str()` of nodes (`highlight_active_function` + `util.replace_nth`), so `__str__` formats matter for correctness; and (b) the `call_state.data` dict used by `store`/`recall`.
- **Receiving call_state in user functions**: a wrapped function only gets the `call_state` kwarg if it has `_receives_call_state = True`; `bind_call_state` sets this and passes call_state as the first positional arg instead.
- **ConcurrentMerge** forks one child per function, sends pickled results/exceptions/`call_state.data` back over a `multiprocessing.Queue`, and merges child `call_state.data` into the parent. Children exit with `os._exit(0)` intentionally (so unittest can't catch `SystemExit` and keep the child alive).
- `metafunctions/api.py` is the public surface (`node`, `star`, `store`, `recall`, `concurrent`, `mmap`, `locate_error`, `bind_call_state`), re-exported from `metafunctions/__init__.py`.

## Tests

Tests live in `metafunctions/tests/`. `simple_nodes.py` defines reusable nodes `a`, `b`, `c`, … (each appends its letter to a string input, so `(a | b)('_') == '_ab'`) used throughout the suite. Test classes subclass `tests/util.py:BaseTestCase`.
