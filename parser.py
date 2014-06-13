# Copyright 2014 The ALIVe authors.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from pyparsing.pyparsing import *
from language import *

identifiers = {}


def parseType(toks):
  if toks[0] == 'i':
    return IntType(int(toks[1]))
  assert False


def parseOptType(toks):
  if len(toks) == 1:
    return toks[0]
  return IntType()


def parseOperand(toks, type):
  global identifiers

  # %var
  if len(toks) == 2:
    reg = '%' + toks[1]
    if identifiers.has_key(reg):
      return identifiers[reg]
    identifiers[reg] = v = Input(reg, type)
    return v

  # constant
  assert len(toks) == 1
  if toks[0] == 'true':
    n = 1
  elif toks[0] == 'false':
    n = 0
  else:
    n = int(toks[0])

  c = Constant(n, type)
  identifiers[str(c.getTypeSMTName())] = c
  return c

def parseTypeOperand(toks):
  return [toks[0], parseOperand(toks[1], toks[0])]

def parseOptionalStr(toks):
  return toks[0] if len(toks) > 0 else ''

def parseBinOp(toks):
  return BinOp(BinOp.getOpId(toks[0]), toks[2], toks[3],
               parseOperand(toks[4], toks[2]), toks[1])

def parseConversionOp(toks):
  return ConversionOp(ConversionOp.getOpId(toks[0]), toks[1], toks[2], toks[3])

def parseIcmp(toks):
  return Icmp(toks[1], toks[2], toks[3], parseOperand(toks[4], toks[2]))

def parseSelect(toks):
  t1 = toks[2]
  t2 = toks[4]
  if t1.defined:
    if t2.defined:
      if t1.getIntSize() != t2.getIntSize():
        print 'Error: type mismatch in select: %s vs %s' % (t1, t2)
        exit(-1)
    t = t1
  else:
    t = t2
  return Select(t, parseOperand(toks[1], IntType(1)), toks[3], toks[5])

def parseOperandInstr(toks):
  op = parseOperand(toks[1], toks[0])
  if isinstance(op, Constant):
    return op
  return CopyReg(op, toks[0])


def parseInstr(toks):
  global identifiers

  reg = '%' + toks[1]
  if identifiers.has_key(reg):
    print 'Redifinition of ' + reg
    exit(-1)

  toks[2].setName(reg)
  identifiers[reg] = toks[2]
  return


identifier = Word(srange("[a-zA-Z0-9_.]"))
reg = Literal('%') + identifier
opname = identifier

instrs = Forward()
prog = instrs + StringEnd()

comment = Literal(';') + restOfLine()

type = (Literal('i') + Word(nums)).setParseAction(parseType)
opttype = Optional(type).setParseAction(parseOptType)
flags = ZeroOrMore(Literal('nsw') | Literal('nuw') | Literal('exact')).\
        setParseAction(lambda toks : [toks])
operand = (reg | Regex(r"-?[0-9]+") | Literal('false') | Literal('true')).\
            setParseAction(lambda toks : [toks])

typeoperand = (opttype + operand).setParseAction(parseTypeOperand)
comma = Literal(',').suppress()

binop = (opname + flags + typeoperand + comma + operand).\
          setParseAction(parseBinOp)

conversionop = (opname + typeoperand +\
                Optional(Literal('to').suppress() + type).\
                 setParseAction(parseOptType)).setParseAction(parseConversionOp)

optionalname = Optional(identifier).setParseAction(parseOptionalStr)

icmp = (Literal('icmp') + optionalname + typeoperand + comma + operand).\
         setParseAction(parseIcmp)

select = (Literal('select') + Optional(Literal('i1')).suppress() + operand +\
          comma + typeoperand + comma + typeoperand).setParseAction(parseSelect)

operandinstr = (opttype + operand).setParseAction(parseOperandInstr)

op = icmp | select | binop | conversionop | operandinstr


instr = (reg + Literal('=').suppress() + op).setParseAction(parseInstr) |\
        comment.suppress()
instrs <<= OneOrMore(instr)


def parse_llvm(txt, table):
  global identifiers
  try:
    identifiers = table
    prog.parseString(txt)
  except ParseException, e:
    print 'Parsing error:'
    print e
    exit(-1)


##########################
src = Literal('===') + Literal('Source') + Literal('===')
tgt = Literal('===') + Literal('Target') + Literal('===')
pre = Literal('===') + Literal('Pre') + Literal('===')
boolexpr = Literal('true') # TODO
opt_file = src.suppress() + SkipTo('===') +\
           tgt.suppress() + (SkipTo('===') | SkipTo(StringEnd())) +\
           Optional(pre.suppress() + boolexpr) + StringEnd()

def parse_opt_file(txt):
  try:
    return opt_file.parseString(txt)
  except ParseException, e:
    print 'Parsing error:'
    print e
    exit(-1)
