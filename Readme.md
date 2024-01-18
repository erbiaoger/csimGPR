<h1 align="center">
  <img src="https://raw.githubusercontent.com/erbiaoger/PicGo/main/20230608202306091328187.png" alt="csimGPR" width="600">
      <br>csimGPR<br>
</h1>


<h4 align="center">csimGPR Moon and Mars subsurface structure interpretation software.</h4>

<p align="center">
  <a href="https://github.com/erbiaoger/csimGPR/actions">
    <img src="https://img.shields.io/github/actions/workflow/status/erbiaoger/csimGPR/release.yml?branch=master&style=flat-square" alt="Github Actions">
  </a>
  <a href="https://goreportcard.com/report/github.com/erbiaoger/csimGPR">
    <img src="https://goreportcard.com/badge/github.com/erbiaoger/csimGPR?style=flat-square">
  </a>
  <img src="https://img.shields.io/github/go-mod/go-version/erbiaoger/csimGPR?style=flat-square">
  <a href="https://github.com/erbiaoger/csimGPR/releases">
    <img src="https://img.shields.io/github/release/erbiaoger/csimGPR/all.svg?style=flat-square">
  </a>
  <a href="https://github.com/erbiaoger/csimGPR/releases/tag/premium">
    <img src="https://img.shields.io/badge/release-Premium-00b4f0?style=flat-square">
  </a>
</p>

[English](https://github.com/erbiaoger/csimGPR/blob/main/Readme.md)  |  [中文](https://github.com/erbiaoger/csimGPR/blob/main/Readme_cn.md)

![image-20230811113814945](https://raw.githubusercontent.com/erbiaoger/PicGo/main/image-20230811113814945.png)



## Installation

### Step0: clone this repository

```bash
git clone https://github.com/erbiaoger/csimGPR.git
```

### Step1: Make Environment

You can install csimGPR via pip, conda, or Docker(explanation below).

```bash
conda create -n csimGPR python=3.10
conda activate csimGPR
```

OR

```cmd
python -m venv .venv
# Windows
.\.venv\Scripts\activate
# Linux
source .venv/bin/activate
```

### Step2: Install Migration


```bash
python3 installMigration.py
```

details: https://github.com/AlainPlattner/irlib

### Step3: Install csimGPR

#### For User

Install csimGPR

```bash
pip install -r requirements.txt
```

```bash
pip install -e .
```

## Quick Start

```bash
csimGPR
```

![start](https://raw.githubusercontent.com/erbiaoger/PicGo/31dd23b5477dad6cb993387b76c10f0e393d513f/2023-11-25Untitled%20%E2%80%91%20Made%20with%20FlexClip%20(1).gif)


## Usage Example

You can try csimGPR in [`examples`](examples/examplescripts) directory.


