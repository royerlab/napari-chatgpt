# napari-chatgpt

[![License BSD-3](https://img.shields.io/pypi/l/napari-chatgpt.svg?color=green)](https://github.com/royerlab/napari-chatgpt/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-chatgpt.svg?color=green)](https://pypi.org/project/napari-chatgpt)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-chatgpt.svg?color=green)](https://python.org)
[![tests](https://github.com/royerlab/napari-chatgpt/workflows/tests/badge.svg)](https://github.com/royerlab/napari-chatgpt/actions)
[![codecov](https://codecov.io/gh/royerlab/napari-chatgpt/branch/main/graph/badge.svg)](https://codecov.io/gh/royerlab/napari-chatgpt)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-chatgpt)](https://napari-hub.org/plugins/napari-chatgpt)

A napari plugin that levegares Large Language Models like ChatGPT to facilitate image processing and analysis.

It implements /Omega/ an agent that has at its disposal the follwoing tools:

- web search 
- web image serach 
- wikipedia search
- file download
- napari viewer control (running its own sub-LLM)
- napari query (running its own sub-LLM)
- napari widget maker (running its own sub-LLM)
- cellpose segmentation (running its own sub-LLM)
- python function signature query




----------------------------------


## Installation

You can install `napari-chatgpt` via [pip]:

    pip install napari-chatgpt

To install latest development version :

    pip install git+https://github.com/royerlab/napari-chatgpt.git

## Contributing

Contributions are very welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-chatgpt" is free and open source software

## Issues

If you encounter any problems, please [file an issue] along with a detailed
description.

[napari]: https://github.com/napari/napari

[Cookiecutter]: https://github.com/audreyr/cookiecutter

[@napari]: https://github.com/napari

[MIT]: http://opensource.org/licenses/MIT

[BSD-3]: http://opensource.org/licenses/BSD-3-Clause

[GNU GPL v3.0]: http://www.gnu.org/licenses/gpl-3.0.txt

[GNU LGPL v3.0]: http://www.gnu.org/licenses/lgpl-3.0.txt

[Apache Software License 2.0]: http://www.apache.org/licenses/LICENSE-2.0

[Mozilla Public License 2.0]: https://www.mozilla.org/media/MPL/2.0/index.txt

[cookiecutter-napari-plugin]: https://github.com/napari/cookiecutter-napari-plugin

[file an issue]: https://github.com/royerlab/napari-chatgpt/issues

[napari]: https://github.com/napari/napari

[tox]: https://tox.readthedocs.io/en/latest/

[pip]: https://pypi.org/project/pip/

[PyPI]: https://pypi.org/
