======================
Argument Clinic How-To
======================

:author: Larry Hastings


.. topic:: Abstract

  Argument Clinic is a preprocessor for CPython C files.
  Its purpose is to automate all the boilerplate involved
  with writing argument parsing code for "builtins".
  This document shows you how to convert your first C
  function to work with Argument Clinic, and then introduces
  some advanced topics on Argument Clinic usage.

  Currently Argument Clinic is considered internal-only
  for CPython.  Its use is not supported for files outside
  CPython, and no guarantees are made regarding backwards
  compatibility for future versions.  In other words: if you
  maintain an external C extension for CPython, you're welcome
  to experiment with Argument Clinic in your own code.  But the
  version of Argument Clinic that ships with CPython 3.5 *could*
  be totally incompatible and break all your code.

========================
Basic Concepts And Usage
========================

Argument Clinic ships with CPython; you'll find it in ``Tools/clinic/clinic.py``.
If you run that script, specifying a C file as an argument::

    % python3 Tools/clinic/clinic.py foo.c

Argument Clinic will scan over the file looking for lines that
look exactly like this::

    /*[clinic input]

When it finds one, it reads everything up to a line that looks
exactly like this::

    [clinic start generated code]*/

Everything in between these two lines is input for Argument Clinic.
All of these lines, including the beginning and ending comment
lines, are collectively called an Argument Clinic "block".

When Argument Clinic parses one of these blocks, it
generates output.  This output is rewritten into the C file
immediately after the block, followed by a comment containing a checksum.
The Argument Clinic block now looks like this::

    /*[clinic input]
    ... clinic input goes here ...
    [clinic start generated code]*/
    ... clinic output goes here ...
    /*[clinic end generated code: checksum=...]*/

If you run Argument Clinic on the same file a second time, Argument Clinic
will discard the old output and write out the new output with a fresh checksum
line.  However, if the input hasn't changed, the output won't change either.

You should never modify the output portion of an Argument Clinic block.  Instead,
change the input until it produces the output you want.  (That's the purpose of the
checksum--to detect if someone changed the output, as these edits would be lost
the next time Argument Clinic writes out fresh output.)

For the sake of clarity, here's the terminology we'll use with Argument Clinic:

* The first line of the comment (``/*[clinic input]``) is the *start line*.
* The last line of the initial comment (``[clinic start generated code]*/``) is the *end line*.
* The last line (``/*[clinic end generated code: checksum=...]*/``) is the *checksum line*.
* In between the start line and the end line is the *input*.
* In between the end line and the checksum line is the *output*.
* All the text collectively, from the start line to the checksum line inclusively,
  is the *block*.  (A block that hasn't been successfully processed by Argument
  Clinic yet doesn't have output or a checksum line, but it's still considered
  a block.)


==============================
Converting Your First Function
==============================

The best way to get a sense of how Argument Clinic works is to
convert a function to work with it.  Let's dive in!

0. Make sure you're working with a freshly updated checkout
   of the CPython trunk.

1. Find a Python builtin that calls either :c:func:`PyArg_ParseTuple`
   or :c:func:`PyArg_ParseTupleAndKeywords`, and hasn't been converted
   to work with Argument Clinic yet.
   For my example I'm using ``pickle.Pickler.dump()``.

2. If the call to the ``PyArg_Parse`` function uses any of the
   following format units::

       O&
       O!
       es
       es#
       et
       et#

   or if it has multiple calls to :c:func:`PyArg_ParseTuple`,
   you should choose a different function.  Argument Clinic *does*
   support all of these scenarios.  But these are advanced
   topics--let's do something simpler for your first function.

3. Add the following boilerplate above the function, creating our block::

    /*[clinic input]
    [clinic start generated code]*/

4. Cut the docstring and paste it in between the ``[clinic]`` lines,
   removing all the junk that makes it a properly quoted C string.
   When you're done you should have just the text, based at the left
   margin, with no line wider than 80 characters.
   (Argument Clinic will preserve indents inside the docstring.)

   Sample::

    /*[clinic input]
    Write a pickled representation of obj to the open file.
    [clinic start generated code]*/

