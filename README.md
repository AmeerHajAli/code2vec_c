# C Extractor for code2vec

This package is a proof of concept that implements code2vec functionality for files written in the popular programming 
language C.  This package is not stand alone and requires [code2vec](https://github.com/tech-srl/code2vec),
which in this documentation will be referenced as base code2vec, to provide complete source to model functionality.

Questions and comments about this package should be directed to: info@sei.cmu.edu

# Table of Contents
 - [Requirements](#requirements)
 - [Configuration](#configuration)
 - [Quickstart](#quickstart)
 - [Contents](#Contents)
 - [Differences](#Differences)

# Requirements
 - Everything required for code2vec. https://github.com/tech-srl/code2vec#requirements   
 - python required for cindex python bindings.
```
python --version
```
 - llvm / clang / cindex v6
   * If you are on Ubuntu, or similar linux, the packages `clang` and `libclang-dev` will install the necessary components
   * If you are on Windows you will need to download clang v6 from the [download page](http://releases.llvm.org/) and install the python package cindex
   * This package uses both command line clang and cindex python bindings so clang will need to be in the path of the user executing code2vec-c scripts.
 ```
 clang -v
 python -c"import clang.cindex; import inspect; print(inspect.getfile(clang.cindex))"
 ```
- awk and curl are used in some of our optional instructions
```
awk --version; curl --version
```

# Quickstart

## Step 0: Get the source
The code2vec-c and code2vec packages should be cloned or downloaded from the appropriate repositories.  For ease of use
we suggest these projects be placed either side by side or code2vec-c inside of base code2vec.

## Step 1: Configuration
Configure code2vec-c by changing the [configuration](#configuration) parameters in `configure.sh`

## Step 2: Create a dataset from sources
We have provided a sample extraction process on the top 1000 (ish) starred projects from GitHub to create a C model.
The instructions for this process are [here](git.md).  If not using our process ensure the `SOURCE_DIR` paramter points to
a directory that contains C source files and execute the script `preprocecss.sh`.

## Step 3: Training a model
With the dataset created in [Step 2](#Step-2) a model can be trained using the [base code2vec training method.](https://github.com/tech-srl/code2vec#training-a-model-from-scratch).  For this step work should be performed in the base code2vec directory.

## Step 4: Evaluating a trained model
A model can be evaluated against the test training set with the [same method used in base code2vec.](https://github.com/tech-srl/code2vec#step-3-evaluating-a-trained-model).  For this step work should be performed in the base code2vec directory.

## Step 5: Manual examination of a trained model
In base code2vec an interactive prediction can be performed against a given model by providing the parameter --predict.  
This does not work with C code and models because there is no framework to hook into --predict to instruct code2vec to use the C extractor and not the Java extractor.  To remedy this we have modifed the associated code from code2vec to provide a similar
interactive predictor for C code that is located in in the subdirectory `interactive`.  To use the interactive predictor 
execute `interactive/predict.sh` to begin an interactive prediction session.  The file the perdictor will parse is `interactive/input.c`.

# Configuration - `configure.sh`
The file `configure.sh` in the root of the distribution contains the configuration parameters that can be set in 
code2vec-c and all of the configuration parameters that can be set in base code2vec.  At a minimum CLANG_PATH,CODE2VEC_LOC,SOURCE_DIR, and DATASET_NAME should be configured to locations specific to your environment.  If more system resources are available
MEM_PERCENT and NUM_PROCESSORS shoud be increased accordingly.

To ensure that settings are universal within our package this configuration is sourced by all other scripts.  These parameters are only used within the code2vec-c files so any changes made here also need to be made in the associated base code2vec files.

The attributes that have been added with the C implementation of code2vec are:

- CLANG_PATH - should be set to the path to lib clang
- CODE2VEC_LOC - should be the path to base codevec
- SOURCE_DIR - path where the c source files reside
- MAX_LEAVES - maximum number of leaf nodes in an AST (default 32, remember function complexity is ~ leaves^2)
- SKIP_DECLS - whether to skip or tag function declarations
- DOWNSAMPLE - the percentage of total features to use for model training.  
- DATASET_NAME - dataset name to use (This should be same as the name used in base code2vec)
- MEM_PERCENT - for configurable commands like sort limit set the percent of memory to use
- NUM_PROCESSORS - for configurable commands like sort set the number of processors to use

# Contents
code2vec-c is an extension of the code2vec package that provides methods that work with C source files.
Most of the scripts are complex and require many input parameters so to simplify usage the parameters 
have been abstracted out into a [configuration script](#configuration).  The main drivers of the C functionality
are two scripts `preprocess.sh` which produces files in the c2v format that code2vec can use to train a model and 
`interactive\predict.sh` which invokes the interactive predictor to evaluate code against a working model.  The main functionality 
is provided by python scripts that are invoked from these above shell scripts.   Below is a brief description of each file 
in the code2vec-c repo:

- `preprocess.sh` - Shell script that will take a directory structure of source files and convert them into a set of c2v
files in a format code2vec can use.  This process differs from base code2vec in that we collect all of the source 
files into a single randomly shuffled feature file and then extract the training, validation, and test datasets from this
randomly shuffled feature file.
- `interactive\predict.sh` - Shell script that will invoke the interactive prediction capability of code2vec-c
- `extract-c.py` - An extraction file similar to the base code2vec file for spidering a directory and extracting features.
- `cparser.py` - The primary parsing script that will manage includes, find c source files, parse files and create output.   
- `astnode.py` - A python scrip that contains an object that provides convenience functions and caching for a Clang AST.
- `interactive\invoke_predictor.py` - python script with code related to prediction extracted from base code2vec's code2vec.py
- `interactive\interactive_predictor.py` - python script copied from the java interactive predictor and modified to work with C code.
- `interactive\extractor_c.py`- copied and modified code2vec code that implements an Extractor object that works C code.
- `test\*` - set of tests that ensures that known inputs create expected outputs.

# Differences
There are a few differences between the C parser and associated scripts and the Java parser and base code2vec.
These are enumerated below with brief descriptions.

- max leaf nodes - Base code2vec limits what it will parse using depth and width parameters.  The C parser uses 
a simpler maximum leaf node metric beyond which it will skip a function.
- function declarations - C has function declarations and Java does not.  The C parser has a parameter that can be set
that determines whether to tag or discard function declarations when they are encountered. 
- child node numbering - When constructing code paths, the Java parser numbers child nodes and includes this information in
the generated code paths.  The C parser does not do this. 
- hash codes - The Java parser produces Java style hash codes.  The C parser uses a sha256 hash code.
- leaf nodes - The Java parser is very aggressive and only leaves alphabetic characters in leaf nodes.  The C parser is more 
permissive and will only filter out symbols, some of which will break file formats.
- unique shuffed bags - base code2vec assigns bags of path contexts to a dataset (test, val, train) based on the directory 
the file they are contained in.  The C parser collects all bags of path contexts into a single unique list, shuffles
the list, and then samples the datasets (test, val, train) from the shuffled list.

Note: Because of the differences between our implementation and base code2vec (down sampling, max leaf nodes, unique path contexts) our
implementation may entirely filter out or result in fewer path contexts in the bag of path contexts for a given file compared to base code2vec.

# Document markings
```
# C extractor for code2vec
#
# Copyright 2019 Carnegie Mellon University. All Rights Reserved.
#
# NO WARRANTY. THIS CARNEGIE MELLON UNIVERSITY AND SOFTWARE ENGINEERING INSTITUTE MATERIAL IS FURNISHED ON AN "AS-IS" BASIS. CARNEGIE MELLON UNIVERSITY MAKES NO WARRANTIES OF ANY KIND, EITHER EXPRESSED OR IMPLIED, AS TO ANY MATTER INCLUDING, BUT NOT LIMITED TO, WARRANTY OF FITNESS FOR PURPOSE OR MERCHANTABILITY, EXCLUSIVITY, OR RESULTS OBTAINED FROM USE OF THE MATERIAL. CARNEGIE MELLON UNIVERSITY DOES NOT MAKE ANY WARRANTY OF ANY KIND WITH RESPECT TO FREEDOM FROM PATENT, TRADEMARK, OR COPYRIGHT INFRINGEMENT.
# Released under a MIT (SEI)-style license, please see license.txt or contact permission@sei.cmu.edu for full terms.
# [DISTRIBUTION STATEMENT A] This material has been approved for public release and unlimited distribution.  Please see Copyright notice for non-US Government use and distribution.
# Carnegie Mellon® and CERT® are registered in the U.S. Patent and Trademark Office by Carnegie Mellon University.
# This Software includes and/or makes use of the following Third-Party Software subject to its own license:
# 1. code2vec (https://github.com/tech-srl/code2vec/blob/master/LICENSE) Copyright 2018 Technion.
# 2. LLVM / CLANG (https://github.com/llvm-mirror/clang/blob/master/LICENSE.TXT) Copyright 2019 LLVM.
# DM19-0540
```
