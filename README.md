## Home of _Omega_, a napari-aware autonomous LLM-based agent specialized in image processing and analysis.

[![License BSD-3](https://img.shields.io/pypi/l/napari-chatgpt.svg?color=green)](https://github.com/royerlab/napari-chatgpt/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-chatgpt.svg?color=green)](https://pypi.org/project/napari-chatgpt)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-chatgpt.svg?color=green)](https://python.org)
[![Downloads](https://pepy.tech/badge/napari-chatgpt)](https://pepy.tech/project/napari-chatgpt)
[![Downloads](https://pepy.tech/badge/napari-chatgpt/month)](https://pepy.tech/project/napari-chatgpt)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-chatgpt)](https://napari-hub.org/plugins/napari-chatgpt)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.10828225.svg)](https://doi.org/10.5281/zenodo.10828225)
[![GitHub stars](https://img.shields.io/github/stars/royerlab/napari-chatgpt?style=social)](https://github.com/royerlab/napari-chatgpt/)
[![GitHub forks](https://img.shields.io/github/forks/royerlab/napari-chatgpt?style=social)](https://github.com/royerlab/napari-chatgpt/)

<img src='https://github.com/royerlab/napari-chatgpt/assets/1870994/c85185d2-6d16-472d-a2c8-5680ea869bf2' height='300'>
<img height="300" alt="image" src="https://github.com/royerlab/napari-chatgpt/assets/1870994/f3ea245e-dd86-4ff2-802e-48c2073cb6f9">


A [napari](napari.org) plugin that leverages Large Language Models
to implement _Omega_, a napari-aware agent capable of performing image processing and analysis tasks
in a conversational manner.

This repository started as a 'week-end project'
by [Loic A. Royer](https://twitter.com/loicaroyer)
who leads a [research group](https://royerlab.org) at
the [Chan Zuckerberg Biohub](https://royerlab.org). It
uses [LiteMind](https://github.com/royerlab/litemind), an LLM abstraction library
supporting multiple providers including [OpenAI](https://openai.com),
[Anthropic](https://anthropic.com) (Claude), and [Google Gemini](https://deepmind.google/technologies/gemini/),
as well as [napari](https://napari.org), a fast, interactive,
multi-dimensional image viewer for Python,
[another](https://ilovesymposia.com/2019/10/24/introducing-napari-a-fast-n-dimensional-image-viewer-in-python/)
week-end project, initially started by Loic and [Juan Nunez-Iglesias](https://github.com/jni).

# What is Omega?

Omega is an LLM-based and tool-armed autonomous agent that demonstrates the
potential for Large Language Models (LLMs) to be applied to image processing,
analysis and visualization.
Can LLM-based agents write image processing code and napari widgets, correct its
coding mistakes, performing follow-up analysis, and controlling the napari viewer?
The answer appears to be yes.

The publication is available here: [10.1038/s41592-024-02310-w](https://doi.org/10.1038/s41592-024-02310-w).
The preprint can be downloaded here: [10.5281/zenodo.10828225](https://doi.org/10.5281/zenodo.10828225).

#### In this video, I ask Omega to segment an image using the [SLIC](https://www.iro.umontreal.ca/~mignotte/IFT6150/Articles/SLIC_Superpixels.pdf) algorithm. It makes a first attempt using the implementation in scikit-image but fails because of an inexistent 'multichannel' parameter. Realizing that, Omega tries again, and this time succeeds:

https://user-images.githubusercontent.com/1870994/235768559-ca8bfa84-21f5-47b6-b2bd-7fcc07cedd92.mp4

#### After loading a sample 3D image of cell nuclei in napari, I asked Omega to segment the nuclei using the Otsu method. My first request was vague, so it just segmented foreground versus background. I then ask to segment the foreground into distinct segments for each connected component. Omega does a rookie mistake by forgetting to 'import np'. No problem; it notices, tries again, and succeeds:

https://user-images.githubusercontent.com/1870994/235769990-a281a118-1369-47aa-834a-b491f706bd48.mp4

#### In this video, one of my favorites, I ask Omega to make a 'Max color projection widget.' It is not a trivial task, but it manages!

https://github.com/royerlab/napari-chatgpt/assets/1870994/bb9b35a4-d0aa-4f82-9e7c-696ef5859a2f

As LLMs improve, Omega will become even more adept at handling complex
image processing and analysis tasks. Through the [LiteMind](https://github.com/royerlab/litemind) library,
Omega supports multiple LLM providers including OpenAI (GPT-4, GPT-4o), Anthropic (Claude),
and Google Gemini. Many of the videos (see below and here) are highly reproducible,
with a typically 90% success rate (see preprint for a reproducibility analysis).

Omega could eventually help non-experts process and analyze images, especially
in the bioimage domain.
It is also potentially valuable for educative purposes as it could
assist in teaching image processing and analysis, making it more accessible.
Although the LLMs powering Omega may still need to be on par with an expert image
analyst or computer vision expert, it is just a matter of time...

Omega holds a conversation with the user and uses different tools to answer questions,
download and operate on images, write widgets for napari, and more.

## Omega's Built-in AI-Augmented Code Editor

The Omega AI-Augmented Code Editor is a new feature within Omega, designed to enhance the Omega's user experience. This
editor is not just a text editor; it's a powerful interface that interacts with the Omega dialogue agent to generate,
optimize, and manage code for advanced image analysis tasks.

<img src='https://github.com/royerlab/napari-chatgpt/assets/1870994/cf9b1c15-f11a-4e25-a73d-d96915c46c6a' width='800'>

#### Key Features

- **Code Highlighting and Completion**: For ease of reading and writing, the code editor comes with built-in syntax
  highlighting and intelligent code completion features.
- **LLM-Augmented Tools**: The editor is equipped with AI tools that assist in commenting, cleaning up, fixing,
  modifying, and performing safety checks on the code.
- **Persistent Code Snippets**: Users can save and manage snippets of code, preserving their work across multiple Napari
  sessions.
- **Network Code Sharing (Code-Drop)**: Facilitates the sharing of code snippets across the local network, empowering
  collaborative work and knowledge sharing.

#### Usage Scenarios

- **Widget Creation**: Expert users can create widgets using the Omega dialogue agent and retain them for future use.
- **Collaboration**: Share custom widgets with colleagues or the community, even if they don't have access to an API
  key.
- **Learning**: New users can learn from the AI-augmented suggestions, improving their coding skills in Python and image
  analysis workflows.

You can find more information in the
corresponding [wiki page](https://github.com/royerlab/napari-chatgpt/wiki/OmegaCodeEditor).

----------------------------------

## Omega's Installation instructions:

Assuming you have a Python environment with a working napari installation, you can simply:

    pip install napari-chatgpt

Or install the plugin from napari's plugin installer.

For detailed instructions and variations, check [this page](http://github.com/royerlab/napari-chatgpt/wiki/InstallOmega)
of our wiki.

## Requirements:

You need an API key from at least one supported LLM provider:
- **OpenAI** - Get your key at [platform.openai.com](https://platform.openai.com)
- **Anthropic (Claude)** - Get your key at [console.anthropic.com](https://console.anthropic.com)
- **Google Gemini** - Get your key at [aistudio.google.com](https://aistudio.google.com)

Check [here](https://github.com/royerlab/napari-chatgpt/wiki/APIKeys) for details on API key setup.
Omega will automatically detect which providers you have configured.

## Usage:

Check this [page](https://github.com/royerlab/napari-chatgpt/wiki/HowToStartOmega) of
our [wiki](https://github.com/royerlab/napari-chatgpt/wiki) for details on how to start Omega.

## Tips, Tricks, and Example prompts:

Check our guide on how to prompt Omega and some
examples [here](https://github.com/royerlab/napari-chatgpt/wiki/Tips&Tricks).

## Video Demos:

You can check the original release videos [here](https://github.com/royerlab/napari-chatgpt/wiki/VideoDemos).
You can also find the latest preprint videos on [Vimeo](https://vimeo.com/showcase/10983382).

## How does Omega work?

The publication is available here: [10.1038/s41592-024-02310-w](https://doi.org/10.1038/s41592-024-02310-w).
Check our preprint here: [10.5281/zenodo.10828225](https://doi.org/10.5281/zenodo.10828225).

and our [wiki page](https://github.com/royerlab/napari-chatgpt/wiki/OmegaDesign) on Omega's design and architecture.

## Cost:

LLM API costs vary by provider and model. For reference:
- **OpenAI** pricing: [openai.com/pricing](https://openai.com/pricing)
- **Anthropic** pricing: [anthropic.com/pricing](https://anthropic.com/pricing)
- **Google Gemini** pricing: [ai.google.dev/pricing](https://ai.google.dev/pricing)

Most providers allow you to set spending limits to control costs.

## Disclaimer:

Do not use this software lightly; it will download libraries of its own volition
and write any code it deems necessary; it might do what you ask, even
if it is a very bad idea. Also, beware that it might _misunderstand_ what you ask and
then do something bad in ways that elude you. For example, it is unwise to use Omega to delete
'some' files from your system; it might end up deleting more than that if you are unclear in
your request.  
Omega is generally safe as long as you do not make dangerous requests. To be 100% safe, and
if your experiments with Omega could be potentially problematic, I recommend using this
software from within a sandboxed virtual machine.
API keys are only as safe as the overall machine is, see the section below on API key hygiene.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## API key hygiene:

Best Practices for Managing Your API Keys:

- **Host Computer Hygiene:** Ensure that the machine you're installing napari-chatgpt/Omega on is secure, free of malware
  and viruses, and otherwise not compromised. Make sure to install antivirus software on Windows.
- **Security:**  Treat your API key like a password. Do not share it with others or expose it in public repositories or
  forums.
- **Cost Control:** Set spending limits on your LLM provider account:
  [OpenAI](https://platform.openai.com/account/limits) |
  [Anthropic](https://console.anthropic.com/settings/limits) |
  [Google Gemini](https://console.cloud.google.com/billing)
- **Regenerate Keys:** If you believe your API key has been compromised, revoke and regenerate it from your provider's
  console immediately:
  [OpenAI](https://platform.openai.com/api-keys) |
  [Anthropic](https://console.anthropic.com/settings/keys) |
  [Google Gemini](https://aistudio.google.com/apikey)
- **Key Storage:** Omega has a built-in 'API Key Vault' that encrypts keys using a password, this is the preferred
  approach. You can also store the key in an environment variable, but that is not encrypted and could compromise the
  key.

## Contributing

Contributions are extremely welcome. The project uses a Makefile for development:

```bash
make setup      # Install with dev dependencies + pre-commit hooks
make test       # Run all tests
make test-cov   # Run tests with coverage
make format     # Format code with black and isort
make check      # Run all code checks
```

Please ensure the coverage stays the same before you submit a pull request.

## License

Distributed under the terms of the [BSD-3] license,
"napari-chatgpt" is free and open-source software

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