5. If your docstring doesn't have a "summary" line, Argument Clinic will
   complain.  So let's make sure it has one.  The "summary" line should
   be a paragraph consisting of a single 80-column line
   at the beginning of the docstring.

   (Our example docstring consists solely of a summary line, so the sample
   code doesn't have to change for this step.)

6. Above the docstring, enter the name of the function, followed
   by a blank line.  This should be the Python name of the function,
   and should be the full dotted path
   to the function--it should start with the name of the module,
   include any sub-modules, and if the function is a method on
   a class it should include the class name too.

   Sample::

    /*[clinic input]
    pickle.Pickler.dump

    Write a pickled representation of obj to the open file.
    [clinic start generated code]*/

7. If this is the first time that module or class has been used with Argument
   Clinic in this C file,
   you must declare the module and/or class.  Proper Argument Clinic hygiene
   prefers declaring these in a separate block somewhere near the
   top of the C file, in the same way that include files and statics go at
   the top.  (In our sample code we'll just show the two blocks next to
   each other.)

   Sample::

    /*[clinic input]
    module pickle
    class pickle.Pickler
    [clinic start generated code]*/

    /*[clinic input]
    pickle.Pickler.dump

    Write a pickled representation of obj to the open file.
    [clinic start generated code]*/


8. Declare each of the parameters to the function.  Each parameter
   should get its own line.  All the parameter lines should be
   indented from the function name and the docstring.

   The general form of these parameter lines is as follows::

       name_of_parameter: converter

   If the parameter has a default value, add that after the
   converter::

       name_of_parameter: converter = default_value

   Add a blank line below the parameters.

   What's a "converter"?  It establishes both the type
   of the variable used in C, and the method to convert the Python
   value into a C value at runtime.
   For now you're going to use what's called a "legacy converter"--a
   convenience syntax intended to make porting old code into Argument
   Clinic easier.

   For each parameter, copy the "format unit" for that
   parameter from the ``PyArg_Parse()`` format argument and
   specify *that* as its converter, as a quoted
   string.  ("format unit" is the formal name for the one-to-three
   character substring of the ``format`` parameter that tells
   the argument parsing function what the type of the variable
   is and how to convert it.  For more on format units please
   see :ref:`arg-parsing`.)

   For multicharacter format units like ``z#``, use the
   entire two-or-three character string.

   Sample::

       /*[clinic input]
       module pickle
       class pickle.Pickler
       [clinic start generated code]*/

       /*[clinic input]
       pickle.Pickler.dump

           obj: 'O'

       Write a pickled representation of obj to the open file.
       [clinic start generated code]*/

9. If your function has ``|`` in the format string, meaning some
   parameters have default values, you can ignore it.  Argument
   Clinic infers which parameters are optional based on whether
   or not they have default values.

   If your function has ``$`` in the format string, meaning it
   takes keyword-only arguments, specify ``*`` on a line by
   itself before the first keyword-only argument, indented the
   same as the parameter lines.

   (``pickle.Pickler.dump`` has neither, so our sample is unchanged.)


10. If the existing C function calls :c:func:`PyArg_ParseTuple`
    (as opposed to :c:func:`PyArg_ParseTupleAndKeywords`), then all its
    arguments are positional-only.

    To mark all parameters as positional-only in Argument Clinic,
    add a ``/`` on a line by itself after the last parameter,
    indented the same as the parameter lines.

    Currently this is all-or-nothing; either all parameters are
    positional-only, or none of them are.  (In the future Argument
    Clinic may relax this restriction.)

    Sample::

        /*[clinic input]
        module pickle
        class pickle.Pickler
        [clinic start generated code]*/

        /*[clinic input]
        pickle.Pickler.dump

            obj: 'O'
            /

        Write a pickled representation of obj to the open file.
        [clinic start generated code]*/

11. It's helpful to write a per-parameter docstring for each parameter.
    But per-parameter docstrings are optional; you can skip this step
    if you prefer.

    Here's how to add a per-parameter docstring.  The first line
    of the per-parameter docstring must be indented further than the
    parameter definition.  The left margin of this first line establishes
    the left margin for the whole per-parameter docstring; all the text
    you write will be outdented by this amount.  You can write as much
    text as you like, across multiple lines if you wish.

    Sample::

        /*[clinic input]
        module pickle
        class pickle.Pickler
        [clinic start generated code]*/

        /*[clinic input]
        pickle.Pickler.dump

            obj: 'O'
                The object to be pickled.
            /

        Write a pickled representation of obj to the open file.
        [clinic start generated code]*/

12. Save and close the file, then run ``Tools/clinic/clinic.py`` on it.
    With luck everything worked and your block now has output!  Reopen
    the file in your text editor to see::

       /*[clinic input]
       module pickle
       class pickle.Pickler
       [clinic start generated code]*/
       /*[clinic end generated code: checksum=da39a3ee5e6b4b0d3255bfef95601890afd80709]*/

       /*[clinic input]
       pickle.Pickler.dump

           obj: 'O'
               The object to be pickled.
           /

       Write a pickled representation of obj to the open file.
       [clinic start generated code]*/

       PyDoc_STRVAR(pickle_Pickler_dump__doc__,
       "Write a pickled representation of obj to the open file.\n"
       "\n"
       ...
       static PyObject *
       pickle_Pickler_dump_impl(PyObject *self, PyObject *obj)
       /*[clinic end generated code: checksum=3bd30745bf206a48f8b576a1da3d90f55a0a4187]*/

    Obviously, if Argument Clinic didn't produce any output, it's because
    it found an error in your input.  Keep fixing your errors and retrying
    until Argument Clinic processes your file without complaint.

13. Double-check that the argument-parsing code Argument Clinic generated
    looks basically the same as the existing code.

    First, ensure both places use the same argument-parsing function.
    The existing code must call either
    :c:func:`PyArg_ParseTuple` or :c:func:`PyArg_ParseTupleAndKeywords`;
    ensure that the code generated by Argument Clinic calls the
    *exact* same function.

    Second, the format string passed in to :c:func:`PyArg_ParseTuple` or
    :c:func:`PyArg_ParseTupleAndKeywords` should be *exactly* the same
    as the hand-written one in the existing function, up to the colon
    or semi-colon.

    (Argument Clinic always generates its format strings
    with a ``:`` followed by the name of the function.  If the
    existing code's format string ends with ``;``, to provide
    usage help, this change is harmless--don't worry about it.)

    Third, for parameters whose format units require two arguments
    (like a length variable, or an encoding string, or a pointer
    to a conversion function), ensure that the second argument is
    *exactly* the same between the two invocations.

    Fourth, inside the output portion of the block you'll find a preprocessor
    macro defining the appropriate static :c:type:`PyMethodDef` structure for
    this builtin::

        #define _PICKLE_PICKLER_DUMP_METHODDEF    \
        {"dump", (PyCFunction)_pickle_Pickler_dump, METH_O, _pickle_Pickler_dump__doc__},

    This static structure should be *exactly* the same as the existing static
    :c:type:`PyMethodDef` structure for this builtin.

    If any of these items differ in *any way*,
    adjust your Argument Clinic function specification and rerun
    ``Tools/clinic/clinic.py`` until they *are* the same.


14. Notice that the last line of its output is the declaration
    of your "impl" function.  This is where the builtin's implementation goes.
    Delete the existing prototype of the function you're modifying, but leave
    the opening curly brace.  Now delete its argument parsing code and the
    declarations of all the variables it dumps the arguments into.
    Notice how the Python arguments are now arguments to this impl function;
    if the implementation used different names for these variables, fix it.

    Let's reiterate, just because it's kind of weird.  Your code should now
    look like this::

        static return_type
        your_function_impl(...)
        /*[clinic end generated code: checksum=...]*/
        {
        ...

    Argument Clinic generated the checksum line and the function prototype just
    above it.  You should write the opening (and closing) curly braces for the
    function, and the implementation inside.

    Sample::

        /*[clinic input]
        module pickle
        class pickle.Pickler
        [clinic start generated code]*/
        /*[clinic end generated code: checksum=da39a3ee5e6b4b0d3255bfef95601890afd80709]*/

        /*[clinic input]
        pickle.Pickler.dump

            obj: 'O'
                The object to be pickled.
            /

        Write a pickled representation of obj to the open file.
        [clinic start generated code]*/

        PyDoc_STRVAR(pickle_Pickler_dump__doc__,
        "Write a pickled representation of obj to the open file.\n"
        "\n"
        ...
        static PyObject *
        pickle_Pickler_dump_impl(PyObject *self, PyObject *obj)
        /*[clinic end generated code: checksum=3bd30745bf206a48f8b576a1da3d90f55a0a4187]*/
        {
            /* Check whether the Pickler was initialized correctly (issue3664).
               Developers often forget to call __init__() in their subclasses, which
               would trigger a segfault without this check. */
            if (self->write == NULL) {
                PyErr_Format(PicklingError,
                             "Pickler.__init__() was not called by %s.__init__()",
                             Py_TYPE(self)->tp_name);
                return NULL;
            }

            if (_Pickler_ClearBuffer(self) < 0)
                return NULL;

            ...

15. Remember the macro with the :c:type:`PyMethodDef` structure for this
    function?  Find the existing :c:type:`PyMethodDef` structure for this
    function and replace it with a reference to the macro.  (If the builtin
    is at module scope, this will probably be very near the end of the file;
    if the builtin is a class method, this will probably be below but relatively
    near to the implementation.)

    Note that the body of the macro contains a trailing comma.  So when you
    replace the existing static :c:type:`PyMethodDef` structure with the macro,
    *don't* add a comma to the end.

    Sample::

        static struct PyMethodDef Pickler_methods[] = {
            _PICKLE_PICKLER_DUMP_METHODDEF
            _PICKLE_PICKLER_CLEAR_MEMO_METHODDEF
            {NULL, NULL}                /* sentinel */
        };


16. Compile, then run the relevant portions of the regression-test suite.
    This change should not introduce any new compile-time warnings or errors,
    and there should be no externally-visible change to Python's behavior.

    Well, except for one difference: ``inspect.signature()`` run on your function
    should now provide a valid signature!

    Congratulations, you've ported your first function to work with Argument Clinic!

===============
Advanced Topics
===============


Renaming the C functions generated by Argument Clinic
-----------------------------------------------------

Argument Clinic automatically names the functions it generates for you.
Occasionally this may cause a problem, if the generated name collides with
the name of an existing C function.  There's an easy solution: override the names
used for the C functions.  Just add the keyword ``"as"``
to your function declaration line, followed by the function name you wish to use.
Argument Clinic will use that function name for the base (generated) function,
then add ``"_impl"`` to the end and use that for the name of the impl function.

For example, if we wanted to rename the C function names generated for
``pickle.Pickler.dump``, it'd look like this::

    /*[clinic input]
    pickle.Pickler.dump as pickler_dumper

    ...

The base function would now be named ``pickler_dumper()``,
and the impl function would now be named ``pickler_dumper_impl()``.


Optional Groups
---------------

Some legacy functions have a tricky approach to parsing their arguments:
they count the number of positional arguments, then use a ``switch`` statement
to call one of several different :c:func:`PyArg_ParseTuple` calls depending on
how many positional arguments there are.  (These functions cannot accept
keyword-only arguments.)  This approach was used to simulate optional
arguments back before :c:func:`PyArg_ParseTupleAndKeywords` was created.

While functions using this approach can often be converted to
use :c:func:`PyArg_ParseTupleAndKeywords`, optional arguments, and default values,
it's not always possible.  Some of these legacy functions have
behaviors :c:func:`PyArg_ParseTupleAndKeywords` doesn't directly support.
The most obvious example is the builtin function ``range()``, which has
an optional argument on the *left* side of its required argument!
Another example is ``curses.window.addch()``, which has a group of two
arguments that must always be specified together.  (The arguments are
called ``x`` and ``y``; if you call the function passing in ``x``,
you must also pass in ``y``--and if you don't pass in ``x`` you may not
pass in ``y`` either.)

In any case, the goal of Argument Clinic is to support argument parsing
for all existing CPython builtins without changing their semantics.
Therefore Argument Clinic supports
this alternate approach to parsing, using what are called *optional groups*.
Optional groups are groups of arguments that must all be passed in together.
They can be to the left or the right of the required arguments.  They
can *only* be used with positional-only parameters.

To specify an optional group, add a ``[`` on a line by itself before
the parameters you wish to group together, and a ``]`` on a line by itself
after these parameters.  As an example, here's how ``curses.window.addch``
uses optional groups to make the first two parameters and the last
parameter optional::

    /*[clinic input]

    curses.window.addch

        [
        x: int
          X-coordinate.
        y: int
          Y-coordinate.
        ]

        ch: object
          Character to add.

        [
        attr: long
          Attributes for the character.
        ]
        /

    ...


Notes:

* For every optional group, one additional parameter will be passed into the
  impl function representing the group.  The parameter will be an int named
  ``group_{direction}_{number}``,
  where ``{direction}`` is either ``right`` or ``left`` depending on whether the group
  is before or after the required parameters, and ``{number}`` is a monotonically
  increasing number (starting at 1) indicating how far away the group is from
  the required parameters.  When the impl is called, this parameter will be set
  to zero if this group was unused, and set to non-zero if this group was used.
  (By used or unused, I mean whether or not the parameters received arguments
  in this invocation.)

* If there are no required arguments, the optional groups will behave
  as if they're to the right of the required arguments.

* In the case of ambiguity, the argument parsing code
  favors parameters on the left (before the required parameters).

* Optional groups can only contain positional-only parameters.

* Optional groups are *only* intended for legacy code.  Please do not
  use optional groups for new code.


Using real Argument Clinic converters, instead of "legacy converters"
---------------------------------------------------------------------

To save time, and to minimize how much you need to learn
to achieve your first port to Argument Clinic, the walkthrough above tells
you to use "legacy converters".  "Legacy converters" are a convenience,
designed explicitly to make porting existing code to Argument Clinic
easier.  And to be clear, their use is entirely acceptable when porting
code for Python 3.4.

However, in the long term we probably want all our blocks to
use Argument Clinic's real syntax for converters.  Why?  A couple
reasons:

* The proper converters are far easier to read and clearer in their intent.
* There are some format units that are unsupported as "legacy converters",
  because they require arguments, and the legacy converter syntax doesn't
  support specifying arguments.
* In the future we may have a new argument parsing library that isn't
  restricted to what :c:func:`PyArg_ParseTuple` supports; this flexibility
  won't be available to parameters using legacy converters.

Therefore, if you don't mind a little extra effort, you should consider
using normal converters instead of legacy converters.

In a nutshell, the syntax for Argument Clinic (non-legacy) converters
looks like a Python function call.  However, if there are no explicit
arguments to the function (all functions take their default values),
you may omit the parentheses.  Thus ``bool`` and ``bool()`` are exactly
the same converters.

All arguments to Argument Clinic converters are keyword-only.
All Argument Clinic converters accept the following arguments:

``doc_default``
  If the parameter takes a default value, normally this value is also
  provided in the ``inspect.Signature`` metadata, and displayed in the
  docstring.  ``doc_default`` lets you override the value used in these
  two places: pass in a string representing the Python value you wish
  to use in these two contexts.

``required``
  If a parameter takes a default value, Argument Clinic infers that the
  parameter is optional.  However, you may want a parameter to take a
  default value in C, but not behave in Python as if the parameter is
  optional.  Passing in ``required=True`` to a converter tells Argument
  Clinic that this parameter is not optional, even if it has a default
  value.

``annotation``
  The annotation value for this parameter.  Not currently supported,
  because PEP 8 mandates that the Python library may not use
  annotations.

Below is a table showing the mapping of legacy converters into real
Argument Clinic converters.  On the left is the legacy converter,
on the right is the text you'd replace it with.

=========   =================================================================================
``'B'``     ``byte(bitwise=True)``
``'b'``     ``byte``
``'c'``     ``char``
``'C'``     ``int(types='str')``
``'d'``     ``double``
``'D'``     ``Py_complex``
``'es#'``   ``str(encoding='name_of_encoding', length=True, zeroes=True)``
``'es'``    ``str(encoding='name_of_encoding')``
``'et#'``   ``str(encoding='name_of_encoding', types='bytes bytearray str', length=True)``
``'et'``    ``str(encoding='name_of_encoding', types='bytes bytearray str')``
``'f'``     ``float``
``'h'``     ``short``
``'H'``     ``unsigned_short``
``'i'``     ``int``
``'I'``     ``unsigned_int``
``'K'``     ``unsigned_PY_LONG_LONG``
``'L'``     ``PY_LONG_LONG``
``'n'``     ``Py_ssize_t``
``'O!'``    ``object(subclass_of='&PySomething_Type')``
``'O&'``    ``object(converter='name_of_c_function')``
``'O'``     ``object``
``'p'``     ``bool``
``'s#'``    ``str(length=True)``
``'S'``     ``PyBytesObject``
``'s'``     ``str``
``'s*'``    ``Py_buffer(types='str bytes bytearray buffer')``
``'u#'``    ``Py_UNICODE(length=True)``
``'u'``     ``Py_UNICODE``
``'U'``     ``unicode``
``'w*'``    ``Py_buffer(types='bytearray rwbuffer')``
``'y#'``    ``str(type='bytes', length=True)``
``'Y'``     ``PyByteArrayObject``
``'y'``     ``str(type='bytes')``
``'y*'``    ``Py_buffer``
``'Z#'``    ``Py_UNICODE(nullable=True, length=True)``
``'z#'``    ``str(nullable=True, length=True)``
``'Z'``     ``Py_UNICODE(nullable=True)``
``'z'``     ``str(nullable=True)``
``'z*'``    ``Py_buffer(types='str bytes bytearray buffer', nullable=True)``
=========   =================================================================================

As an example, here's our sample ``pickle.Pickler.dump`` using the proper
converter::

    /*[clinic input]
    pickle.Pickler.dump

        obj: object
            The object to be pickled.
        /

    Write a pickled representation of obj to the open file.
    [clinic start generated code]*/

Argument Clinic will show you all the converters it has
available.  For each converter it'll show you all the parameters
it accepts, along with the default value for each parameter.
Just run ``Tools/clinic/clinic.py --converters`` to see the full list.


Advanced converters
-------------------

Remeber those format units you skipped for your first
time because they were advanced?  Here's how to handle those too.

The trick is, all those format units take arguments--either
conversion functions, or types, or strings specifying an encoding.
(But "legacy converters" don't support arguments.  That's why we
skipped them for your first function.)  The argument you specified
to the format unit is now an argument to the converter; this
argument is either ``converter`` (for ``O&``), ``subclass_of`` (for ``O!``),
or ``encoding`` (for all the format units that start with ``e``).

When using ``subclass_of``, you may also want to use the other
custom argument for ``object()``: ``type``, which lets you set the type
actually used for the parameter.  For example, if you want to ensure
that the object is a subclass of ``PyUnicode_Type``, you probably want
to use the converter ``object(type='PyUnicodeObject *', subclass_of='&PyUnicode_Type')``.

One possible problem with using Argument Clinic: it takes away some possible
flexibility for the format units starting with ``e``.  When writing a
``PyArg_Parse`` call by hand, you could theoretically decide at runtime what
encoding string to pass in to :c:func:`PyArg_ParseTuple`.   But now this string must
be hard-coded at Argument-Clinic-preprocessing-time.  This limitation is deliberate;
it made supporting this format unit much easier, and may allow for future optimizations.
This restriction doesn't seem unreasonable; CPython itself always passes in static
hard-coded encoding strings for parameters whose format units start with ``e``.


Using a return converter
------------------------

By default the impl function Argument Clinic generates for you returns ``PyObject *``.
But your C function often computes some C type, then converts it into the ``PyObject *``
at the last moment.  Argument Clinic handles converting your inputs from Python types
into native C types--why not have it convert your return value from a native C type
into a Python type too?

That's what a "return converter" does.  It changes your impl function to return
some C type, then adds code to the generated (non-impl) function to handle converting
that value into the appropriate ``PyObject *``.

The syntax for return converters is similar to that of parameter converters.
You specify the return converter like it was a return annotation on the
function itself.  Return converters behave much the same as parameter converters;
they take arguments, the arguments are all keyword-only, and if you're not changing
any of the default arguments you can omit the parentheses.

(If you use both ``"as"`` *and* a return converter for your function,
the ``"as"`` should come before the return converter.)

There's one additional complication when using return converters: how do you
indicate an error has occured?  Normally, a function returns a valid (non-``NULL``)
pointer for success, and ``NULL`` for failure.  But if you use an integer return converter,
all integers are valid.  How can Argument Clinic detect an error?  Its solution: each return
converter implicitly looks for a special value that indicates an error.  If you return
that value, and an error has been set (``PyErr_Occurred()`` returns a true
value), then the generated code will propogate the error.  Otherwise it will
encode the value you return like normal.

Currently Argument Clinic supports only a few return converters::

    int
    long
    Py_ssize_t
    DecodeFSDefault

None of these take parameters.  For the first three, return -1 to indicate
error.  For ``DecodeFSDefault``, the return type is ``char *``; return a NULL
pointer to indicate an error.

To see all the return converters Argument Clinic supports, along with
their parameters (if any),
just run ``Tools/clinic/clinic.py --converters`` for the full list.


Calling Python code
-------------------

The rest of the advanced topics require you to write Python code
which lives inside your C file and modifies Argument Clinic's
runtime state.  This is simple: you simply define a Python block.

A Python block uses different delimiter lines than an Argument
Clinic function block.  It looks like this::

    /*[python input]
    # python code goes here
    [python start generated code]*/

All the code inside the Python block is executed at the
time it's parsed.  All text written to stdout inside the block
is redirected into the "output" after the block.

As an example, here's a Python block that adds a static integer
variable to the C code::

    /*[python input]
    print('static int __ignored_unused_variable__ = 0;')
    [python start generated code]*/
    static int __ignored_unused_variable__ = 0;
    /*[python checksum:...]*/


Using a "self converter"
------------------------

Argument Clinic automatically adds a "self" parameter for you
using a default converter.  However, you can override
Argument Clinic's converter and specify one yourself.
Just add your own ``self`` parameter as the first parameter in a
block, and ensure that its converter is an instance of
``self_converter`` or a subclass thereof.

What's the point?  This lets you automatically cast ``self``
from ``PyObject *`` to a custom type, just like ``object()``
does with its ``type`` parameter.

How do you specify the custom type you want to cast ``self`` to?
If you only have one or two functions with the same type for ``self``,
you can directly use Argument Clinic's existing ``self`` converter,
passing in the type you want to use as the ``type`` parameter::

    /*[clinic input]

    _pickle.Pickler.dump

      self: self(type="PicklerObject *")
      obj: object
      /

    Write a pickled representation of the given object to the open file.
    [clinic start generated code]*/

On the other hand, if you have a lot of functions that will use the same
type for ``self``, it's best to create your own converter, subclassing
``self_converter`` but overwriting the ``type`` member::

    /*[clinic input]
    class PicklerObject_converter(self_converter):
        type = "PicklerObject *"
    [clinic start generated code]*/

    /*[clinic input]

    _pickle.Pickler.dump

      self: PicklerObject
      obj: object
      /

    Write a pickled representation of the given object to the open file.
    [clinic start generated code]*/



Writing a custom converter
--------------------------

As we hinted at in the previous section... you can write your own converters!
A converter is simply a Python class that inherits from ``CConverter``.
The main purpose of a custom converter is if you have a parameter using
the ``O&`` format unit--parsing this parameter means calling
a :c:func:`PyArg_ParseTuple` "converter function".

Your converter class should be named ``*something*_converter``.
If the name follows this convention, then your converter class
will be automatically registered with Argument Clinic; its name
will be the name of your class with the ``_converter`` suffix
stripped off.  (This is accomplished with a metaclass.)

You shouldn't subclass ``CConverter.__init__``.  Instead, you should
write a ``converter_init()`` function.  ``converter_init()``
always accepts a ``self`` parameter; after that, all additional
parameters *must* be keyword-only.  Any arguments passed in to
the converter in Argument Clinic will be passed along to your
``converter_init()``.

There are some additional members of ``CConverter`` you may wish
to specify in your subclass.  Here's the current list:

``type``
    The C type to use for this variable.
    ``type`` should be a Python string specifying the type, e.g. ``int``.
    If this is a pointer type, the type string should end with ``' *'``.

``default``
    The Python default value for this parameter, as a Python value.
    Or the magic value ``unspecified`` if there is no default.

``doc_default``
    ``default`` as it should appear in the documentation,
    as a string.
    Or ``None`` if there is no default.
    This string, when run through ``eval()``, should produce
    a Python value.

``py_default``
    ``default`` as it should appear in Python code,
    as a string.
    Or ``None`` if there is no default.

``c_default``
    ``default`` as it should appear in C code,
    as a string.
    Or ``None`` if there is no default.

``c_ignored_default``
    The default value used to initialize the C variable when
    there is no default, but not specifying a default may
    result in an "uninitialized variable" warning.  This can
    easily happen when using option groups--although
    properly-written code will never actually use this value,
    the variable does get passed in to the impl, and the
    C compiler will complain about the "use" of the
    uninitialized value.  This value should always be a
    non-empty string.

``converter``
    The name of the C converter function, as a string.

``impl_by_reference``
    A boolean value.  If true,
    Argument Clinic will add a ``&`` in front of the name of
    the variable when passing it into the impl function.

``parse_by_reference``
    A boolean value.  If true,
    Argument Clinic will add a ``&`` in front of the name of
    the variable when passing it into :c:func:`PyArg_ParseTuple`.


Here's the simplest example of a custom converter, from ``Modules/zlibmodule.c``::

    /*[python input]

    class uint_converter(CConverter):
        type = 'unsigned int'
        converter = 'uint_converter'

    [python start generated code]*/
    /*[python end generated code: checksum=da39a3ee5e6b4b0d3255bfef95601890afd80709]*/

This block adds a converter to Argument Clinic named ``uint``.  Parameters
declared as ``uint`` will be declared as type ``unsigned int``, and will
be parsed by the ``'O&'`` format unit, which will call the ``uint_converter``
converter function.
``uint`` variables automatically support default values.

More sophisticated custom converters can insert custom C code to
handle initialization and cleanup.
You can see more examples of custom converters in the CPython
source tree; grep the C files for the string ``CConverter``.

Writing a custom return converter
---------------------------------

Writing a custom return converter is much like writing
a custom converter.  Except it's somewhat simpler, because return
converters are themselves much simpler.

Return converters must subclass ``CReturnConverter``.
There are no examples yet of custom return converters,
because they are not widely used yet.  If you wish to
write your own return converter, please read ``Tools/clinic/clinic.py``,
specifically the implementation of ``CReturnConverter`` and
all its subclasses.


Using Argument Clinic in Python files
-------------------------------------

It's actually possible to use Argument Clinic to preprocess Python files.
There's no point to using Argument Clinic blocks, of course, as the output
wouldn't make any sense to the Python interpreter.  But using Argument Clinic
to run Python blocks lets you use Python as a Python preprocessor!

Since Python comments are different from C comments, Argument Clinic
blocks embedded in Python files look slightly different.  They look like this::

    #/*[python input]
    #print("def foo(): pass")
    #[python start generated code]*/
    def foo(): pass
    #/*[python checksum:...]*/
