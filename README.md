## Home of _Omega_, a napari-aware autonomous LLM-based agent specialized in image processing and analysis.

[![License BSD-3](https://img.shields.io/pypi/l/napari-chatgpt.svg?color=green)](https://github.com/royerlab/napari-chatgpt/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-chatgpt.svg?color=green)](https://pypi.org/project/napari-chatgpt)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-chatgpt.svg?color=green)](https://python.org)
[![tests](https://github.com/royerlab/napari-chatgpt/workflows/tests/badge.svg)](https://github.com/royerlab/napari-chatgpt/actions)
[![codecov](https://codecov.io/gh/royerlab/napari-chatgpt/branch/main/graph/badge.svg)](https://codecov.io/gh/royerlab/napari-chatgpt)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-chatgpt)](https://napari-hub.org/plugins/napari-chatgpt)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8240289.svg)](https://doi.org/10.5281/zenodo.8240289)

<img src='https://github.com/royerlab/napari-chatgpt/assets/1870994/c85185d2-6d16-472d-a2c8-5680ea869bf2' height='300'>
<img height="300" alt="image" src="https://github.com/royerlab/napari-chatgpt/assets/1870994/f3ea245e-dd86-4ff2-802e-48c2073cb6f9">


A [napari](napari.org) plugin that leverages OpenAI's Large Language Model
ChatGPT to implement _Omega_
a napari-aware agent capable of performing image processing and analysis tasks
in a conversational manner.

This repository started as a 'week-end project'
by [Loic A. Royer](https://twitter.com/loicaroyer)
who leads a [research group](https://royerlab.org) at
the [Chan Zuckerberg Biohub](https://czbiohub.org/sf/). It
leverages [OpenAI](https://openai.com)'s ChatGPT API via
the [LangChain](https://python.langchain.com/en/latest/index.html) Python
library, as well as [napari](https://napari.org), a fast, interactive,
multi-dimensional
image viewer for
Python, [another](https://ilovesymposia.com/2019/10/24/introducing-napari-a-fast-n-dimensional-image-viewer-in-python/)
project initially started by Loic and [Juan Nunez-Iglesias](https://github.com/jni).

# What is Omega?

Omega is an LLM-based and tool-armed autonomous agent that demonstrates the
potential for Large Language Models (LLMs) to be applied to image processing,
analysis and visualization.
Can LLM-based agents write image processing code and napari widgets, correct its
coding mistakes, performing follow-up analysis, and controlling the napari viewer? 
The answer appears to be yes.

The preprint can be downloaded here: [10.5281/zenodo.8240289](https://zenodo.org/records/8240289)


#### In this video, I ask Omega to segment an image using the [SLIC](https://www.iro.umontreal.ca/~mignotte/IFT6150/Articles/SLIC_Superpixels.pdf) algorithm. It makes a first attempt using the implementation in scikit-image but fails because of an inexistent 'multichannel' parameter. Realizing that, Omega tries again, and this time succeeds:

https://user-images.githubusercontent.com/1870994/235768559-ca8bfa84-21f5-47b6-b2bd-7fcc07cedd92.mp4

#### After loading in napari a sample 3D image of cell nuclei, I ask Omega to segment the nuclei using the Otsu method. My first request was very vague, so it just segmented foreground versus background. I then ask to segment the foreground into distinct segments for each connected component. Omega does a rookie mistake by forgetting to 'import np'. No problem; it notices, tries again, and succeeds:

https://user-images.githubusercontent.com/1870994/235769990-a281a118-1369-47aa-834a-b491f706bd48.mp4

#### In this video, one of my favorites, I ask Omega to make a 'Max color projection widget.' It is not a trivial task, but it manages!

https://github.com/royerlab/napari-chatgpt/assets/1870994/bb9b35a4-d0aa-4f82-9e7c-696ef5859a2f

As LLMs continue to improve, Omega will become even more adept at handling complex
image processing and analysis tasks. The current version of ChatGPT, 3.5,
has a cutoff date of 2021, which means that it lacks nearly two years of knowledge
on the napari API and usage, as well as the latest versions of popular libraries
like scikit-image, OpenCV, numpy, scipy, etc... Despite this, you can see in the
videos below that it is quite capable. While ChatGPT 4.0 is a significant upgrade, it is not
yet widely available.

Omega could eventually help non-experts process and analyze images, especially
in the bioimage domain.
It is also potentially valuable for educative purposes as it could
assist in teaching image processing and analysis, making it more accessible.
Although ChatGPT, which powers Omega, may not be yet on par with an expert image
analyst or computer vision expert, it is just a matter of time...

Omega holds a conversation with the user and uses different tools to answer questions, 
download and operate on images, write widgets for napari, and more.

## Omega's Built-in AI-Augmented Code Editor

The Omega AI-Augmented Code Editor is a new feature within Omega, designed to enhance the Omega's user experience. This editor is not just a text editor; it's a powerful interface that interacts with the Omega dialogue agent to generate, optimize, and manage code for advanced image analysis tasks.

<img src='https://github.com/royerlab/napari-chatgpt/assets/1870994/cf9b1c15-f11a-4e25-a73d-d96915c46c6a' width='800'>

#### Key Features
- **Code Highlighting and Completion**: For ease of reading and writing, the code editor comes with built-in syntax highlighting and intelligent code completion features.
- **LLM-Augmented Tools**: The editor is equipped with AI tools that assist in commenting, cleaning up, fixing, modifying, and performing safety checks on the code.
- **Persistent Code Snippets**: Users can save and manage snippets of code, preserving their work across multiple Napari sessions.
- **Network Code Sharing (Code-Drop)**: Facilitates the sharing of code snippets across the local network, empowering collaborative work and knowledge sharing.

#### Usage Scenarios
- **Widget Creation**: Expert users can create widgets using the Omega dialogue agent and retain them for future use.
- **Collaboration**: Share custom widgets with colleagues or the community, even if they don't have access to an API key.
- **Learning**: New users can learn from the AI-augmented suggestions, improving their coding skills in Python and image analysis workflows.

You can find more information in the corresponding [wiki page](https://github.com/royerlab/napari-chatgpt/wiki/OmegaCodeEditor).

----------------------------------

## Omega's Installation instructions:

Assuming you have a Python environment with a working napari installation, you can simply:

    pip install napari-chatgpt

Or just install the plugin from napari's plugin installer.

For detailed instructions and variations, check [this page](http://github.com/royerlab/napari-chatgpt/wiki/InstallOmega) of our wiki.
    
## Requirements:

You need an OpenAI key; there is no way around this, I have been experimenting with 
other models, including open-source models, but right now, the best results, by far, are obtained with ChatGPT 4 (and to
a lesser extent 3.5). Check [here](https://github.com/royerlab/napari-chatgpt/wiki/OpenAIKey) for details on how to get your OpenAI key. In particular, check [this](https://github.com/royerlab/napari-chatgpt/wiki/AccessToGPT4) for how to gain access to GPT-4 models.

## Usage:

Check this [page](https://github.com/royerlab/napari-chatgpt/wiki/HowToStartOmega) of our [wiki](https://github.com/royerlab/napari-chatgpt/wiki) for details on how to start Omega. 

## Tips, Tricks, and Example prompts:

Check our guide on how to prompt Omega and some examples [here](https://github.com/royerlab/napari-chatgpt/wiki/Tips&Tricks).

## Video Demos:

You can check the original release videos [here](https://github.com/royerlab/napari-chatgpt/wiki/VideoDemos).
You can also find the latest preprint videos on [Vimeo](https://vimeo.com/showcase/10983385).

## How does Omega work?

Check our preprint here: [10.5281/zenodo.8240289](10.5281/zenodo.8240289)
and our [wiki page](https://github.com/royerlab/napari-chatgpt/wiki/OmegaDesign) on Omega's design and architecture.

## Cost:

Developing the initial version of Omega cost me $13.97, hardly a fortune. 
OpenAI [pricing](https://openai.com/pricing) on ChatGPT 4 is very reasonable at 0.01 dollars per 1K tokens, which means $1 per 750000 words. 

Note: you can limit the burn rate to a certain amount of dollars per month, just
in case you let Omega think over the weekend and forget to stop it (don't worry, 
this is actually **not** possible).

## Disclaimer:

Do not use this software lightly; it will download libraries of its own volition
and write any code that it deems necessary; it might actually do what you ask, even
if it is a very bad idea. Also, beware that it might _misunderstand_ what you ask and
then do something bad in ways that elude you. For example, it is unwise to use Omega to delete 
'some' files from your system; it might end up deleting more than that if you are unclear in 
your request.  
Omega is generally safe as long as you do not make dangerous requests. To be 100% safe, and
if your experiments with Omega could be potentially problematic, I recommend using this 
software from within a sandboxed virtual machine.

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A
PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS
BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR
THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contributing

Contributions are extremely welcome. Tests can be run with [tox], please ensure
the coverage at least stays the same before you submit a pull request.

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
