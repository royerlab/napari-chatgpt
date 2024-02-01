# napari-chatgpt

## Home of
_Omega_, a napari-aware autonomous LLM-based agent specialised in image processing and analysis.

[![License BSD-3](https://img.shields.io/pypi/l/napari-chatgpt.svg?color=green)](https://github.com/royerlab/napari-chatgpt/raw/main/LICENSE)
[![PyPI](https://img.shields.io/pypi/v/napari-chatgpt.svg?color=green)](https://pypi.org/project/napari-chatgpt)
[![Python Version](https://img.shields.io/pypi/pyversions/napari-chatgpt.svg?color=green)](https://python.org)
[![tests](https://github.com/royerlab/napari-chatgpt/workflows/tests/badge.svg)](https://github.com/royerlab/napari-chatgpt/actions)
[![codecov](https://codecov.io/gh/royerlab/napari-chatgpt/branch/main/graph/badge.svg)](https://codecov.io/gh/royerlab/napari-chatgpt)
[![napari hub](https://img.shields.io/endpoint?url=https://api.napari-hub.org/shields/napari-chatgpt)](https://napari-hub.org/plugins/napari-chatgpt)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.8240289.svg)](https://doi.org/10.5281/zenodo.8240289)


A [napari](napari.org) plugin that leverages OpenAI's Large Language Model
ChatGPT to implement _Omega_
a napari-aware agent capable of performing image processing and analysis tasks
in a conversational manner.

This repository was created as a 'week-end project'
by [Loic A. Royer](https://twitter.com/loicaroyer)
who leads a [research group](https://royerlab.org) at
the [Chan Zuckerberg Biohub](https://czbiohub.org/sf/). It
levegages [OpenAI](https://openai.com)'s ChatGPT API via
the [LangChain](https://python.langchain.com/en/latest/index.html) Python
library, as well as [napari](https://napari.org), a fast, interactive,
multi-dimensional
image viewer for
Python, [another](https://ilovesymposia.com/2019/10/24/introducing-napari-a-fast-n-dimensional-image-viewer-in-python/)
of Loic's week-end projects.

# What is Omega?

Omega is a LLM-based and tool-armed autonomous agent that demonstrates the
potential for Large Language Models (LLMs) to be applied to image processing,
analysis and visualisation.
Can LLM-based agents write image processing code and napari widgets, correct its
coding mistakes, perform follow-up analysis, and control the napari viewer? 
The answer appears to be yes.

The preprint can be downloaded here: [10.5281/zenodo.8240289](10.5281/zenodo.8240289)


#### In this video I ask Omega to segment an image using the [SLIC](https://www.iro.umontreal.ca/~mignotte/IFT6150/Articles/SLIC_Superpixels.pdf) algorithm. It makes a first attempt using the implementation in scikit-image, but fails because of an inexistant 'multichannel' parameter. Realising that, Omega tries again, and this time, succeeds:

https://user-images.githubusercontent.com/1870994/235768559-ca8bfa84-21f5-47b6-b2bd-7fcc07cedd92.mp4

#### After loading in napari a sample 3D image of cell nuclei, I ask Omega to segment the nuclei using the Otsu method. My first request was very vague, so it just segmented foreground versus background. I then ask to segment the foreground into distinct segments for each connected component. Omega does a rookie mistake by forgetting to 'import np'. No problem, it notices, tries again, and succeeds:

https://user-images.githubusercontent.com/1870994/235769990-a281a118-1369-47aa-834a-b491f706bd48.mp4

As LLMs continue to improve, Omega will become even more adept at handling
complex
image processing and analysis tasks. The current version of ChatGPT, 3.5,
has a cutoff date of 2021, which means that it lacks nearly two years of
knowledge
on the napari API and usage, as well as the latest versions of popular libraries
like scikit-image, OpenCV, numpy, scipy, etc... Despite this, you can see in the
videos below
that it is quite capable. While ChatGPT 4.0 is a significant upgrade, it is not
yet widely
available.

Omega could eventually help non-experts process and analyze images, especially
in the bioimage domain.
It is also potentially valuable for educative purposes as it could
assist in teaching image processing and analysis, making it more accessible.
Although ChatGPT, which powers Omega, may not be yet on par with an expert image
analyst or computer vision
expert, it is just a matter of time...

Omega holds a conversation with the user and uses the following tools to achieve
answer questions,
download and operate on images, write widgets for napari, and more:

### napari related tools:

- napari viewer control:
  Gives Omega the ability to control all aspects of the napari viewer.

- napari query:
  Gives Omega the ability to query information about the state of the viewer, of
  its layer, and their contents.

- napari widget maker:
  Gives Omega the ability to make napari functional widgets that take layers as
  input and return a new layer.

### cell segmentation tools:

- cell and nuclei segmentation:
  This tool specializes in segmenting cells and nuclei in images using some
  predefined segmentation algorithms. Right no,w only cellpose is implemented.

### Generic Python installation queries:

- python function signature query:
  Lets Omega query the signature of a function when it is unsure how to call a
  function and what the names and type of the parameters are.

### web search-related tools:

- web search:
  Usefull to give Omega access to the knowledge accessible through the web

- web image search:
  Streamlined path to search the web for images and open them in napari

- Wikipedia search:
  Gives Omega access to the whole Wikipediaa

----------------------------------

## Installation from within napari:

You can install `napari-chatgpt` directly from within napari in the Plugins>
Install/Uninstall Plugins menu.
(Please note that the Omega agent will happily install packages in the
corresponding environment).

IMPORTANT NOTE: Make sure you have a recent version of napari! Ideally, the
latest one!

## Installation in a new conda environment (RECOMMENDED):

Make sure you have an [miniconda](https://docs.conda.io/en/latest/miniconda.html) installation on your system.
Ask [ChatGPT](https://chat.openai.com/auth/login) what that is all about if you are unsure ;-)

Create environment:

    conda create -y -n napari-chatgpt -c conda-forge python=3.9

Activate environment:

    conda activate napari-chatgpt 

Install [napari](napari.org) in the environment using conda-forge: (very important on Apple M1/M2)

    conda install -c conda-forge napari pyqt

**Or**, with pip (linux, windows, or Intel Macs, not recommended on Apple M1/M2!):

    pip install napari

Install napari-chatgpt in the environment:

    pip install napari-chatgpt

## Installation variations:

To install the latest development version (not recommended for end-users):

    conda create -y -n napari-chatgpt -c conda-forge python=3.9
    conda activate napari-chatgpt
    pip install napari  
    git clone https://github.com/royerlab/napari-chatgpt.git
    cd napari-chatgpt
    pip install -e .
    pip install -e ".[testing]"

or:
    
    # same steps as above and then:
    pip install git+https://github.com/royerlab/napari-chatgpt.git

## System-specific tweaks:

On Ubuntu systems, I recommend setting changing the UI timeout, 
otherwise, whenever Omega is thinking, the UI will freeze, and a popup will block
everything which is very annoying:

    gsettings set org.gnome.mutter check-alive-timeout 60000
    


## Requirements:

You need an OpenAI key; there is no way around this, I have been experimenting with 
other models, but right now, the best results, by far, are obtained with ChatGPT 4 (and to
a lesser extent 3.5). You can get your OpenAI key by signing up [here](https://openai.com/blog/openai-api).
Developing Omega cost me $13.97, hardly a fortune. OpenAI pricing on ChatGPT 3.5
is very reasonable at 0.002 dollars per 1K tokens, which means $2 per 750000 words. A
bargain. Now, ChatGPT 4.0 is about 10x more expensive... But that could eventually drop,
hopefully.

Note: you can limit the burn rate to a certain amount of dollars per month, just
in case you let Omega think over the weekend and forget to stop it (don't worry, 
this is actually **not** possible).

## Usage:

Once all is installed, and if it is not already running, start napari:

    napari

You can then the Omega napari plugin via the plugins menu:

<img width="498" alt="image" src="https://user-images.githubusercontent.com/1870994/235790134-1d87fd50-583f-4fd9-ade2-c64497b91331.png">


You just opened the plugin as a widget, this widget will appear:

<img width="267" alt="image" src="https://github.com/royerlab/napari-chatgpt/assets/1870994/fdbde938-548d-4104-9241-d87c46c76dcf">

I recommend that initially, you stick to the default values, which work well.
The best memory is 'hybrid'.
The 'auto-fix' features only make sense if you are choosing a ChatGPT 4 model, 
ChatGPT might get confused... 
Increasing creativity also decreases 'attention to detail'; the models will make more
coding mistakes, but might try more original solutions...

You then need to start Omega:

<img width="104" alt="image" src="https://user-images.githubusercontent.com/1870994/235811111-9e468785-9562-410a-8e9a-c63cb03fb765.png">


If you have not set the 'OPENAI_API_KEY' environment variable as is typically
done, Omega will ask you for your OpenAI API key and will store it _safely_ in an
_encrypted_ way on your machine (~/.omega_api_keys/OpenAI.json):

<img width="293" alt="image" src="https://user-images.githubusercontent.com/1870994/235793528-9e892c5e-d8ca-43e1-9020-f2dfab45b32d.png">


Just enter an encryption/decryption key, your OpenAI key, and
everytime you start Omega, it will just ask for the decryption key:

<img width="300" alt="image" src="https://user-images.githubusercontent.com/1870994/235794262-4c0eff4d-1c81-47b0-a097-f34e3d5c93b8.png">

(The idea is that you might not be able to remember your OpenAI key by heart, obviously,
but you might be able to do so with your own password or passphrase)

You can then direct your browser
to: [http://127.0.0.1:9000/](http://127.0.0.1:9000/)
and start having a hopefully nice chat with Omega:

<img width="631" alt="image" src="https://github.com/royerlab/napari-chatgpt/assets/1870994/a5cf6d4d-deea-4df8-be8a-601d1cc0424c">


## Example prompts:

Here are example prompts/questions/requests to try:

- What is your name?
- What tools do you have available?
- Make me a Gaussian blur widget with sigma parameter
- Open this tiff file in
  napari: https://people.math.sc.edu/Burkardt/data/tif/at3_1m4_03.tif
- Make a widget that applies the transformation: y = x^alpha + y^beta with alpha
  and beta two parameters.
- Create a widget to multiply two images
- Can you open in napari a photo of Albert Einstein?
- Downscale by a factor 3x the image on layer named 'img'
- Rename selected layer to 'downscaled_image'
- Upscale image 'downscaled_image' by a factor 3 using some smart interpolation
  scheme of your choice (not nearest-neighbor)
- Caveat: makes a plugin instead of actually doing teh job
- How many channels has the image on layer 0
- Make a image sharpening filter widget, expose relevant parameters
- Can you open this file in
  napari: https://uk1s3.embassy.ebi.ac.uk/idr/zarr/v0.4/idr0062A/6001240.zarr
- Split the two channels of the first layer (first axis) into two separate
  layers
- Switch viewer to 3d
- Create a napari widget for a function that takes two image layers and returns
  a 3D image stack of n images where each 2D image corresponds to a linear
  blending of the two layer images between 0 and 1.
- Loaded the ‘cell’ sample image. there is one cell in the image on the first
  layer, it is roughly circular and brighter than its surroundings, ca you write
  segmentation code that returns a labels layer for it?
- Can you create a widget to blend two images?
- Can you tell me more about the 'guided Canny edge filter' ?
- Write a configurable RGB to grayscale widget, ensure weights sum to 1

## Video Demos:

Not everyone will want, or can, get an API key for the latest and best LLM
models,
so here are videos showcasing what's possible. You will notice that Omega
sometimes
fails on its first attempt, typically because of mistaken parameters for
functions,
or other syntax errors. But it also often recovers by having access to the error
message,
and reasoning its way to the right piece of code. The videos below were made with ChatGPT 3.5,
version 4 works much better imagine what will be possible with future even more capable models...

##

In this first video, I ask Omega to make a napari widget to convert images from
RGB to grayscale:

https://user-images.githubusercontent.com/1870994/235769895-23cfc7ed-622a-47f9-95aa-4be77efc0f78.mp4

##

Of course Omega is capable of holding a conversation, it sort of knows 'who it
is', can search the web
and wikipedia. Eventually I imagine it could leverage the ability to search for
improving its responses,
and I have seen doing it a few times:

https://user-images.githubusercontent.com/1870994/235769920-86b02d9d-1196-4339-a8d9-9a028bcd4607.mp4

##

Following-up from the previous video, I ask Omega to create a new labels layer
containing just the largest segment. The script that Omega writes as another
rookie mistake: it confuses layers and images. The error message then confuses
Omega into thinking that it got the name of the layer wrong, setting it off in a
quest
to find the name of the labels layer. It succeeds at writing code that searches
for the labels layer, and uses that name to write a script that then does
extract the largest segment into its own layer. Not bad:

https://user-images.githubusercontent.com/1870994/235770741-d8905afd-0a9b-4eb7-a075-481979ab7b01.mp4

##

In this video, I ask Omega to write a 'segmentation widget'. Pretty unspecific.
The answer is a vanilla yet effective widget that uses the Otsu approach to
threshold the image and then finds the connected components.
Note that when you ask Omega to make a widget, it won't know of any runtime
issues with the code because
it is not running the code itself, yet. It can tell if there is a syntax problem
though... Nevertheless, the widget ends up working just fine:

https://user-images.githubusercontent.com/1870994/235770794-90091bfe-b546-4dd0-bd9c-3895bfc33a1d.mp4

##

Now it gets more interesting. Following up on the previous video, can we ask
Omega to do some follow-
up analysis on the segments themselves? I ask Omega to list the 10 largest
segments and compute their
areas and centroids. No problem:

https://user-images.githubusercontent.com/1870994/235770828-0f829f76-1f3d-44b8-b8e8-89fcbcde6e11.mp4

Note: You could even ask for it in markdown format, which would look better (not
shown here).

##

Next I ask Omega to make a widget that lets me filter segments by area. And it
works beautifully.
Arguably it is not rocket science, but the thought-to-widget time ratio must be
in the hundreds when comparing Omega to an average user trying to write their
own widget:

https://user-images.githubusercontent.com/1870994/235770860-4287e6a3-dae3-4c6d-a588-dea2bb1f69b7.mp4

##

This is an example of a failed widget. I ask for a widget that can do dilations
and erosions. The widget
is created but is 'broken' because Omega made the mistake of using floats for
the number of dilations
and erosions: (In the next video I tell Omega to fix it)

https://user-images.githubusercontent.com/1870994/235770896-819f394d-9785-46e8-a31a-a135b19316bf.mp4

##

Following up from previous video, I explain that I want the two parameters (
number erosions and dilations)
to be integers. Notice that I exploit the conversational nature of the agent by
assuming that it remembers
what the widget is about:

https://user-images.githubusercontent.com/1870994/235770914-90991ac4-337e-4dcd-a04c-dd44b5e8be3e.mp4

##

This video demos a specialised 'cell and nuclei segmentation tool' which
leverages [cellpose 2.0](https://www.cellpose.org/) to segment cell cytoplasms
or nuclei. In general, we can't assume that
LLMs know about every single image processing library, especially for specific
domains. So it can be
a good strategy to provide such specialised tools. After Omega successfully
segments the nuclei, I ask
from it to count the nuclei. Answer: 340. Notice that the code generated '
searches' the layer with name 'segmented' with a loop. Cute:

https://user-images.githubusercontent.com/1870994/235770933-07f5cbe6-2224-4dcd-b378-e81cc4e66500.mov

##

Enough with cells. Aparently The 'memory' of ChatGPT is filled with unescessary
information, it knows the url of Albert Einstein's photo on wikipedia, and
combined with the 'napari file open' tool it can therefore open that photo in
napari:

https://user-images.githubusercontent.com/1870994/235770959-406e8173-8416-4100-bcb6-7f0b617ce234.mp4

##  

You can ask for rather incongruous widgets, widgets you would probably never
write because you just need them once or something. Here I ask for a widget that
applies a rather odd non-linear transformation to each
pixel. The result is predictably boring, but it works, and I don't think that
the answer was 'copy pasted'
from somewhere else...

https://user-images.githubusercontent.com/1870994/235770984-c88c8eac-d3b2-47d7-81b1-48fbe4429e90.mp4

##

In this one, starting again from our beloved Albert, I ask to rename that layer
to 'Einstein' which looks
better than just 'array'. Then I ask Omega to apply a Canny edge filter.
Predictably it uses scikit-image:

https://user-images.githubusercontent.com/1870994/235771000-89dba0db-e710-4f76-b271-e9dcf65239b1.mp4

##  

Then I ask for a 'Canny edge detection widget'. It happily makes the widget and
offers relevant parameters:

https://user-images.githubusercontent.com/1870994/235771031-d978b652-2e28-4178-aa7e-dbdfd2e21c2d.mp4

##

Following up on previous video, I play with dilations on the edge image.
Omega has some trouble when I ask to 'do it again'. Fine, sometimes you have a
bit more explicit:

https://user-images.githubusercontent.com/1870994/235771066-adc7f0bb-0b8e-415c-8e89-6107182cd5b1.mp4

##

You can also experiment with more classic 'numpy' code by creating and
manipulating arrays and visualising
the output live:

https://user-images.githubusercontent.com/1870994/235771093-85a751c8-cc5a-4685-b40a-acdf81f0e5c9.mp4

##

This video demonstrates that Omega understand many aspects of the napari viewer
API. It can switch viewing modes, translate layers, etc... :

https://user-images.githubusercontent.com/1870994/235771129-db095c1f-56f7-4bb9-9bff-ef57ce66387b.mp4

##

I never thought this one would work: I ask Omega to open in napari a mp4 video
from a URL and then use OpenCV to detect people. It does it. But the one thing
that Omega does not know is that creating a layer for each frame of the video is
not a practical approach. Not clear what happened to the colors though. Probably
an RGB ordering or format issue:

https://user-images.githubusercontent.com/1870994/235771146-ced45353-4886-42cb-b48f-3ce0859ed434.mp4

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
