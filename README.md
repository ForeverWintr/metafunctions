# MetaFunctions
[![Build Status](https://travis-ci.org/ForeverWintr/metafunctions.svg?branch=master)](https://travis-ci.org/ForeverWintr/metafunctions) [![Build status](https://ci.appveyor.com/api/projects/status/8120lqx7e9ys2m0u/branch/master?svg=true)](https://ci.appveyor.com/project/ForeverWintr/metafunctions/branch/master) [![Codecov](https://codecov.io/gh/ForeverWintr/metafunctions/coverage.svg?branch=master)](https://codecov.io/gh/ForeverWintr/metafunctions)
![GithubActions Badge](https://github.com/ForeverWintr/metafunctions/actions/workflows/python-package.yml/badge.svg)



## Metafunctions is a function composition and data pipelining library.
It allows for data pipeline creation separate from execution, so instead of writing:

```python
result = step3(step2(step1(data)))

#or
result_1 = step1(data)
result_2 = step2(result_1)
result_3 = step3(result_2)
```

You can write:

```python
pipeline = step1 | step2 | step3
result = pipeline(data)
```

### Why do you need new syntax for pipelining functions?
Well you may not *need* a new syntax, but the ability to compose a data pipeline before executing it does impart some advantages, such as:

* **Reuse**. Compose a pipeline once and use it in multiple places, including as part of larger pipelines:
  ```python
  # load, parse, clean, validate, and format are functions
  preprocess = load | parse | clean | validate | format

  # preprocess is now a MetaFunction, and can be reused
  clean_data1 = preprocess('path/to/data/file')
  clean_data2 = preprocess('path/to/different/file')

  # Preprocess can be included in larger pipelines
  pipeline = preprocess | step1 | step2 | step3
  ```
* **Readability**. `step1 | step2 | step3` is both read and executed from left to right, unlike `step3(step2(step1()))`, which is executed from innermost function outwards.
* **Inspection**. Can't remember what your MetaFunction does? `str` will tell you:
  ```python
  >>> str(preprocess)
  "(load | parse | clean | validate | format)"
* **Advanced Composition**. Anything beyond simple function chaining becomes difficult using traditional methods. What if you want to send the result of `step1` to both steps `2` and `3`, then sum the results? The traditional approach requires an intermediate variable and can quickly become unwieldy:
  ```python
  result1 = step1(data)
  result2 = step2(result1) + step3(result1)
  ```
  Using metafunctions, you can declare a pipeline that does the same thing:
  ```python
  pipeline = step1 | step2 + step3
  result = pipeline(data)
  ```

## Installation

MetaFunctions supports python 3.5+ (tested to 3.10+)

`pip install metafunctions`

## How does it work?

Conceptually, a MetaFunction is a function that contains other functions. When you call a MetaFunction, the MetaFunction calls the functions it contains.

You can create a MetaFunction using the `node` decorator:
```python
from metafunctions import node

@node
def get_name(prompt):
    return input(prompt)

@node
def say_hello(name):
    return 'Hello {}!'.format(name)
```

MetaFunctions override certain operators to allow for composition. For example, the following creates a new MetaFunction that combines `get_name` and `say_hello`:
```python
greet = get_name | say_hello
```

When we call the `greet` MetaFunction, it calls both its internal functions in turn.
```python
# First, `get_name` is called, which prints our prompt to the screen.
# If we enter 'Tom' at the prompt, the second function returns the string 'Hello Tom!'
greeting = greet('Please enter your name ')
print(greeting) # Hello Tom!
```

MetaFunctions are also capable of upgrading regular functions to MetaFunctions at composition time, so we can simplify our example by composing `say_hello` directly with the builtin `input` and `print` functions:
```python
>>> greet = input | say_hello | print
>>> greet('Please enter your name: ')
# Please enter your name: Tom
# Hello Tom!
```

## Features

### Helpful Tracebacks

Errors in composed functions can be confusing. If an exception occurs in a MetaFunction, the exception traceback will tell you which function the exception occurred in. But what if that function appears multiple times in the data pipeline?

Imagine this function, which downloads stringified numeric data from a web api:

```python
>>> compute_value = (query_volume | float) * (query_price | float)
>>> compute_value('http://prices.com/123')
```

Here we've assumed that `query_volume` and `query_price` will return strings that convert cleanly to floats, but what if something goes wrong?

```
>>> compute_value('http://prices.com/123')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  ...
builtins.ValueError: could not convert string to float: '$800'
```

We can deduce that float conversion failed, but *which* float function raised the exception? MetaFunctions addresses this by adding the `locate_error` metafunction decorator, which adds a location information string to any exception raised within the pipeline:

```
>>> from metafunctions import locate_error
>>> with_location = locate_error(compute_value)
>>> with_location('http://prices.com/123')
Traceback (most recent call last):
  File "<stdin>", line 1, in <module>
  ...
builtins.ValueError: could not convert string to float: '$800'
Occured in the following function: ((query_volume | float) + (query_price | ->float<-))
```

### Advanced Pipeline Construction Tools

Metafunctions provides utilities for constructing advanced function pipelines.

* **store** / **recall**: store the output of the preceding function, and recall it later to pass to a different function. For example:
  
  ```python
  # The following pipeline sends the output of `a` to `b`, and also adds it to the output of `c`
  p = a | store('a') | b | recall('a') + c
  ```

* **mmap**: A MetaFunction decorator that wraps a function (or MetaFunction) and calls it once per item in the input it receives. This allows you to  create loops in function pipelines:
  
  ```python
  (1, 2, 3) | mmap(process) # <- equivalent to (1, 2, 3) | (process & process & process)
  ```
  `mmap` duplicates the behaviour of the builtin [`map`](https://docs.python.org/3/library/functions.html#map) function.

* **star**: Calls the wrapped MetaFunction with *args instead of args (It's analogous to `lambda args, **kwargs: metafunction(*args, **kwargs)`). This allows you to incorporate functions that accept more than one parameter into your function pipeline:

  ```python
  @node
  def f(result1, result2):
      ...

  # When cmp is called, f will receive the results of both a and b as positional args
  cmp = (a & b) | star(f)
  ```
  `star` can be combined with the above `mmap` to duplicate the behaviour of [`itertools.starmap`](https://docs.python.org/3/library/itertools.html#itertools.starmap): 

  ```python
  starmap = star(mmap(f))
  ```

  For more discussion of `star`, see [this pull request](https://github.com/ForeverWintr/metafunctions/pull/9)

* **concurrent**:
  *experimental, requires an os that provides `os.fork()`*

  Consider the following long running MetaFunction:

  ```python
  process_companies = get_company_data | filter | process
  process_customers = get_customer_data | filter | process

  process_all = process_companies & process_customers
  ```

  Assuming the component functions in the `process_all` MetaFunction follow good functional practices and do not have side effects, it's easy to see that `process_companies` and `process_customers` are independent of each other. If that's the case, we can safely execute them in parallel. The `concurrent` metafunction decorator allows you to specify steps in the function pipeline to execute in parallel:

  ```python
  from metafunctions import concurrent

  do_large_calculation_async = concurrent(process_companies + process_customers)
  ```

  `concurrent` can be combined with `mmap` to create an asynchronous map, similar to [`multiprocessing.pool.map`](https://docs.python.org/3/library/multiprocessing.html#multiprocessing.pool.Pool.map): 
  
  ```python
  map_async = concurrent(mmap(f))
  ```
