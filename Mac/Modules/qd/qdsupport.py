# This script generates a Python interface for an Apple Macintosh Manager.
# It uses the "bgen" package to generate C code.
# The function specifications are generated by scanning the mamager's header file,
# using the "scantools" package (customized for this particular manager).

import string

# Declarations that change for each manager
MACHEADERFILE = 'QuickDraw.h'		# The Apple header file
MODNAME = 'Qd'				# The name of the module
OBJECTNAME = 'Graf'			# The basic name of the objects used here

# The following is *usually* unchanged but may still require tuning
MODPREFIX = MODNAME			# The prefix for module-wide routines
OBJECTTYPE = OBJECTNAME + 'Ptr'		# The C type used to represent them
OBJECTPREFIX = MODPREFIX + 'Obj'	# The prefix for object methods
INPUTFILE = string.lower(MODPREFIX) + 'gen.py' # The file generated by the scanner
EXTRAFILE = string.lower(MODPREFIX) + 'edit.py' # A similar file but hand-made
OUTPUTFILE = MODNAME + "module.c"	# The file generated by this program

from macsupport import *

# Create the type objects

class TextThingieClass(FixedInputBufferType):
	def getargsCheck(self, name):
		pass

TextThingie = TextThingieClass(None)

# These are temporary!
RgnHandle = OpaqueByValueType("RgnHandle", "ResObj")
OptRgnHandle = OpaqueByValueType("RgnHandle", "OptResObj")
PicHandle = OpaqueByValueType("PicHandle", "ResObj")
PolyHandle = OpaqueByValueType("PolyHandle", "ResObj")
PixMapHandle = OpaqueByValueType("PixMapHandle", "ResObj")
PixPatHandle = OpaqueByValueType("PixPatHandle", "ResObj")
PatHandle = OpaqueByValueType("PatHandle", "ResObj")
CursHandle = OpaqueByValueType("CursHandle", "ResObj")
CCrsrHandle = OpaqueByValueType("CCrsrHandle", "ResObj")
CIconHandle = OpaqueByValueType("CIconHandle", "ResObj")
CTabHandle = OpaqueByValueType("CTabHandle", "ResObj")
ITabHandle = OpaqueByValueType("ITabHandle", "ResObj")
GDHandle = OpaqueByValueType("GDHandle", "ResObj")
CGrafPtr = OpaqueByValueType("CGrafPtr", "GrafObj")
GrafPtr = OpaqueByValueType("GrafPtr", "GrafObj")
BitMap_ptr = OpaqueByValueType("BitMapPtr", "BMObj")
RGBColor = OpaqueType('RGBColor', 'QdRGB')
RGBColor_ptr = RGBColor
FontInfo = OpaqueType('FontInfo', 'QdFI')

Cursor_ptr = StructInputBufferType('Cursor')
Pattern = StructOutputBufferType('Pattern')
Pattern_ptr = StructInputBufferType('Pattern')
PenState = StructOutputBufferType('PenState')
PenState_ptr = StructInputBufferType('PenState')

includestuff = includestuff + """
#include <%s>""" % MACHEADERFILE + """

#define resNotFound -192 /* Can't include <Errors.h> because of Python's "errors.h" */

/*
** Parse/generate RGB records
*/
PyObject *QdRGB_New(itself)
	RGBColorPtr itself;
{

	return Py_BuildValue("lll", (long)itself->red, (long)itself->green, (long)itself->blue);
}

QdRGB_Convert(v, p_itself)
	PyObject *v;
	RGBColorPtr p_itself;
{
	long red, green, blue;
	
	if( !PyArg_ParseTuple(v, "lll", &red, &green, &blue) )
		return 0;
	p_itself->red = (unsigned short)red;
	p_itself->green = (unsigned short)green;
	p_itself->blue = (unsigned short)blue;
	return 1;
}

/*
** Generate FontInfo records
*/
static
PyObject *QdFI_New(itself)
	FontInfo *itself;
{

	return Py_BuildValue("hhhh", itself->ascent, itself->descent,
			itself->widMax, itself->leading);
}


"""

variablestuff = """
{
	PyObject *o;
 	
	o = QDGA_New();
	if (o == NULL || PyDict_SetItemString(d, "qd", o) != 0)
		Py_FatalError("can't initialize Qd.qd");
}
"""

