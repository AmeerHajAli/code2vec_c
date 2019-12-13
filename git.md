# Generating a C code2vec Model from GitHub
This walkthrough will generate a code2vec model from a dataset that is 
comprised of the top 1000 starred repos on github.  This process has been executed on 
Ubuntu 18.04.2 LTS using clang version 6 but it should work on any system that has the following installed:

- Clang v6
- Bash
- Python
- code2vec
- awk, curl

The machine used for our training was a 12 processor, 4 GPU machine with 126GB of memory and 20TB of disk space.  
On it this process can be completed from start to a trained model in a couple days.

### Step 1: Download all of the GitHub repos
This shell command will get the top 1000 starred repo URLs from GitHub and write them to the file repos.txt.
**This is very fragile and prone to break because it makes assumptions about the format of output from github API.**
```
for i in {1..10}; do curl "https://api.github.com/search/repositories?fields=html_url&q=language:C&sort=stars&order=desc&per_page=100&page=$i" | grep html_url | awk 'NR % 2 == 0' | awk 'BEGIN{FS="\""}{print $4}' >> repos.txt; done
```
With this file all of the repos can be cloned from github using this command.  Because the configuration 
of the package makes external calls we remove the project netmap if it is present.  In addition, linux
is a huge project that creates almost twice as many features as everything else.  If you would like
to work with a smaller dataset removing linux would be a good place to start.
```
cat repos.txt | xargs -l git clone
# (optional) Netmap configure makes external calls remove it if it is present.
rm -rf netmap
# (optional) Linux is very large and can overwhelm results
rm -rf linux
```

### Step 1.5: (Optional) Configure C packages
You can choose to configure the packages downloaded from GitHub.  This will improve the accuracy of the
model produced as it will create some missing header files and improve the pre-processing of files.  If you
are just exploring this package you can skip this step.  If you are looking for a better model 
we recomend at least configuring linux(if not deleted), gcc, and glibc.  And for the most accurate model configure everything.
The steps for linux and a generic configuration one liner that will configure all packages are below.  

#### Configure Linux
Linux needs a few tools that are not installed by default on linux systems like flex and bison.  These will need to be installed 
using apt-get or appropriate tool on your system.  I suggest repeatedly trying to configure linux and installing any needed tools until
the configuration succeeds.  A simple command to configure linux would be:
```
yes "" | make oldconfig
```

#### Bulk configure
A number of the packages downloaded from github can be configured using typical commands and minimal additional software packages.
A simple command that can be run from your git download directory and will attempt to configure each package is below.  
This will **not** succeed in configuring all packages but will configure a large portion of them. 

**Do not run this as a privileged user as some scripts do compilation and other unknown tasks**
```
for dir in *; do (cd "$dir" && ./configure || ./config || yes "" | make oldconfig  || make config || make includes); done
```

### Step 2: Generate features
Now that the GitHub repos are downloaded, staged, and optionally configured the rest of this process 
will be similar to the process for default code2vec.  The first step is to extract features from the GitHub packages and 
stage them in a format code2vec recognizes for model training.   The code2vec-c shell script `preprocess.sh` will do this for
you.  This script does the following:

- Extract features from the GitHub repos into the appropriate train,test,validation data files located in a data 
folder under the code2vec directory.
- Aggregate the features into histogram files in the data folder.  Code2vec uses these files as hints when sampling.
- Execute the base code2vec file `preprocess.py` that samples the files into c2v files suitable for training.

To execute this script edit `configure.sh` and customize any parameters to your environment then invoke `preprocess.py`.  As a warning this file could take day(s) to week(s) to run depending on the number of leaf nodes used, the processing power available, and the size of packages being extracted.  The default value of 32 leaf nodes is a good starting point but will exclude a lot of functions, a value of 320 will get most functions but will need a lot of disk space and processing time.  

### Step 3: Train a model
The dataset produced by the previous steps is now in format that code2vec can work with.  You can skip to the section
"Step 2: Training a model" of the [code2vec-c documentation](README.md#step-3-training-a-model)
and follow those instructions to train a working model.


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
