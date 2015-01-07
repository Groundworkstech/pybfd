//
// Python wrapper for PyBFD (libbfd & libopcodes extension module)
//
// Copyright (c) 2013 Groundworks Technologies
//

#include <Python.h>

#include <stdio.h>
#include <stdarg.h>
#include <string.h>

#include "bfd_headers.h"

#ifdef __APPLE__
// TODO : Make sure this kludge can't be fixed otherwise.
// This is required by OSX because is'nt defined by the loader.
char** environ;
#endif

//
// Name     : get_symbols
//
// Purpose  : Transfer all symbolic information into python objects for further
//              usage.
//
// Params   :   @abfd : The current BFD.
//              @py_symbol_list : Ths destination list containing the symbols.
//
// Returns  : On success return the total number of symbols found (could be 0).
//              On error returns -1.
//
int
get_symbols(bfd* abfd, PyObject** py_symbol_list) {
    long storage_needed_static,
        storage_needed_dynamic,
        number_of_symbols_static,
        number_of_symbols_dynamic,
        i;

    asymbol **symbol_table;

    asymbol *symbol;

    // Create a python list to hold all the symbols representations.
    if (!(*py_symbol_list = PyList_New(0)))
        return -1;

    // Calculate the space necessary to hold all the symbolic information.
    storage_needed_static = bfd_get_symtab_upper_bound (abfd);
    storage_needed_dynamic = bfd_get_dynamic_symtab_upper_bound (abfd);

    if (storage_needed_static + storage_needed_dynamic <= 0)
        return -1;

    symbol_table = (asymbol **) malloc(
        storage_needed_static + storage_needed_dynamic);

    number_of_symbols_static = 
        bfd_canonicalize_symtab(abfd, symbol_table);

    number_of_symbols_dynamic =
        bfd_canonicalize_dynamic_symtab(
            abfd, &symbol_table[number_of_symbols_static]);

    // Make sure we've got some symbols. Otherwise return.
    if (number_of_symbols_static + number_of_symbols_dynamic < 0) {
        // Release unused symbol table and return.
        if (symbol_table)
            free (symbol_table);

        return -1;
    }

    for (i = 0; i < number_of_symbols_static + number_of_symbols_dynamic; i++) {
        
        symbol = symbol_table[i];

        PyList_Append(*py_symbol_list,
            Py_BuildValue(
                "(Is" PYBFD_SYMBOL_VALUE_FMT PYBFD_SYMBOL_FLAG_FMT ")",
                symbol->section->index,
                symbol->name,
                symbol->value,
                symbol->flags
            ));
    }

    // Release symbol tabel because we don't need it anymore.
    if (symbol_table)
        free(symbol_table);

    return number_of_symbols_static + number_of_symbols_dynamic;

}

