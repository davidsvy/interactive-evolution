<h1 align="center">
  <b>Interactive Evolution</b><br>
</h1>

<p align="center">
      <a href="https://www.python.org/">
        <img src="https://img.shields.io/badge/python-3.7-blue.svg" /></a>
       <a href= "https://pytorch.org/">
        <img src="https://img.shields.io/badge/PyTorch-1.9-FF0000.svg" /></a>
       <a href= "https://github.com/davidsvy/interactive-evolution/blob/main/LICENSE">
        <img src="https://img.shields.io/badge/license-MIT-white.svg" /></a>
</p>

An unofficial PyTorch implementation of the paper [Deep Interactive Evolution](https://arxiv.org/pdf/1801.08230.pdf).



<p align="center">
  <image src="assets/algorithm.png" />
  Image stolen from the paper.
</p>




Table of contents
===

<!--ts-->
  * [➤ Paper Summary](#paper-summary)
    * [➤ GAN](#gan)
    * [➤ GUI](#gui)
  * [➤ Installation](#installation)
  * [➤ Usage](#usage)
  * [➤ Citations](#citations)
<!--te-->


<a  id="paper-summary"></a>
Paper Summary
===

This paper combines generative adversarial networks with interactive evolutionary computation. Specifically,
instead of randomly sampling from gans, a user can guide the generation by selecting images with desired traits using an interactive gui.

<a  id="gan"></a>
GAN
---
The author of this repo does not possess the hardware, the time, the patience or the skills necessary to train gans. Threfore, the pretrained models from [Facebook's GAN zoo](https://github.com/facebookresearch/pytorch_GAN_zoo) are employed.



<a  id="gui"></a>
GUI
---
Whereas the authors of the paper developed a web interface to display images, the author of this repo possesses zero web development skills and therefore makes due with a makeshift [tkinter](https://docs.python.org/3/library/tkinter.html) gui.



<a  id="installation"></a>
Installation
===
```
$ git clone https://github.com/davidsvy/interactive-evolution
$ cd interactive-evolution
$ pip install -r requirements.txt
```



<a  id="usage"></a>
Usage
===

```
$ python run.py [-c configs/config.yaml]
```

<a  id="citations"></a>
Citations
===

```bibtex
@misc{bontrager2018deep,
      title={Deep Interactive Evolution}, 
      author={Philip Bontrager and Wending Lin and Julian Togelius and Sebastian Risi},
      year={2018},
      eprint={1801.08230},
      archivePrefix={arXiv},
      primaryClass={cs.NE}
}
}
```