## not yet...
##
##class Region_ObjectDefinition(GlobalObjectDefinition):
##	def outputCheckNewArg(self):
##		Output("if (itself == NULL) return PyMac_Error(resNotFound);")
##	def outputFreeIt(self, itselfname):
##		Output("DisposeRegion(%s);", itselfname)
##
##class Polygon_ObjectDefinition(GlobalObjectDefinition):
##	def outputCheckNewArg(self):
##		Output("if (itself == NULL) return PyMac_Error(resNotFound);")
##	def outputFreeIt(self, itselfname):
##		Output("KillPoly(%s);", itselfname)

class MyGRObjectDefinition(GlobalObjectDefinition):
	def outputCheckNewArg(self):
		Output("if (itself == NULL) return PyMac_Error(resNotFound);")
	def outputCheckConvertArg(self):
		OutLbrace("if (DlgObj_Check(v) || WinObj_Check(v))")
		Output("*p_itself = ((GrafPortObject *)v)->ob_itself;")
		Output("return 1;")
		OutRbrace()
	def outputGetattrHook(self):
		Output("#ifndef TARGET_API_MAC_CARBON")
		Output("""
		{	CGrafPtr itself_color = (CGrafPtr)self->ob_itself;
		
			if ( strcmp(name, "data") == 0 )
				return PyString_FromStringAndSize((char *)self->ob_itself, sizeof(GrafPort));
				
			if ( (itself_color->portVersion&0xc000) == 0xc000 ) {
				/* Color-only attributes */
			
				if ( strcmp(name, "portBits") == 0 )
					/* XXXX Do we need HLock() stuff here?? */
					return BMObj_New((BitMapPtr)*itself_color->portPixMap);
				if ( strcmp(name, "grafVars") == 0 )
					return Py_BuildValue("O&", ResObj_New, (Handle)itself_color->visRgn);
				if ( strcmp(name, "chExtra") == 0 )
					return Py_BuildValue("h", itself_color->chExtra);
				if ( strcmp(name, "pnLocHFrac") == 0 )
					return Py_BuildValue("h", itself_color->pnLocHFrac);
				if ( strcmp(name, "bkPixPat") == 0 )
					return Py_BuildValue("O&", ResObj_New, (Handle)itself_color->bkPixPat);
				if ( strcmp(name, "rgbFgColor") == 0 )
					return Py_BuildValue("O&", QdRGB_New, &itself_color->rgbFgColor);
				if ( strcmp(name, "rgbBkColor") == 0 )
					return Py_BuildValue("O&", QdRGB_New, &itself_color->rgbBkColor);
				if ( strcmp(name, "pnPixPat") == 0 )
					return Py_BuildValue("O&", ResObj_New, (Handle)itself_color->pnPixPat);
				if ( strcmp(name, "fillPixPat") == 0 )
					return Py_BuildValue("O&", ResObj_New, (Handle)itself_color->fillPixPat);
			} else {
				/* Mono-only attributes */
				if ( strcmp(name, "portBits") == 0 )
					return BMObj_New(&self->ob_itself->portBits);
				if ( strcmp(name, "bkPat") == 0 )
					return Py_BuildValue("s#", (char *)&self->ob_itself->bkPat, sizeof(Pattern));
				if ( strcmp(name, "fillPat") == 0 )
					return Py_BuildValue("s#", (char *)&self->ob_itself->fillPat, sizeof(Pattern));
				if ( strcmp(name, "pnPat") == 0 )
					return Py_BuildValue("s#", (char *)&self->ob_itself->pnPat, sizeof(Pattern));
			}
			/*
			** Accessible for both color/mono windows.
			** portVersion is really color-only, but we put it here
			** for convenience
			*/
			if ( strcmp(name, "portVersion") == 0 )
				return Py_BuildValue("h", itself_color->portVersion);
			if ( strcmp(name, "device") == 0 )
				return PyInt_FromLong((long)self->ob_itself->device);
			if ( strcmp(name, "portRect") == 0 )
				return Py_BuildValue("O&", PyMac_BuildRect, &self->ob_itself->portRect);
			if ( strcmp(name, "visRgn") == 0 )
				return Py_BuildValue("O&", ResObj_New, (Handle)self->ob_itself->visRgn);
			if ( strcmp(name, "clipRgn") == 0 )
				return Py_BuildValue("O&", ResObj_New, (Handle)self->ob_itself->clipRgn);
			if ( strcmp(name, "pnLoc") == 0 )
				return Py_BuildValue("O&", PyMac_BuildPoint, self->ob_itself->pnLoc);
			if ( strcmp(name, "pnSize") == 0 )
				return Py_BuildValue("O&", PyMac_BuildPoint, self->ob_itself->pnSize);
			if ( strcmp(name, "pnMode") == 0 )
				return Py_BuildValue("h", self->ob_itself->pnMode);
			if ( strcmp(name, "pnVis") == 0 )
				return Py_BuildValue("h", self->ob_itself->pnVis);
			if ( strcmp(name, "txFont") == 0 )
				return Py_BuildValue("h", self->ob_itself->txFont);
			if ( strcmp(name, "txFace") == 0 )
				return Py_BuildValue("h", (short)self->ob_itself->txFace);
			if ( strcmp(name, "txMode") == 0 )
				return Py_BuildValue("h", self->ob_itself->txMode);
			if ( strcmp(name, "txSize") == 0 )
				return Py_BuildValue("h", self->ob_itself->txSize);
			if ( strcmp(name, "spExtra") == 0 )
				return Py_BuildValue("O&", PyMac_BuildFixed, self->ob_itself->spExtra);
			/* XXXX Add more, as needed */
			/* This one is so we can compare grafports: */
			if ( strcmp(name, "_id") == 0 )
				return Py_BuildValue("l", (long)self->ob_itself);
		}""")
		Output("#endif")

