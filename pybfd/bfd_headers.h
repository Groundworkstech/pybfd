//
// Python wrapper for PyBFD (libbfd & libopcodes extension module)
//
// Copyright (c) 2013 Groundworks Technologies
//

#ifndef PYBFD_HEADERS
#define PYBFD_HEADERS

#define PACKAGE "pybfd"
#define PACKAGE_VERSION "0.1"

#include <dis-asm.h>

#define PYBFD_SYMBOL_VALUE_FMT "k" // unsigned long
#define PYBFD_SYMBOL_FLAG_FMT "I" // typedef unsigned int flagword;	/* 32 bits of flags */

#ifdef BFD64
#define PY_VMA_FMT "L" /* unsigned long */
#else
#define PY_VMA_FMT "L" /* unsigned long */
#endif /* noy BFD64 */

//
// List of Python callback function return values.
//
enum PYBFD_DISASM_CALLBACK_RESULT {
    PYBFD_DISASM_CONTINUE = 0,
    PYBFD_DISASM_STOP
};

#endif /* PYBFD_HEADERS */
