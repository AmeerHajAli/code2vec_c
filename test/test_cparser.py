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
# Test the ASTNode class as well as token manipulation code in file
# This script requires clang to work correctly.  The CLANG_PATH environment variable
# must point to the library for this code to work correctly. 

import unittest, os, sys
from StringIO import StringIO
from clang.cindex import Config, Index, CursorKind, TypeKind, LinkageKind, TranslationUnit, StorageClass
testdir = os.path.abspath(os.path.dirname(sys.argv[0]))
srcdir = '../'
sys.path.insert(0, os.path.abspath(os.path.join(testdir, srcdir)))
import cparser as cp
import astnode

class TmpObject(object):
    pass
hash_const = "sum|square v1,c375f631afa6af4cdb856067743771a8c8631231e0358b6a3264e0f17cccece5,v2 v1,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v1 v1,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v2 v1,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v1 v1,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v2 v2,c375f631afa6af4cdb856067743771a8c8631231e0358b6a3264e0f17cccece5,v1 v2,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v1 v2,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v2 v2,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v1 v2,f3aa6ec4ca33e8d047be1cf2d75ade3efe56e28bf0283699557420362edaf2f9,v2 v1,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v1 v1,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v2 v1,944ae52db187a5aed0f55cc8b2ab6aaa371ddda027c0e6434f0b2bf1765ba9d4,v2 v1,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v1 v1,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v2 v2,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v1 v2,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v2 v2,944ae52db187a5aed0f55cc8b2ab6aaa371ddda027c0e6434f0b2bf1765ba9d4,v1 v2,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v1 v2,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v2 v1,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v1 v1,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v2 v1,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v1 v1,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v2 v1,944ae52db187a5aed0f55cc8b2ab6aaa371ddda027c0e6434f0b2bf1765ba9d4,v2 v2,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v1 v2,2d7f777b56ac82b7b48d1e38017430b067b3f201c8440a550cd7d463c203a401,v2 v2,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v1 v2,5b354093cc588c05d20ee8bc70c00e6cf5964dbef4b10f4fc8379152fb2cdee6,v2 v2,944ae52db187a5aed0f55cc8b2ab6aaa371ddda027c0e6434f0b2bf1765ba9d4,v1\n"
path_const = "sum|square v1,(PARM_DECL)^(FUNCTION_DECL)_(PARM_DECL),v2 v1,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v1,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v1,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v1,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v2,(PARM_DECL)^(FUNCTION_DECL)_(PARM_DECL),v1 v2,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v2,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v2,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v2,(PARM_DECL)^(FUNCTION_DECL)_(COMPOUND_STMT)_(RETURN_STMT)_(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v1 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v2 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v1 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v2 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v1 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v2 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v1,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v1 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)^(RETURN_STMT)^(COMPOUND_STMT)^(FUNCTION_DECL)_(PARM_DECL),v2 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)^(PAREN_EXPR)^(BINARY_OPERATOR:*)_(PAREN_EXPR)_(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v2 v2,(DECL_REF_EXPR)^(UNEXPOSED_EXPR)^(BINARY_OPERATOR:+)_(UNEXPOSED_EXPR)_(DECL_REF_EXPR),v1\n"
tree_const = """-FUNCTION_DECL sum_square int (int, int) FUNCTION_DECL
  -PARM_DECL v1 int v1
  -PARM_DECL v2 int v2
  -COMPOUND_STMT   COMPOUND_STMT
    -RETURN_STMT   RETURN_STMT
      -BINARY_OPERATOR  int *
        -PAREN_EXPR  int PAREN_EXPR
          -BINARY_OPERATOR  int +
            -UNEXPOSED_EXPR v1 int v1
              -DECL_REF_EXPR v1 int v1
            -UNEXPOSED_EXPR v2 int v2
              -DECL_REF_EXPR v2 int v2
        -PAREN_EXPR  int PAREN_EXPR
          -BINARY_OPERATOR  int +
            -UNEXPOSED_EXPR v1 int v1
              -DECL_REF_EXPR v1 int v1
            -UNEXPOSED_EXPR v2 int v2
              -DECL_REF_EXPR v2 int v2
"""
CLANG_PATH = ""
class Test_cparser(unittest.TestCase):
   
    def setUp(self):
        self.args = TmpObject()
        self.args.file_path = os.path.abspath(os.path.dirname(sys.argv[0]))+os.sep+"sample.c"
        self.args.max_leaves = 32
        self.args.hash_paths = False
        self.args.clang_path = CLANG_PATH
        self.args.dump_tree = False
        self.args.dump_nodes = False
        self.args.skip_decls = False
        self.args.include_path = os.path.abspath(os.path.dirname(sys.argv[0]))
        cp.set_args(self.args)
        self.index = Index.create()
        self.tu = self.index.parse(self.args.file_path)
    
    def test_set_args(self):
        args = TmpObject()
        args.dir_path = "/tmp"
        cp.set_args(args)
        self.assertEquals(cp.ARGS.dir_path, "/tmp")

    def test_setup_includes(self):
        self.assertEquals(cp.setup_includes(), [os.path.abspath(os.path.dirname(sys.argv[0]))])

    def test_add_dir_if_exists(self):
        tmp = []
        cp.add_dir_if_exists(tmp, os.path.abspath(os.path.dirname(sys.argv[0])))
        self.assertEquals(tmp, [os.path.abspath(os.path.dirname(sys.argv[0]))])
        cp.add_dir_if_exists(tmp, "/thisprobablydoesntexistonyourmachine")
        self.assertEquals(tmp, [os.path.abspath(os.path.dirname(sys.argv[0]))])

    def test_append_include(self):
        self.assertEquals(cp.append_include("tmp"), "tmp"+os.sep+"include")
        self.assertEquals(cp.append_include("tmp"+os.sep), "tmp"+os.sep+"include")

    def test_parse_single(self):
        cp.parse_single(self.args.file_path, [], self.index)
        with self.assertRaises(Exception):
            cp.parse_single("garbage", [], self.index)

    def test_traverse_to_print(self):
        output = StringIO()
        functions = cp.root_level(self.tu.cursor.get_children())
        cp.traverse_to_print(functions[0], output)
        self.assertEqual(output.getvalue(), tree_const)
        output.close()

    def test_generate_and_print_paths(self):
        # Test hashed writing
        output = StringIO()
        functions = cp.root_level(self.tu.cursor.get_children())
        cp.generate_and_print_paths(functions[0], output)
        self.assertEqual(output.getvalue(), hash_const)
        vals = output.getvalue().split(" ")
        output.close()
        self.assertEqual(len(vals), 31)
        self.assertEqual(vals[0], "sum|square")
        # Test unhashed writing
        self.args.hash_paths = True
        output = StringIO()
        functions = cp.root_level(self.tu.cursor.get_children())
        cp.generate_and_print_paths(functions[0], output)
        self.assertEqual(output.getvalue(), path_const)
        # Revisit
        cp.generate_and_print_paths(functions[1], sys.stdout)
        # Test max leaves
        self.args.max_leaves = 5
        output = StringIO()
        functions = cp.root_level(self.tu.cursor.get_children())
        cp.generate_and_print_paths(functions[0], output)
        self.assertEqual(output.getvalue(), "")
        self.args.max_leaves = 6
        output = StringIO()
        functions = cp.root_level(self.tu.cursor.get_children())
        cp.generate_and_print_paths(functions[0], output)
        self.assertNotEqual(output.getvalue(), "")
        output.close()


    # Stubbed for later
    def test_visit(self):
        self.assertEqual(True, True)

    def test_traverse(self):
        self.assertEqual(True, True)

    def test_normalize_function_name(self):
        self.assertEqual(True, True)

if __name__ == '__main__':
    # Ensure clang is setup (but only do it once)
    CLANG_PATH = os.environ.get('CLANG_PATH', CLANG_PATH)
    cp.configure_clang(CLANG_PATH)
    unittest.main()