class MyBMObjectDefinition(GlobalObjectDefinition):
	def outputCheckNewArg(self):
		Output("if (itself == NULL) return PyMac_Error(resNotFound);")
	def outputStructMembers(self):
		# We need to more items: a pointer to privately allocated data
		# and a python object we're referring to.
		Output("%s ob_itself;", self.itselftype)
		Output("PyObject *referred_object;")
		Output("BitMap *referred_bitmap;")
	def outputInitStructMembers(self):
		Output("it->ob_itself = %sitself;", self.argref)
		Output("it->referred_object = NULL;")
		Output("it->referred_bitmap = NULL;")
	def outputCleanupStructMembers(self):
		Output("Py_XDECREF(self->referred_object);")
		Output("if (self->referred_bitmap) free(self->referred_bitmap);")
	def outputGetattrHook(self):
		Output("""if ( strcmp(name, "baseAddr") == 0 )
			return PyInt_FromLong((long)self->ob_itself->baseAddr);
		if ( strcmp(name, "rowBytes") == 0 )
			return PyInt_FromLong((long)self->ob_itself->rowBytes);
		if ( strcmp(name, "bounds") == 0 )
			return Py_BuildValue("O&", PyMac_BuildRect, &self->ob_itself->bounds);
		/* XXXX Add more, as needed */
		if ( strcmp(name, "bitmap_data") == 0 )
			return PyString_FromStringAndSize((char *)self->ob_itself, sizeof(BitMap));
		if ( strcmp(name, "pixmap_data") == 0 )
			return PyString_FromStringAndSize((char *)self->ob_itself, sizeof(PixMap));
		""")
		
# This object is instanciated once, and will access qd globals.
class QDGlobalsAccessObjectDefinition(ObjectDefinition):
	def outputStructMembers(self):
		pass
	def outputNew(self):
		Output()
		Output("%sPyObject *%s_New()", self.static, self.prefix)
		OutLbrace()
		Output("%s *it;", self.objecttype)
		Output("it = PyObject_NEW(%s, &%s);", self.objecttype, self.typename)
		Output("if (it == NULL) return NULL;")
		Output("return (PyObject *)it;")
		OutRbrace()
	def outputConvert(self):
		pass
	def outputCleanupStructMembers(self):
		pass

	def outputGetattrHook(self):
		Output("#ifndef TARGET_API_MAC_CARBON")
		Output("""
	if ( strcmp(name, "arrow") == 0 )
		return PyString_FromStringAndSize((char *)&qd.arrow, sizeof(qd.arrow));
	if ( strcmp(name, "black") == 0 ) 
		return PyString_FromStringAndSize((char *)&qd.black, sizeof(qd.black));
	if ( strcmp(name, "white") == 0 ) 
		return PyString_FromStringAndSize((char *)&qd.white, sizeof(qd.white));
	if ( strcmp(name, "gray") == 0 ) 
		return PyString_FromStringAndSize((char *)&qd.gray, sizeof(qd.gray));
	if ( strcmp(name, "ltGray") == 0 ) 
		return PyString_FromStringAndSize((char *)&qd.ltGray, sizeof(qd.ltGray));
	if ( strcmp(name, "dkGray") == 0 ) 
		return PyString_FromStringAndSize((char *)&qd.dkGray, sizeof(qd.dkGray));
	if ( strcmp(name, "screenBits") == 0 ) 
		return BMObj_New(&qd.screenBits);
	if ( strcmp(name, "thePort") == 0 ) 
		return GrafObj_New(qd.thePort);
	if ( strcmp(name, "randSeed") == 0 ) 
		return Py_BuildValue("l", &qd.randSeed);
		""")
		Output("#endif")

