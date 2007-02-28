#! /usr/bin/env python

"""Non-terminal symbols of Python grammar (from "graminit.h")."""

#  This file is automatically generated; please don't muck it up!
#
#  To update the symbols in this file, 'cd' to the top directory of
#  the python source tree after building the interpreter and run:
#
#    python Lib/symbol.py

#--start constants--
single_input = 256
file_input = 257
eval_input = 258
decorator = 259
decorators = 260
funcdef = 261
parameters = 262
typedargslist = 263
tname = 264
tfpdef = 265
tfplist = 266
varargslist = 267
vname = 268
vfpdef = 269
vfplist = 270
stmt = 271
simple_stmt = 272
small_stmt = 273
expr_stmt = 274
augassign = 275
del_stmt = 276
pass_stmt = 277
flow_stmt = 278
break_stmt = 279
continue_stmt = 280
return_stmt = 281
yield_stmt = 282
raise_stmt = 283
import_stmt = 284
import_name = 285
import_from = 286
import_as_name = 287
dotted_as_name = 288
import_as_names = 289
dotted_as_names = 290
dotted_name = 291
global_stmt = 292
nonlocal_stmt = 293
assert_stmt = 294
compound_stmt = 295
if_stmt = 296
while_stmt = 297
for_stmt = 298
try_stmt = 299
with_stmt = 300
with_var = 301
except_clause = 302
suite = 303
testlist_safe = 304
old_test = 305
old_lambdef = 306
test = 307
or_test = 308
and_test = 309
not_test = 310
comparison = 311
comp_op = 312
expr = 313
xor_expr = 314
and_expr = 315
shift_expr = 316
arith_expr = 317
term = 318
factor = 319
power = 320
atom = 321
listmaker = 322
testlist_gexp = 323
lambdef = 324
trailer = 325
subscriptlist = 326
subscript = 327
sliceop = 328
exprlist = 329
testlist = 330
dictsetmaker = 331
classdef = 332
arglist = 333
argument = 334
list_iter = 335
list_for = 336
list_if = 337
gen_iter = 338
gen_for = 339
gen_if = 340
testlist1 = 341
encoding_decl = 342
yield_expr = 343
#--end constants--

sym_name = {}
for _name, _value in list(globals().items()):
    if type(_value) is type(0):
        sym_name[_value] = _name


def main():
    import sys
    import token
    if len(sys.argv) == 1:
        sys.argv = sys.argv + ["Include/graminit.h", "Lib/symbol.py"]
    token.main()

if __name__ == "__main__":
    main()
