#define NPY_NO_DEPRECATED_API NPY_1_7_API_VERSION

// Workaround for GCC<10 bug, see https://github.com/numpy/numpy/issues/16970
#if defined __GNUC__ && !defined __clang__ && __GNUC__ < 10
struct _typeobject {};
#endif

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/halffloat.h>
#include <numpy/ufuncobject.h>

static PyObject* create_numpy_array(PyObject *self, PyObject *args) {
    npy_intp dims[2] = {5, 5};
    PyObject *pyArray = PyArray_SimpleNew(2, dims, NPY_HALF);

    for (int i = 0; i < 5; i++) {
        for (int j = 0; j < 5; j++) {
            *((npy_half *)PyArray_GETPTR2((PyArrayObject *)pyArray, i, j)) = npy_float_to_half((float)i * j);
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