# Create the generator groups and link them
module = MacModule(MODNAME, MODPREFIX, includestuff, finalstuff, initstuff, variablestuff)
##r_object = Region_ObjectDefinition('Region', 'QdRgn', 'RgnHandle')
##po_object = Polygon_ObjectDefinition('Polygon', 'QdPgn', 'PolyHandle')
##module.addobject(r_object)
##module.addobject(po_object)
gr_object = MyGRObjectDefinition("GrafPort", "GrafObj", "GrafPtr")
module.addobject(gr_object)
bm_object = MyBMObjectDefinition("BitMap", "BMObj", "BitMapPtr")
module.addobject(bm_object)
qd_object = QDGlobalsAccessObjectDefinition("QDGlobalsAccess", "QDGA", "XXXX")
module.addobject(qd_object)


# Create the generator classes used to populate the lists
Function = OSErrFunctionGenerator
Method = OSErrMethodGenerator

# Create and populate the lists
functions = []
methods = []
execfile(INPUTFILE)
execfile(EXTRAFILE)

# add the populated lists to the generator groups
# (in a different wordl the scan program would generate this)
for f in functions: module.add(f)
##for f in r_methods: r_object.add(f)
##for f in po_methods: po_object.add(f)

# Manual generator: get data out of a bitmap
getdata_body = """
int from, length;
char *cp;

if ( !PyArg_ParseTuple(_args, "ii", &from, &length) )
	return NULL;
cp = _self->ob_itself->baseAddr+from;
return PyString_FromStringAndSize(cp, length);
"""
f = ManualGenerator("getdata", getdata_body)
f.docstring = lambda: """(int start, int size) -> string. Return bytes from the bitmap"""
bm_object.add(f)

# Manual generator: store data in a bitmap
putdata_body = """
int from, length;
char *cp, *icp;

if ( !PyArg_ParseTuple(_args, "is#", &from, &icp, &length) )
	return NULL;
cp = _self->ob_itself->baseAddr+from;
memcpy(cp, icp, length);
Py_INCREF(Py_None);
return Py_None;
"""
f = ManualGenerator("putdata", putdata_body)
f.docstring = lambda: """(int start, string data). Store bytes into the bitmap"""
bm_object.add(f)

#
# We manually generate a routine to create a BitMap from python data.
#
BitMap_body = """
BitMap *ptr;
PyObject *source;
Rect bounds;
int rowbytes;
char *data;

if ( !PyArg_ParseTuple(_args, "O!iO&", &PyString_Type, &source, &rowbytes, PyMac_GetRect,
		&bounds) )
	return NULL;
data = PyString_AsString(source);
if ((ptr=(BitMap *)malloc(sizeof(BitMap))) == NULL )
	return PyErr_NoMemory();
ptr->baseAddr = (Ptr)data;
ptr->rowBytes = rowbytes;
ptr->bounds = bounds;
if ( (_res = BMObj_New(ptr)) == NULL ) {
	free(ptr);
	return NULL;
}
((BitMapObject *)_res)->referred_object = source;
Py_INCREF(source);
((BitMapObject *)_res)->referred_bitmap = ptr;
return _res;
"""
	
f = ManualGenerator("BitMap", BitMap_body)
f.docstring = lambda: """Take (string, int, Rect) argument and create BitMap"""
module.add(f)

#
# And again, for turning a correctly-formatted structure into the object
#
RawBitMap_body = """
BitMap *ptr;
PyObject *source;

if ( !PyArg_ParseTuple(_args, "O!", &PyString_Type, &source) )
	return NULL;
if ( PyString_Size(source) != sizeof(BitMap) && PyString_Size(source) != sizeof(PixMap) ) {
	PyErr_BadArgument();
	return NULL;
}
ptr = (BitMapPtr)PyString_AsString(source);
if ( (_res = BMObj_New(ptr)) == NULL ) {
	return NULL;
}
((BitMapObject *)_res)->referred_object = source;
Py_INCREF(source);
return _res;
"""
	
f = ManualGenerator("RawBitMap", RawBitMap_body)
f.docstring = lambda: """Take string BitMap and turn into BitMap object"""
module.add(f)

# generate output (open the output file as late as possible)
SetOutputFileName(OUTPUTFILE)
module.generate()
SetOutputFile() # Close it
