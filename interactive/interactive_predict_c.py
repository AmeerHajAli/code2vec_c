# coding=utf-8
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
import traceback
import hashlib
import os
from extractor_c import CExtractor

# This is in base code2vec
from common import common

SHOW_TOP_CONTEXTS = 10
MAX_LEAF_NODES = 320

class InteractivePredictor:
    exit_keywords = ['exit', 'quit', 'q']

    def __init__(self, config, model):
        model.predict([])
        self.model = model
        self.config = config
        self.path_extractor = CExtractor(config,
                                        clang_path=os.environ['CLANG_PATH'],
                                        max_leaves=MAX_LEAF_NODES)

    def read_file(self, input_filename):
        with open(input_filename, 'r') as file:
            return file.readlines()

    def predict(self):
        input_filename = 'input.c'
        print('Starting interactive prediction...')
        while True:
            print(
                'Modify the file: "%s" and press any key when ready, or "q" / "quit" / "exit" to exit' % input_filename)
            user_input = input()
            if user_input.lower() in self.exit_keywords:
                print('Exiting...')
                return
            try:
                predict_lines, hash_to_string_dict = self.path_extractor.extract_paths(input_filename)
            except ValueError as e:
                print(e)
                continue
            results, code_vectors = self.model.predict(predict_lines)
            prediction_results = common.parse_results(results, hash_to_string_dict, topk=SHOW_TOP_CONTEXTS)
            for i, method_prediction in enumerate(prediction_results):
                print('Original name:\t' + method_prediction.original_name)
                for name_prob_pair in method_prediction.predictions:
                    print('\t(%f) predicted: %s' % (name_prob_pair['probability'], name_prob_pair['name']))
                print('Attention:')
                for attention_obj in method_prediction.attention_paths:
                    print('%f\tcontext: %s,%s,%s' % (
                    attention_obj['score'], attention_obj['token1'], attention_obj['path'], attention_obj['token2']))
                if self.config.EXPORT_CODE_VECTORS:
                    print('Code vecetor:')
                    print(' '.join(map(str, code_vectors[i])))
