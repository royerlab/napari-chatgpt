# napari-chatgpt, home of _Omega_

[![License BSD-3](https://img.shields.io/pypi/l/napari-chatgpt.svg?color=green)](https://github.com/royerlab/napari-chatgpt/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-chatgpt.svg?color=green)](https://pypi.org/project/napari-chatgpt)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-chatgpt.svg?color=green)](https://python.org)
[![tests](https://github.com/royerlab/napari-chatgpt/workflows/tests/badge.svg)](https://github.com/royerlab/napari-chatgpt/actions)
[![codecov](https://codecov.io/gh/royerlab/napari-chatgpt/branch/main/graph/badge.svg)](https://codecov.io/gh/royerlab/napari-chatgpt)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-chatgpt)](https://napari-hub.org/plugins/napari-chatgpt)

A [napari](napari.org) plugin that levegares Large Language Models like ChatGPT to implement _Omega_ 
a napari-aware agent capable of performing image processing and analysis tasks in a conversational manner.

This repository was created as a 'week-end project' by [Loic A. Royer](https://twitter.com/loicaroyer) 
who leads a [research group](royerlab.org) at the [Chan Zuckerberg Biohub](czbiohub.org/sf/) .
It levegages [OpenAI](openai.com)'s ChatGPT API via the [LangChain](https://python.langchain.com/en/latest/index.html) 
Python library, as well as [napari](napari.org) a fast, interactive, multi-dimensional 
image viewer for Python, [another](https://ilovesymposia.com/2019/10/24/introducing-napari-a-fast-n-dimensional-image-viewer-in-python/) 
of Loic's week-end projects :-).

# What is Omega?

Omega demonstrates the potential for Large Language Models (LLMs) to write image 
processing and analysis code using napari as image viewer. Can LLM-based agents 
write image processing code and napari widgets, correct coding mistakes, perform 
follow-up analysis, and control the napari viewer? The answer appears to be yes.

(Video)

As LLMs continue to improve, Omega will become even more adept at handling complex 
image processing and analysis tasks. The current version of ChatGPT, 3.5, 
has a cutoff date of 2021, which means that it lacks nearly two years of knowledge 
on the napari API and usage, as well as the latest versions of popular libraries 
like scikit-image. Despite this, you can see in the videos below that it is quite capableWhile ChatGPT 4.0 is a significant upgrade, it is not yet widely 
available.

Omega could eventually help non-experts analyse images, especially in the bioimage domain. 
It is also potentially valuable for educative purposes as it could 
assist in teaching image processing and analysis, making it more accessible. 
Although ChatGPT may not be yet on par with an expert image analyst or computer vision 
expert, it is likely just a matter of time...

Omega holds a conversation with the user and uses the following tools to acheive answer questions, 
download and operate on images, write widgets for napari, and more:

### napari related tools:
- napari viewer control: 
    Gives Omega the ability to control all aspects of the viewer.
  
- napari query:
    Gives Omega the ability to query information about the state of the viewer, of its layers, and their contents.

- napari widget maker:
    Gives Omega the ability to make napari functional widgets that take layers as input and return a new layer.

### cell segmentation tools: 
- cell and nuclei segmentation:
    This tool specialises in segmenting cells and nuclei in images using some predefined segmentation algorithms.
    Right now only cellpose is implemented. Experimental, functional, but quite limited. Exists mostly because of
    lack of knowledge of ChatGPT on some of the specilaised bioimaging segmentation tools. 

### Generic python installation queries:
- python function signature query:
    Lets Omega query the signature of function when it is unsure how to call a function and what the names of parameters are.

### web search related tools:
- web search:
    Usefull to give Omega access to the whole knowledge in the webQ

- web image serach:
    Streamlined path to search the web for images and open them in napari  

- wikipedia search:
    Gioves Omega access to teh whole wikipedia

Beware: Omega will install whatever python packages it thinks it needs,
and will write and execute whatever code it deems nescessary to satisfy your requests. 
Do not ask for 'deleting all files on drive', it WILL HAPPILY DO IT.


----------------------------------

## Installation:

You can also install `napari-chatgpt` directly from within napari in the Plugins>Install/Uninstall Plugins menu.
(Please note that the Omega agent will hapilly install packages in the corresponding environment)

Create environment: 

    conda create -y -n napari-chatgpt -c conda-forge python=3.9

Activate environment:

    conda activate napari-chatgpt 


Install napari in the environment using conda-forge: (important on Apple M1/M2)

    conda install -c conda-forge napari     


Install the repo in enbvironment:

    pip install napari-chatgpt

Start napari:

    napari

To install latest development version :

    git clone https://github.com/royerlab/napari-chatgpt.git
    cd napari-chatgpt
    pip install -e .

or:

    pip install git+https://github.com/royerlab/napari-chatgpt.git


## Requirements:

You need an OpenAI key, there is no way around this, unless we add some other,
potentially local LLMs compatible to LangChaim (LLamaCPP is an interesting candidate).
You can get  your key by signing up [here](https://openai.com/blog/openai-api).
Developping Omega cost me 13.97$, a fortune, indeed. OpenAI pricing on ChatGPT 3.5 is very
reasonable at $0.002 / 1K tokens, which means 2$ per 750'000 words. A bargain.
Now, ChatGPT 4.0 is about 10x more expensive... But that could eventually drop, hopefully.


## Disclaimer:

Do not use this software lightly, it will download libaries by its own volition,
write any code that it deems nescessary, it might actually do what you ask, even if
it is a bad idea. Also, beware that it might _misundertand_ what you ask and then do
something bad. For example, it is unwise to use Omega to delete 'some' files from your system,
it might end up deleteing more than that if you are unclear in your request.  
To be 100% safe, we recommend that you use this software from within a sandboxed virtual machine. 

THE SOFTWARE IS PROVIDED “AS IS”, WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, 
INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR 
PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE 
FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, 
TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE 
USE OR OTHER DEALINGS IN THE SOFTWARE.


## Usage:

Here are example prompts/questions/requests to try:

- What is your name?
- What tools do you have available?
- Make me a Gaussian blur widget with sigma parameter
- Open this tiff file in napari: https://people.math.sc.edu/Burkardt/data/tif/at3_1m4_03.tif
- Make a widget that applies the transformation: y = x^alpha + y^beta with alpha and beta two parameters.
- Create a widget to multiply two images
- Can you open in napari a photo of Albert Einstein?
- Downscale by a factor 3x the image on layer named 'img'
- Rename selected layer to 'downscaled_image'
- Upscale image 'downscaled_image' by a factor 3 using some smart interpolation scheme of your choice (not nearest-neighboor)
- Caveat: makes a plugin instead of actually doing teh job
- How many channels has the image on layer 0
- Make a image sharpening filter widget, expose relevant parameters
- Can you open this file in napari: https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr
- Split the two channels of the first layer (first axis) into two separate layers
- Switch viewer to 3d
- Create a napari widget for a function that takes two image layers and returns a 3D image stack of n images where each 2D image corresponds to a linear blending of the two layer images between 0 and 1.
- [Loaded the ‘cell’ sample image] there is one cell in the image on the first layer, it is roughly circular and brighter than its surroundings, ca you write segmentation code that returns a labels layer for it?
- Can you create a widget to blend two images?
- Can you tell me more about the 'guided Canny edge filter' ?
- Write a configurable RGB to grayscale widget, ensure weights sum to 1

## Video Demos:

(all videos)


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
