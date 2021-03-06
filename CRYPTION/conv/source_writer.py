# -*- coding: cp949 -*-

# TODO(tim): Modules should be registered as native python modules.
#            Get rid of this.
def run(moduleLst, libname):
	libname = libname.strip()
	sourceName = "Python%sManager" % libname

	initSource = open("..\\..\\Diamas\\source\\client\\eterXClient\\" + sourceName + ".cpp", "w")
	initHeader = open("..\\..\\Diamas\\source\\client\\eterXClient\\" + sourceName + ".h", "w")

	initSource.write('#pragma once\n')
	initSource.write('#ifdef __USE_CYTHON__\n')
	initSource.write('#include "%s.h"\n' % sourceName)
	initSource.write('\n')
	initSource.write('struct SMethodDef\n')
	initSource.write('{\n')
	initSource.write('	char* func_name;\n')
	initSource.write('	void (*func)();\n')
	initSource.write('};\n')
	initSource.write('\n')
	#
	for moduleName in moduleLst:
		if moduleName == "system":
			continue
		initFunction = "init%s()" % moduleName
		initSource.write("PyMODINIT_FUNC %s;\n" % initFunction)

	initSource.write('\n')
	initSource.write('SMethodDef rootlib_init_methods[] =\n')
	initSource.write('{\n')
	#
	for moduleName in moduleLst:
		initFunction = "init%s" % moduleName
		initSource.write("	{ \"%s\", %s },\n" % (moduleName, initFunction))

	initSource.write('	{ NULL, NULL },\n')
	initSource.write('};\n')
	initSource.write('\n')
	initSource.write('static PyObject* isExist(PyObject *self, PyObject *args)\n')
	initSource.write('{\n')
	initSource.write('	char* func_name;\n')
	initSource.write('\n')
	initSource.write('	if(!PyArg_ParseTuple(args, "s", &func_name))\n')
	initSource.write('		return NULL;\n')
	initSource.write('\n')
	initSource.write('	for (int i = 0; NULL != rootlib_init_methods[i].func_name;i++)\n')
	initSource.write('	{\n')
	initSource.write('		if (0 == strcmp(rootlib_init_methods[i].func_name, func_name))\n')
	initSource.write('		{\n')
	initSource.write('			return Py_BuildValue("i", 1);\n')
	initSource.write('		}\n')
	initSource.write('	}\n')
	initSource.write('	return Py_BuildValue("i", 0);\n')
	initSource.write('}\n')
	initSource.write('\n')
	initSource.write('static PyObject* import(PyObject *self, PyObject *args)\n')
	initSource.write('{\n')
	initSource.write('	char* func_name;\n')
	initSource.write('\n')
	initSource.write('	if(!PyArg_ParseTuple(args, "s", &func_name))\n')
	initSource.write('		return NULL;\n')
	initSource.write('\n')
	initSource.write('	for (int i = 0; NULL != rootlib_init_methods[i].func_name;i++)\n')
	initSource.write('	{\n')
	initSource.write('		if (0 == strcmp(rootlib_init_methods[i].func_name, func_name))\n')
	initSource.write('		{\n')
	initSource.write('			rootlib_init_methods[i].func();\n')
	initSource.write('			if (PyErr_Occurred())\n')
	initSource.write('				return NULL;\n')
	initSource.write('			PyObject* m = PyDict_GetItemString(PyImport_GetModuleDict(), func_name);\n')
	initSource.write('			if (m == NULL) {\n')
	initSource.write('				PyErr_SetString(PyExc_SystemError,\n')
	initSource.write('					"dynamic module not initialized properly");\n')
	initSource.write('				return NULL;\n')
	initSource.write('			}\n')
	initSource.write('			Py_INCREF(m);\n')
	initSource.write('			return Py_BuildValue("S", m);\n')
	initSource.write('		}\n')
	initSource.write('	}\n')
	initSource.write('	return NULL;\n')
	initSource.write('}\n')
	initSource.write('\n')
	initSource.write('\n')
	initSource.write('void init%sManager()\n' % libname)
	initSource.write('{\n')
	initSource.write('	static struct PyMethodDef methods[] =\n')
	initSource.write('	{\n')
	initSource.write('		{"isExist", isExist, METH_VARARGS},\n')
	initSource.write('		{"moduleImport", import, METH_VARARGS},\n')
	initSource.write('		{nullptr, nullptr, 0},\n')
	initSource.write('	};\n')
	initSource.write('\n')
	initSource.write('	Py_InitModule("%s", methods);\n' % libname)
	initSource.write('}\n')
	initSource.write('#endif\n')
	
	initHeader.write('#pragma once\n')
	initHeader.write('#include <python27/Python.h>\n')
	initHeader.write('\n')
	initHeader.write("/* %s module */\n" % libname)
	initHeader.write("/* %s.isExist */\n" % libname)
	initHeader.write("/* %s.moduleImport */\n" % libname)
	initHeader.write("/* this lib includes modules under this lines.\n")
	for moduleName in moduleLst:
		initHeader.write("	%s\n" % moduleName)
	initHeader.write("*/\n")
	initHeader.write('#ifdef __USE_CYTHON__\n')
	initHeader.write('	PyMODINIT_FUNC initsystem();\n')
	initHeader.write('#endif\n')
	initHeader.write('\n')
	initHeader.write('void init%sManager();\n' % libname)

	
	return sourceName