// Based on https://github.com/numpy/numpy/blob/v1.26.0/numpy/core/tests/examples/limited_api/limited_api.c

#define Py_LIMITED_API 0x03060000

#include <Python.h>
#include <numpy/arrayobject.h>
#include <numpy/ufuncobject.h>

static PyModuleDef moduledef = {
    .m_base = PyModuleDef_HEAD_INIT,
    .m_name = "limited_api"
};

PyMODINIT_FUNC PyInit_limited_api(void)
{
    import_array();
    import_umath();
    return PyModule_Create(&moduledef);
}
