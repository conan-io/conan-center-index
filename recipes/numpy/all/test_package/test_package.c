#define Py_LIMITED_API 0x03060000
#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/ufuncobject.h>

static PyObject* create_numpy_array(PyObject *self, PyObject *args) {
    npy_intp dims[2] = {5, 5};
    PyObject *pyArray = PyArray_SimpleNew(2, dims, NPY_FLOAT64);

    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            *((double *)PyArray_GETPTR2(pyArray, i, j)) = (double)i * j;
        }
    }

    return pyArray;
}

static PyMethodDef ExampleMethods[] = {
    {"create_numpy_array",  create_numpy_array, METH_VARARGS, "Create a 2D NumPy array."},
    {NULL, NULL, 0, NULL}
};

static PyModuleDef moduledef = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "test_package",
    .m_methods = ExampleMethods,
};

PyMODINIT_FUNC PyInit_test_package(void)
{
    import_array();
    import_umath();
    return PyModule_Create(&moduledef);
}