// ---------------------- Begin of Python Layer -------------------
//
// Name     : pybfd_get_symbols
//
// Purpose  : 
//
// Params   :
//
// Returns  : 
//
static PyObject *
pybfd_get_symbols(PyObject *self, PyObject *args) {
    bfd* abfd;
    PyObject* py_symbol_list = NULL;

    int symbols_count;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        if (!abfd) {
            // An error ocurred receviing the bfd struct.
            PyErr_SetNone(PyExc_IOError);
        }
        else {
            symbols_count = get_symbols(abfd, &py_symbol_list);

            if (symbols_count >= 0) {
                // Seems that we've got a the symbols after all!!!
                return Py_BuildValue("O", py_symbol_list);
            }

            PyErr_SetString(PyExc_TypeError, "Unable to get symbols.");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_openr
//
// Purpose  : Create a BFD structure from a given a filename and target
//              architecture specified. Open for reading!
//
// Params   :   @filename : file to open.
//              @target : bfd target architecture.
//
// Returns  : A BFD* when successfull or raise on error.
//
static PyObject *
pybfd_openr(PyObject *self, PyObject *args) {
    bfd* abfd;

    const char* filename;
    const char* target;

    if (PyArg_ParseTuple(args, "ss", &filename, &target)) {
        abfd = bfd_openr(filename, NULL);

        if (!abfd) {
            // An error ocurred trying to open the file.
            PyErr_SetString(PyExc_IOError, bfd_errmsg(bfd_get_error()));
        }
        else {
            return Py_BuildValue("n", abfd);
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_fdopenr
//
// Purpose  : Create a BFD structure from a given a file descriptor and target
//              architecture specified. Open for reading!
//
// Params   :   @filename : Name of the file being opened.
//              @target : bfd target architecture.
//              @fd : File descriptor in use for the file.
//
// Returns  : A BFD* when successfull or raise on error.
//
static PyObject *
pybfd_fdopenr(PyObject *self, PyObject *args) {
    bfd* abfd;

    const char* filename;
    const char* target;
    int fd;

    if (PyArg_ParseTuple(args, "ssi", &filename, &target, &fd)) {
        abfd = bfd_fdopenr(filename, NULL, fd);

        if (!abfd) {
            // An error ocurred trying to open the file.
            PyErr_SetString(PyExc_IOError, bfd_errmsg(bfd_get_error()));
        }
        else {
            return Py_BuildValue("n", abfd);
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_close
//
// Purpose  : close the specified bfd structure.
//
// Params   :   @abfd : Current bfd structure.
//
// Returns  : None
//
static PyObject *
pybfd_close(PyObject *self, PyObject *args) {
    //
    // Close the specified BFD object.
    //
    bfd* abfd;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            if (bfd_close(abfd) == TRUE) {
                Py_RETURN_NONE;
            }

            PyErr_SetString(PyExc_TypeError, "Unable to close BFD.");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_check_format
//
// Purpose  : Initialize the format for an opened a BFD structure for further
//              operations.
//
// Params   :   @abfd : Already open bfd.
//              @format : bfd file format.
//
// Returns  : A BFD* when successfull or raise on error.
//
static PyObject *
pybfd_check_format(PyObject *self, PyObject *args) {
    bfd* abfd;

    bfd_format* format;

    if (PyArg_ParseTuple(args, "ni", &abfd, &format)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            if (bfd_check_format(abfd, (bfd_format)format)) {
                Py_RETURN_TRUE;
            }
            Py_RETURN_FALSE;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_archive_list_filenames
//
// Purpose  : Return a list of filenames inside an archive.
//
// Params   : @abfd : bfd of archive file.
//
// Returns  : A list of filenames inside the archive.
//
static PyObject *
pybfd_archive_list_filenames(PyObject *self, PyObject *args) {
    bfd* abfd;
    bfd* next_one = NULL;
    bfd* last_arfile = NULL;

    PyObject* list = NULL;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
            return NULL;
        }

        // Create a python list with a preexisting number of archs as its
        // items.
        if (!(list = PyList_New(0))) {
            PyErr_SetString(
                PyExc_TypeError, 
                "Unable to create matches list.");

            return NULL;
        }

        // Read all the contents right away, regardless.
        for (next_one = bfd_openr_next_archived_file (abfd, NULL);
            next_one;
            next_one = bfd_openr_next_archived_file (abfd, next_one)) {
                // We've got a new Bfd pointing inside the archive. That means
                // that a new file was found in there.
                if (PyList_Append(
                    list, Py_BuildValue("s", bfd_get_filename(next_one))) == -1) {

                    bfd_close (next_one);

                    PyErr_SetString(PyExc_TypeError,
                        "Unable to append filename to archive list.");
                    return NULL;
                }

                last_arfile = next_one;

                bfd_close(last_arfile);
            }

        last_arfile = (bfd *) NULL;

        if (bfd_get_error () != bfd_error_no_more_archived_files) {
            // Something went wrong so we inform of that instead of
            // returning the list.
            PyErr_SetString(PyExc_TypeError,
                            bfd_errmsg(bfd_get_error()));

            // TODO: Remove the list created so far.
            list = NULL;
        }

    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    if (last_arfile != NULL)
        bfd_close(last_arfile);

    return list;
}


//
// Name     : pybfd_archive_list_files
//
// Purpose  : Return a list of BFDs inside an archive.
//
// Params   : @abfd : bfd of archive file.
//
// Returns  : A list of BFDs inside the archive.
//
static PyObject *
pybfd_archive_list_files(PyObject *self, PyObject *args) {
    bfd* abfd;
    bfd* next_one = NULL;

    PyObject* list = NULL;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
            return NULL;
        }

        // Create a python list with a preexisting number of archs as its
        // items.
        if (!(list = PyList_New(0))) {
            PyErr_SetString(
                PyExc_TypeError, 
                "Unable to create matches list.");

            return NULL;
        }

        // Read all the contents right away, regardless.
        for (next_one = bfd_openr_next_archived_file (abfd, NULL);
            next_one;
            next_one = bfd_openr_next_archived_file (abfd, next_one)) {
                // We've got a new Bfd pointing inside the archive. That means
                // that a new file was found in there.
                if (PyList_Append(
                    list, Py_BuildValue("n", next_one)) == -1) {

                    PyErr_SetString(PyExc_TypeError,
                        "Unable to append BFD to archive list.");
                    return NULL;
                }

            }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return list;
}

//
// Name     : pybfd_check_format_matches
//
// Purpose  : Return a list of matching formats for current bfd.
//
// Params   :   @abfd : Already open bfd.
//              @format : bfd file format.
//
// Returns  : A list of matches.
//
static PyObject *
pybfd_check_format_matches(PyObject *self, PyObject *args) {
    bfd* abfd;
    bfd_format* format;

    PyObject* list = NULL;
    // TODO: Remove this fixed value and re-test all this routine.
    char **matching;

    if (PyArg_ParseTuple(args, "ni", &abfd, &format)) {

        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            if (bfd_check_format_matches(abfd, (bfd_format)format,
                &matching)) {

                Py_RETURN_TRUE;
            }
            else {
                if (bfd_get_error() == bfd_error_file_ambiguously_recognized) {

                    // Create a python list with a preexisting number of archs
                    // as it items.
                    if (!(list = PyList_New(0))) {
                        PyErr_SetString(
                            PyExc_TypeError, 
                            "Unable to create matches list.");

                        return NULL;
                    }

                    // Use matching list.

                    free(matching);
                }

                Py_RETURN_FALSE;
            }
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_set_error
//
// Purpose  : Set the internal BFD error code.
//
// Params   : New error code (one of bfd_error_type) 
//
// Returns  : -
//
static PyObject *
pybfd_set_error(PyObject *self, PyObject *args) {

    bfd_error_type* error_tag;

    if (PyArg_ParseTuple(args, "i", &error_tag)) {

        // Validate the passes eror code.
        if ((bfd_error_type)error_tag > bfd_error_invalid_error_code) {
            PyErr_SetString(PyExc_TypeError, "Invalid eror code specified.");
        }
        else {
            bfd_set_error((bfd_error_type)error_tag);
            Py_RETURN_NONE;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_get_error
//
// Purpose  : Return the internal BFD error code.
//
// Params   : - 
//
// Returns  : A value of type bfd_error_type.
//
static PyObject *
pybfd_get_error(PyObject *self, PyObject *args) {
    return Py_BuildValue("i", bfd_get_error());
}

//
// Name     : pybfd_get_last_error_message
//
// Purpose  : Return the lastest internal BFD error message.
//
// Params   : -
//
// Returns  : A string with error message according to the last bfd_get_error()
//              value returned.
//
static PyObject *
pybfd_get_last_error_message(PyObject *self, PyObject *args) {
    return Py_BuildValue("s", bfd_errmsg(bfd_get_error()));
}

//
// Name     : pybfd_get_error_message
//
// Purpose  : Return the internal BFD error message.
//
// Params   : error_code = a bfd_error_type value.
//
// Returns  : A string with error message.
//
static PyObject *
pybfd_get_error_message(PyObject *self, PyObject *args) {

    bfd_error_type err;

    if (PyArg_ParseTuple(args, "i", &err)) {

        if (err == bfd_error_no_error) {
            Py_RETURN_NONE;
        }
        else {
            return Py_BuildValue("s", bfd_errmsg(err));
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_get_sections_list
//
// Purpose  : 
//
// Params   : -
//
// Returns  : -
//
static PyObject *
pybfd_get_sections_list(PyObject *self, PyObject *args) {
    bfd* abfd;
    asection* section;

    PyObject* result = NULL;
    PyObject* list = NULL;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {

            // Create a python list with a preexisting number of sections as its
            // size.
            if (!(list = PyList_New(abfd->section_count)))
                return NULL;

            for (section = abfd->sections; section; section = section->next) {
                PyList_SetItem(list, section->index, Py_BuildValue("n", section));
            }

            result = list;
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;
}

//
// Name     : pybfd_arch_list
//
// Purpose  : Return a list of the currently supported arch architectures.
//
// Params   : None
//
// Returns  : A list of arch architecture names.
//
static PyObject *
pybfd_arch_list(PyObject *self, PyObject *args) {
    PyObject* list = NULL;

    // Get a list of supported archs.
    const char** archs = bfd_arch_list();
    const char** arch = archs;

    // Create a python list with a preexisting number of archs as its
    // items.
    if (!(list = PyList_New(0)))
        return NULL;

    for ( ; *arch != NULL; arch++) {
        if (PyList_Append(list, Py_BuildValue("s", *arch)) == -1)
            return NULL;
    }

    // Release archs char array.
    if (archs)
        free (archs);

    return list;
}


//
// Name     : pybfd_target_list
//
// Purpose  : Return a list of the currently supported target architectures.
//
// Params   : None
//
// Returns  : A list of target architecture names.
//
static PyObject *
pybfd_target_list(PyObject *self, PyObject *args) {
    PyObject* list = NULL;

    // Get a list of supported targets.
    const char** targets = bfd_target_list();
    const char** target = targets;

    // Create a python list with a preexisting number of targets as its
    // items.
    if (!(list = PyList_New(0))) {
        PyErr_SetString(
            PyExc_TypeError, 
            "Unable to create matches list.");
    }

    for ( ; *target != NULL; target++) {
        if (PyList_Append(list, Py_BuildValue("s", *target)) == -1)
            return NULL;
    }

    // Release targets char array.
    if (targets)
        free (targets);

    return list;
}

//
// Name     : pybfd_get_section_attribute
//
// Purpose  : Return the requested attribute from the specified bfd section.
//
// Params   :   @bfd : a bfd structure.
//
// Returns  : Section attribute value.
//
enum {
    INDEX = 0,
    NAME,
    SIZE,
    VMA,
    LMA,
    ALIGNMENT,
    FLAGS,
    FILE_POS,
    ENTSIZE
} section_attributes;

static PyObject *
pybfd_get_section_attribute(PyObject *self, PyObject *args) {
    asection* section;
    int attribute_index;

    PyObject* result = NULL;

    if (PyArg_ParseTuple(args, "ni", &section, &attribute_index)) {

        switch (attribute_index) {
        case INDEX:
            result = Py_BuildValue("i", section->index);
            break;

        case NAME:
            result = Py_BuildValue("s", section->name);
            break;

        case SIZE:
            result = Py_BuildValue("i", section->size);
            break;

        case VMA:
            result = Py_BuildValue("i", section->vma);
            break;

        case LMA:
            result = Py_BuildValue("i", section->lma);
            break;

        case ALIGNMENT:
            result = Py_BuildValue("i", section->alignment_power);
            break;

        case FLAGS:
            result = Py_BuildValue("i", section->flags);
            break;

        case FILE_POS:
            result = Py_BuildValue("i", section->filepos);
            break;

        case ENTSIZE:
            result = Py_BuildValue("i", section->entsize);
            break;

        default:
            PyErr_SetString(
                PyExc_TypeError, "Invalid section attribute requested.");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;
}

//
// Name     : pybfd_bfd_get_attribute
//
// Purpose  : Return the requested attribute from the specified bfd.
//
// Params   :   @bfd : a bfd structure.
//
// Returns  : bfd attribute value.
//
enum {
    FILENAME = 0,
    CACHEABLE,
    FORMAT,
    TARGET,
    FLAVOUR,
    FAMILY_COFF,
    IS_BIG_ENDIAN,
    IS_LITTLE_ENDIAN,
    HEADER_BIG_ENDIAN,
    HEADER_LITTLE_ENDIAN,
    FILE_FLAGS,
    APPLICABLE_FILE_FLAGS,
    APPLICABLE_SECTION_FLAGS,
    MY_ARCHIEVE,
    HAS_MAP,
    IS_THIN_ARCHIEVE,
    HAS_GAP_IN_ELF_SHNDX,
    VALID_RELOC_TYPES,
    USRDATA,
    START_ADDRESS,
    SYMCOUNT,
    OUTSYMBOLS,
    COUNT_SECTIONS,
    DYNAMIC_SYMCOUNT,
    SYMBOL_LEADING_CHAR,
} bfd_attributes;

static PyObject *
pybfd_get_bfd_attribute(PyObject *self, PyObject *args) {
    bfd* abfd;
    int attribute_index;

    PyObject* result = NULL;

    if (PyArg_ParseTuple(args, "ni", &abfd, &attribute_index)) {

        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }

        switch (attribute_index) {
        case FILENAME:
            result = Py_BuildValue("s", bfd_get_filename(abfd));
            break;

        case CACHEABLE:
            result = Py_BuildValue("i", bfd_get_cacheable(abfd));
            break;

        case FORMAT:
            result = Py_BuildValue("i", bfd_get_format(abfd));
            break;

        case TARGET:
            result = Py_BuildValue("s", bfd_get_target(abfd));
            break;

        case FLAVOUR:
            result = Py_BuildValue("i", bfd_get_flavour(abfd));
            break;

        case FAMILY_COFF:
            result = Py_BuildValue("i", bfd_family_coff(abfd));
            break;

        case IS_BIG_ENDIAN:
            result = Py_BuildValue("i", bfd_big_endian(abfd));
            break;

        case IS_LITTLE_ENDIAN:
            result = Py_BuildValue("i", bfd_little_endian(abfd));
            break;

        case HEADER_BIG_ENDIAN:
            result = Py_BuildValue("i", bfd_header_big_endian(abfd));
            break;

        case HEADER_LITTLE_ENDIAN:
            result = Py_BuildValue("i", bfd_header_little_endian(abfd));
            break;

        case FILE_FLAGS:
            result = Py_BuildValue("i", bfd_get_file_flags(abfd));
            break;

        case APPLICABLE_FILE_FLAGS:
            result = Py_BuildValue("i", bfd_applicable_file_flags(abfd));
            break;

        case APPLICABLE_SECTION_FLAGS:
            result = Py_BuildValue("i", bfd_applicable_section_flags(abfd));
            break;

        case MY_ARCHIEVE:
            result = Py_BuildValue("i", bfd_my_archive(abfd));
            break;

        case HAS_MAP:
            result = Py_BuildValue("i", bfd_has_map(abfd));
            break;

        case IS_THIN_ARCHIEVE:
            result = Py_BuildValue("i", bfd_is_thin_archive(abfd));
            break;

        //case HAS_GAP_IN_ELF_SHNDX:
        //    result = Py_BuildValue("i", bfd_has_gap_in_elf_shndx(abfd));
        //    break;

        // Not necessary at the moment.
        // #define is present in bfd.h but bfd_target struct doesn't have the
        // member. Weird?!
        //case VALID_RELOC_TYPES:
        //    result = Py_BuildValue("i", bfd_valid_reloc_types(abfd));
        //    break;

        case USRDATA:
            result = Py_BuildValue("i", bfd_usrdata(abfd));
            break;

        case START_ADDRESS:
            result = Py_BuildValue("i", bfd_get_start_address(abfd));
            break;

        case SYMCOUNT:
            result = Py_BuildValue("i", bfd_get_symcount(abfd));
            break;

        case OUTSYMBOLS:
            result = Py_BuildValue("i", bfd_get_outsymbols(abfd));
            break;

        case COUNT_SECTIONS:
            result = Py_BuildValue("i", bfd_count_sections(abfd));
            break;

        case DYNAMIC_SYMCOUNT:
            result = Py_BuildValue("i", bfd_get_dynamic_symcount(abfd));
            break;

        case SYMBOL_LEADING_CHAR:
            result = Py_BuildValue("i", bfd_get_symbol_leading_char(abfd));
            break;

        default:
            PyErr_SetString(
                PyExc_TypeError, "Invalid BFD attribute requested.");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;
}

//
// Name     : pybfd_set_file_flags
//
// Purpose  : Set the flag word in the BFD abfd to the value flags.
//
// Params   :   abfd : The BFD in use.
//              file_flags : New flags to set.
//
// Returns  : None on success or raises on error.
//
static PyObject *
pybfd_set_file_flags(PyObject *self, PyObject *args) {

    bfd* abfd;
    int file_flags;

    PyObject* result = NULL;

    if (PyArg_ParseTuple(args, "ni", &abfd, &file_flags)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            if (bfd_set_file_flags(abfd, file_flags)) {
                Py_RETURN_NONE;
            }
            PyErr_SetString(PyExc_TypeError, "Unable to set value(s)");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;
}

//
// Name     : pybfd_set_start_address
//
// Purpose  : Set the value in the BFD abfd to the start address field.
//
// Params   :   abfd : The BFD in use.
//              start_address : New start address to set.
//
// Returns  : None on success or raises on error.
//
static PyObject *
pybfd_set_start_address(PyObject *self, PyObject *args) {
    bfd* abfd;
    int start_address;

    PyObject* result = NULL;

    if (PyArg_ParseTuple(args, "ni", &abfd, &start_address)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            if (bfd_set_start_address(abfd, start_address)) {
                Py_RETURN_NONE;
            }
            PyErr_SetString(PyExc_TypeError, "Unable to set value(s)");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;
}

// Name     : pybfd_get_gp_size
//
// Purpose  : Set the value in the BFD abfd to the GP size field.
//
// Params   :   abfd : The BFD in use.
//              gp_size : New GP size to get.
//
// Returns  : None on success or raises on error.
//
static PyObject *
pybfd_get_gp_size(PyObject *self, PyObject *args) {
    bfd* abfd;

    PyObject* result = NULL;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            return Py_BuildValue("I", bfd_get_gp_size(abfd));
        }
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return result;
}

// Name     : pybfd_set_gp_size
//
// Purpose  : Set the value in the BFD abfd to the GP size field.
//
// Params   :   abfd : The BFD in use.
//              gp_size : New GP size to set.
//
// Returns  : None on success or raises on error.
//
static PyObject *
pybfd_set_gp_size(PyObject *self, PyObject *args) {
    bfd* abfd;
    int gp_size;

    PyObject* result = NULL;

    if (PyArg_ParseTuple(args, "ni", &abfd, &gp_size)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            bfd_set_gp_size(abfd, gp_size);
            Py_RETURN_NONE;
        }
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return result;
}

//
// Name     :
//
// Purpose  : Set the default BFD target based on the configured target.  Doing
//              this permits the binutils to be configured for a particular
//              target, and linked against a shared BFD library which was
//              configured for a different target.
//
// Params   : -
//
// Returns  : -
//
static PyObject *
pybfd_get_arch_size(PyObject *self, PyObject *args) {
    bfd* abfd;
    unsigned int arch_size = 0;

    PyObject* result  = NULL;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            //
            // Ask BFD the current architecture size in bits.
            //
            // TODO: Check if we're working with a ELF BFD.
            // Return the arch_size field of an elf bfd, or -1 if not elf.
            arch_size = bfd_get_arch_size(abfd);

            if (arch_size) {
                result = Py_BuildValue("i", arch_size);
            }
            else {
                PyErr_SetString(PyExc_TypeError,
                    "Unable to get architecure size");
            }
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;
}

//
// Name     : pybfd_find_target
//
// Purpose  : Find the default BFD target based on the configured target. 
//
// Params   :   target : String representing the target name.
//              abfd : bfd structure.
//
// Returns  : -
//
static PyObject *
pybfd_find_target(PyObject *self, PyObject *args) {
    bfd* abfd;
    const char* target;
    const bfd_target* target_list;

    if (PyArg_ParseTuple(args, "ns", &abfd, &target)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            target_list = bfd_find_target(target, abfd);

            if (target_list) {
                // TODO
                Py_RETURN_NONE;
            }
            PyErr_SetString(PyExc_TypeError, "Unable to set value(s)");
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_set_default_target
//
// Purpose  : Set the default BFD target based on the configured target.  Doing
//              this permits the binutils to be configured for a particular
//              target, and linked against a shared BFD library which was
//              configured for a different target.
//
// Params   : -
//
// Returns  : -
//
static PyObject *
pybfd_set_default_target(PyObject *self, PyObject *args) {
    const char* target;

    if (PyArg_ParseTuple(args, "s", &target)) {
        if (bfd_set_default_target (target)) {
            Py_RETURN_NONE;
        }
        PyErr_SetString(PyExc_TypeError, "Unable to set value(s)");
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : pybfd_section_get_content
//
// Purpose  : -
//
// Params   :   bfd
//              section
//              offset
//              count
//
// Returns  : -
//
static PyObject *
pybfd_section_get_content(PyObject *self, PyObject *args) {
    bfd* abfd;
    asection* section;
    unsigned int offset;
    unsigned int count;
    bfd_byte* content;

    PyObject* result  = NULL;

    if (PyArg_ParseTuple(args, "nnII", &abfd, &section, &offset, &count)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            content = (bfd_byte*) malloc(count);

            if (content) {
                if (bfd_get_section_contents(
                    abfd, section, content, offset, count)) {
                    result = Py_BuildValue("s#", content, count);
                }

                free(content);
            }
            else {
                PyErr_SetString(PyExc_TypeError, "Unable to set value(s)");
            }
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return result;

}

//
// Name     : pybfd_get_architecture
//
// Purpose  :  Return the current architecture value.
//
// Params   :   @abfd : The current bfd.
//
// Returns  : The current architecture value stored.
//
static PyObject *
pybfd_get_architecture(PyObject *self, PyObject *args) {
    bfd* abfd;

    if (PyArg_ParseTuple(args, "n", &abfd)) {
        // Validate the BFD pointer passes.
        if (!abfd) {
            PyErr_SetString(PyExc_TypeError, "Null BFD pointer specified");
        }
        else {
            return Py_BuildValue("i", bfd_get_arch(abfd));
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Name     : initialize
//
// Purpose  : Initialize BFD library and any other internal functionallity in
//              order to use libbfd.
//
// Params   : -
//
// Returns  : -
//
void
initialize(void) {
    // Internal BFD initialization.
    bfd_init();
}

//
// Define methods
//
static struct PyMethodDef _bfd_methods[] = { 
#define declmethod(func,h) { #func , ( PyCFunction )pybfd_##func , METH_VARARGS , h }
    declmethod(openr, "Create a BFD for file reading."),
    declmethod(fdopenr, "Create a BFD for file reading (from file descriptor)."),
    declmethod(check_format, "Initialize the file format of the BFD."),
    declmethod(check_format_matches, "Initialize the file format of the BFD and return list of matches if ambiguous format exists."),
    declmethod(close, "Close current BFD."),
    declmethod(get_error, "Return the internal BFD error code."),
    declmethod(archive_list_files, "Return a list with the BFD files inside an archive."),
    declmethod(archive_list_filenames, "Return a list with the filenames inside an archive."),
    declmethod(set_error, "Set the internal BFD error code."),
    declmethod(get_error_message, "Return the internal BFD error message."),
    declmethod(get_last_error_message, "Return the latest internal BFD error message."),
    declmethod(find_target, "Find the BFD target architecture."),
    declmethod(set_default_target, "Set the default BFD target architecture."),
    declmethod(get_sections_list, "Return a list of bfd section pointers."),
    declmethod(get_arch_size, "Return the target architecture size in bits"),
    declmethod(get_section_attribute, "Return the requested attribute from the specified bfd section."),
    declmethod(target_list, "Return a list of all the supported targets."),
    declmethod(arch_list, "Return a list of all the supported architectures."),
    declmethod(get_bfd_attribute, "Return the requested attribute from the specified bfd."),
    declmethod(set_file_flags, "Set the flag word in the BFD abfd to the value flags."),
    declmethod(set_start_address, "Set the address in the BFD abfd to the start address."),
    declmethod(get_gp_size, "Return the maximum size of objects to be optimized using the GP register under ECOFF or MIPS ELF."),
    declmethod(set_gp_size, "Set the maximum size of objects to be optimized using the GP register under ECOFF or MIPS ELF."),
    declmethod(section_get_content, "Return the section specified content."),
    declmethod(get_symbols, "Return the complete list of available symbols."),
    declmethod(get_architecture, "Return the current architecture Id."),
    {NULL},
#undef declmethod
};

//
// Name     : init_pybfd
//
// Purpose  : Initialize Python extension module and BFD specifics.
//
// Params   : -
//
// Returns  : -
//
PyMODINIT_FUNC init_bfd(void) {
    if (!Py_InitModule("_bfd", _bfd_methods))
        return;

    // Initialize current library.
    initialize();
}
