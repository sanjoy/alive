Alive: Automatic LLVM's Instcombine Verifier
============================================

Alive is a tool that can prove the correctness of InstCombine optimizations
specified in a high-level language.


Requirements
------------
Alive requires Python 2.7.x or 3.x and Z3 4.3.2 (or later), which can be 
obtained from https://github.com/Z3Prover/z3 or
precompiled from https://github.com/Z3Prover/bin/tree/master/releases


Usage
-----
  ./alive.py file.opt

The 'tests' directory has multiple examples of optimizations.


More Information
----------------
Please see this paper for more details about Alive:

  http://www.cs.utah.edu/~regehr/papers/pldi15.pdf


Online Version
--------------
Alive is also available online at: http://rise4fun.com/Alive


Generating Benchmarks
---------------------
Alive will automatically generate benchmarks in SMT-LIB 2 format when the
'bench' directory exists and when python is run in non-optimized mode (the
default).
These benchmarks are over the bit-vector theory and may or may not have
quantifiers.
