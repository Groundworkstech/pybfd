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
#include "supported_disasm.h"

//
// Structure to allow the disassembly of multiple formarts simultaneously.
//
// Pseudo FILE object for strings.  */
typedef struct
{
  char* buffer;
  size_t pos;
  size_t alloc;

} SFILE;

int ATTRIBUTE_PRINTF_2
__disassemle_printf (SFILE *f, const char *format, ...);

typedef struct
{
    disassemble_info dinfo;

    disassembler_ftype pfn_disassemble;

    SFILE sfile;

} disassembler_pointer, *p_disassembler_pointer;


//
// Functions declarations
// 
disassembler_ftype
get_disassemble_function(   unsigned long long ull_arch,
                            unsigned long ul_endian);

//int
PyObject*
disassemble(disassembler_pointer*   pdisasm_ptr);

// Name     : initialize_opcodes
disassembler_pointer* initialize_opcodes(void);

//
// Name     : get_disassemble_function
//
// Purpose  : Iterate through our list of supported architectures looking for
//              the correct disassembly function set according to the
//              user-specified endianess.
//
// Params   : -
//
disassembler_ftype
get_disassemble_function(   unsigned long long ull_arch,
                            unsigned long ul_endian)
{
    unsigned int i;

    //
    //
    for (i = 0; p_supported_disasm_list[i].bfd_arch != bfd_arch_last; i++)
    {
        if (p_supported_disasm_list[i].bfd_arch == ull_arch) {
            if (ul_endian == BFD_ENDIAN_BIG) {
                return p_supported_disasm_list[i].bfd_print_insn_endian_big;
            }
            else
            {
                // Fallback on unknown endian or architectures with just
                //  one endianess.
                return p_supported_disasm_list[i].bfd_print_insn_endian_little;
            }
        }
    }

    return (disassembler_ftype)NULL;
}

//
// Name     : initialize_opcodes
//
// Purpose  : Initialize internal structures.
//
// Params   : -
//
// Returns  : A newly created disassembler_pointer structure.
//
p_disassembler_pointer
initialize_opcodes()
{
    p_disassembler_pointer pdisasm_ptr;

    //
    // We've got a valid architecture so now we proceed to initialize
    // our internal control structure and return it back to the user
    // for further disassembly operations.
    //
    pdisasm_ptr = (disassembler_pointer*) malloc (
        sizeof(disassembler_pointer));

    if (!pdisasm_ptr)
        return NULL;

    memset(pdisasm_ptr, 0, sizeof(disassembler_pointer));

    // Zero out structure members
    init_disassemble_info(&pdisasm_ptr->dinfo, &pdisasm_ptr->sfile, 
        (fprintf_ftype)__disassemle_printf);


    pdisasm_ptr->pfn_disassemble = NULL;

    //
    // Set the disassembly structure members information.
    //
    pdisasm_ptr->dinfo.application_data = (void*)pdisasm_ptr;

    //pdisasm_ptr->dinfo.arch = ull_arch;
    //pdisasm_ptr->dinfo.mach = ul_machine;
    //pdisasm_ptr->dinfo.endian = ul_endian;
    pdisasm_ptr->dinfo.flavour = bfd_target_unknown_flavour;

    //pdisasm_ptr->dinfo.fprintf_func  = (fprintf_ftype) __disassemle_printf;

    //pdisasm_ptr->dinfo.stream = &pdisasm_ptr->sfile;

    //pdisasm_ptr->sfile.alloc = 0;
    //pdisasm_ptr->sfile.pos = 0;
    //pdisasm_ptr->sfile.buffer = NULL;
    pdisasm_ptr->sfile.alloc = 100 * 1024;
    pdisasm_ptr->sfile.pos = 0;
    pdisasm_ptr->sfile.buffer = (char *) malloc (pdisasm_ptr->sfile.alloc);

    pdisasm_ptr->dinfo.flags = DISASSEMBLE_DATA;
    pdisasm_ptr->dinfo.flags |= USER_SPECIFIED_MACHINE_TYPE;

    return pdisasm_ptr;
}

//
// Name     : __disassemle_printf
//
// Purpose  : Format the disassembly output by making sprintf to a "stream".
//
// Params   : -
//
// Returns  : -
//
int ATTRIBUTE_PRINTF_2
__disassemle_printf (SFILE *f, const char *format, ...)
{
    size_t n;
    va_list args;
    char* temp_buffer;

    while (1)
    {
        size_t space = f->alloc - f->pos;

        va_start (args, format);
        n = vsnprintf (f->buffer + f->pos, space, format, args);
        va_end (args);

        // Determine if we need more space to hold the current disassembly.
        if (space > n)
            break;

        f->alloc = (f->alloc + n) * 2;

        temp_buffer = (char *) realloc (f->buffer, f->alloc);

        if (!temp_buffer) {
            // When realloc fails it returns NULL and the original buffer
            // remains untouched.
            free(f->buffer);
            f->alloc = f->pos = 0;
            return 0;
        }

        f->buffer = temp_buffer;
    }
    f->pos += n;

    return n;
}

//
// Name     : fix_bfd_pre_metadata
//
// Purpose  : Set straight the target address for the current architecture
//              being disassembled.
//
// Params   :   dinfo : BFD structure with disassembly information.
//              address : The target address.
//
// Returns  : -
//
void fix_bfd_pre_metadata(disassemble_info *dinfo, bfd_vma address)
{
    dinfo->insn_info_valid = 0;

    switch(dinfo->arch) {
    //case bfd_arch_i386:
    //    //bfd_vma target;     // Target address of branch or dref, if known;
    //                        // zero if unknown.
    //    //bfd_vma target2;    // Second target address for dref2
    //
    //    dinfo->target = address;
    //    dinfo->target2 = address;

    //    break;

    default:
        dinfo->target = 0;
        dinfo->target2 = 0;
        break;
    }
}

//
// Name     : fix_bfd_metadata
//
// Purpose  : -
//
// Params   :   dinfo : BFD structure with disassembly information.
//              opcode : Disassembled instruction.
//
// Returns  : -
//
void
fix_bfd_metadata(disassemble_info *dinfo, const char *opcode)
{
    //printf("-> %s\n", opcode);
    dinfo->insn_type = dis_nonbranch;

    switch(dinfo->arch)
    {
    case bfd_arch_arm: // ARM
        dinfo->insn_info_valid = 1;

        if ((!strncasecmp(opcode,"bx", 2)) || (strcasestr(opcode,"lr"))) {
            dinfo->insn_type = dis_branch;
        }
        else if (!strncasecmp(opcode,"bl", 2) || !strncasecmp(opcode,"blx", 3)) {
            dinfo->insn_type = dis_jsr;
        }
        else if (!strncasecmp(opcode,"b ", 2)) { // has a space !!!
            dinfo->insn_type = dis_branch;

            const char *p = strstr(opcode,"0x");

            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }
        else if (!strncasecmp(opcode,"b", 1)) { // BNE,BA,BE,etc.
            dinfo->insn_type = dis_condbranch;

            const char *p = strstr(opcode,"0x");

            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }
        break;

    case bfd_arch_powerpc: // PowerPC

        dinfo->insn_info_valid = 1;

        if (!strncasecmp(opcode,"blr", 3)) {
            dinfo->insn_type = dis_branch;
        }

        else if (!strncasecmp(opcode,"bl ", 3)) {
            dinfo->insn_type = dis_jsr;
            const char *p = strstr(opcode,"0x");

            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }
        else if (!strncasecmp(opcode,"b ", 2)) {
            dinfo->insn_type = dis_branch;
            const char *p = strstr(opcode,"0x");

            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }
        else if (!strncasecmp(opcode,"b", 1)) { //  // BNE,BA,BE,etc.
            dinfo->insn_type = dis_condbranch;
            const char *p = strstr(opcode,"0x");

            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }
        break;

    // TODO: Add target extraction and test cases.
    //case bfd_arch_sparc: // SPARC

    //    dinfo->insn_info_valid = 1;
    //    
    //    if (strcasestr(opcode,"b")) //  // BNE,BA,BE,etc.
    //       dinfo->insn_type = dis_condbranch;

    //    if (strcasestr(opcode,"call")) {
    //        dinfo->insn_type = dis_jsr;
    //        break;
    //    }
    //    if (strcasestr(opcode,"ret") || strcasestr(opcode,"restore")) {
    //        dinfo->insn_type = dis_branch;
    //        break;
    //    }
    //    break;

    case bfd_arch_ia64: // x86_64 info
    case bfd_arch_i386: // 386 info

        dinfo->insn_info_valid = 1;

        if (!strncasecmp(opcode,"ret", 3)){
            dinfo->insn_type = dis_branch;
            break;
        }

        else if (!strncasecmp(opcode,"jmp", 3)) {
            dinfo->insn_type = dis_branch;

            const char *p = strstr(opcode,"0x");
            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }

        else if (!strncasecmp(opcode,"call", 4)) {
            dinfo->insn_type = dis_jsr;

            const char *p = strstr(opcode,"0x");
            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }

        else if (!strncasecmp(opcode,"j", 1)) {
            // JA, JAE, JB, JBE, JC, JCXZ, JE, JG, JGE, JL, JLE, JNA, JNAE,
            // JNB, JNBE, JNC, JNE, JNG, JNGE, JNL, JNLE, JNO, JNP, JNS, JNZ,
            // JO, JP, JPE, JPO, JS, JZ.
            dinfo->insn_type = dis_condbranch;

            const char *p = strstr(opcode,"0x");
            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);
        }
        break;

    case bfd_arch_xtensa: // Tensilica Xtensa info

        dinfo->insn_info_valid = 1;

        if ((!strncasecmp(opcode,"ret", 3)) ||
            (!strncasecmp(opcode,"break", 4))) {
            dinfo->insn_type = dis_branch;
        }

        else if (opcode[0] == 'j') {
            dinfo->insn_type = dis_branch;

            const char *p = strstr(opcode,"0x");
            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);

        }

        else if (!strncasecmp(opcode,"call", 4)) {
            dinfo->insn_type = dis_jsr;

            const char *p = strstr(opcode,"0x");
            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);

        }

        else if (opcode[0] == 'b') {
            dinfo->insn_type = dis_condbranch;

            const char *p = strstr(opcode,"0x");
            if (p)
                sscanf(p,"0x%" BFD_VMA_FMT "x", &dinfo->target);

        }
        break;

    default:
        break;
    }

};

//
// Name     : start_smart_disassemble
//
// Purpose  : Iterate through all the user-specified bytes requested libopcodes
//              to disassemble them into a buffer for further usage.
//
// Params   :   pdisasm_ptr : Internal control structure.
//              bin_buffer : Binary chunk with data to disassemble.
//              buffer_length : Size of the above buffer.
//              vma : Start address of the disassembly.
//
// Returns  : Number of bytes disassembled.
//
int
start_smart_disassemble(disassembler_pointer* pdisasm_ptr, unsigned long offset,
    PyObject *callback)
{
    disassemble_info* dinfo = &(pdisasm_ptr->dinfo);
    unsigned int n = 0;
    unsigned long disassembled_bytes = 0;
    long callback_result;

    PyObject* py_args;
    PyObject* py_result;

    while (offset < dinfo->buffer_length)
    {
        // Fix target address references for further usage.
        fix_bfd_pre_metadata(dinfo, dinfo->buffer_vma + offset);

        // Call the appropriate disassembler function.
        n = pdisasm_ptr->pfn_disassemble(dinfo->buffer_vma + offset, dinfo);

        fix_bfd_metadata(dinfo, pdisasm_ptr->sfile.buffer);
        //
        // Add the current instruction to a list composed of:
        // - Address
        // - Length
        // - Number of delayed branch instructions
        // - Instruction type
        // - Target address number 1
        // - Target address number 2
        // - Disassembled instruction.
        //
        py_args = Py_BuildValue(
                "(" PY_VMA_FMT" ,I,b,I," PY_VMA_FMT "," PY_VMA_FMT ",s)",
                dinfo->buffer_vma + offset,
                n, //dinfo->buffer + offset,
                dinfo->branch_delay_insns,
                dinfo->insn_type,
                dinfo->target,
                dinfo->target2,
                pdisasm_ptr->sfile.buffer);

        pdisasm_ptr->sfile.pos = 0; // Set buffer pointer to the beginning
                                    // because now contains the entire
                                    // disassembled line just processed.
        offset += n; // update the offset for the next disassemble operation.
        disassembled_bytes += n;    // keep track of the number of bytes
                                    // processed.

        py_result = PyEval_CallObject(callback, py_args);
        Py_XDECREF(py_args);

        if (!py_result) {
            return -1;
        }

        callback_result = PyInt_AS_LONG(py_result);

        if (callback_result != PYBFD_DISASM_CONTINUE)
            break;
    }

    return disassembled_bytes;
}

//
// Name     : disassemble
//
// Purpose  : Iterate through all the user-specified bytes requested libopcodes
//              to disassemble them into a buffer for further usage.
//
// Params   :   pdisasm_ptr : Internal control structure.
//              bin_buffer : Binary chunk with data to disassemble.
//              buffer_length : Size of the above buffer.
//              vma : Start address of the disassembly.
//
// Returns  : A list object containing every disassembled instruction.
//
PyObject*
disassemble(disassembler_pointer* pdisasm_ptr)
{
    disassemble_info* dinfo = &(pdisasm_ptr->dinfo);

    unsigned int pos = 0,
                n = 0;

    PyObject* py_instruction_list = NULL; 

    // Create a python list to hold all the instructions representations.
    if (!(py_instruction_list = PyList_New(0)))
        return NULL;

    while (pos < dinfo->buffer_length)
    {
        // Call the appropriate disassembler function.
        n = pdisasm_ptr->pfn_disassemble(dinfo->buffer_vma + pos, dinfo);

        //
        // Add the current instruction to a list composed of:
        // - Instruction address.
        // - Instruction length.
        // - Instruction disassembly.
        //
        PyList_Append(py_instruction_list,
            Py_BuildValue(
                "(" PY_VMA_FMT" ,I,s)",
                dinfo->buffer_vma + pos,
                n,
                pdisasm_ptr->sfile.buffer)
            );

        pdisasm_ptr->sfile.pos = 0;
        pos += n;

    }

    return py_instruction_list;
}

// ---------------------- Begin of Python Layer -------------------

//
// Name     : pyopcodes_start_smart_disassemble
//
// Purpose  : Call the internal disassembler function to obtain a
//              human-readable string with the disassembled code and the
//              spcified offset.
//
// Params   :   
//
// Returns  : A list of tuples of address and size and disassembled
//              instructions.
//
static PyObject * pyopcodes_start_smart_disassemble(PyObject *self, PyObject *args)
{
    int disassembled_bytes;

    disassembler_pointer* pdisasm_ptr;
    bfd_vma vma;
    PyObject *callback;

    PyObject* pPyResult   = NULL;

    if (PyArg_ParseTuple(args, "n" PY_VMA_FMT "O:set_callback", 
        &pdisasm_ptr, &vma, &callback)) {
        // We only do this if a disassembler is not currently assigned. This
        // might happend becase the architure or the endian fields in the
        // disassembly_info structure have changed.
        //
        if (!pdisasm_ptr->pfn_disassemble) {
            //
            // Assign the disassembler function based on user-specified
            // parameters like architecture, specific machine and endianess.
            //
            pdisasm_ptr->pfn_disassemble = get_disassemble_function(
                pdisasm_ptr->dinfo.arch,
                pdisasm_ptr->dinfo.endian);

            if (!pdisasm_ptr->pfn_disassemble) {
                PyErr_SetString(
                    PyExc_TypeError, 
                    "Disassembler unavailable for current architecture.");
                return NULL;
            }
        }

        // If we've got a valid disassembly function from libopcodes then
        // proceed to disassemble the given buffer.
        Py_XINCREF(callback);

        disassembled_bytes = start_smart_disassemble(pdisasm_ptr, vma, callback);

        Py_XDECREF(callback);

        if (disassembled_bytes >= 0) {
            Py_RETURN_NONE;
        }
        else {
            PyErr_SetString(
                PyExc_TypeError, 
                "Unable to disassemble current architecture.");
        }
    }

    return pPyResult;
}

//
// Name     : pyopcodes_initialize_smart_disassemble
//
// Purpose  : Call the internal disassembler function to obtain a
//              human-readable string with the disassembled code and the
//              spcified offset.
//
// Params   :   
//
// Returns  : A list of tuples of address and size and disassembled
//              instructions.
//
static PyObject * pyopcodes_initialize_smart_disassemble(PyObject *self, PyObject *args)
{
    disassembler_pointer* pdisasm_ptr;
    unsigned int buffer_length;
    bfd_vma vma;
    
    unsigned char* bin_buffer  = NULL;    
    unsigned char* disasm_buffer;

    PyObject* pPyResult   = NULL;

    if (PyArg_ParseTuple(args, "ns#" PY_VMA_FMT,
        &pdisasm_ptr, &bin_buffer, &buffer_length, &vma)) {

        // free previous buffer
        if(pdisasm_ptr->dinfo.buffer != 0)
        {
            free(pdisasm_ptr->dinfo.buffer);
            pdisasm_ptr->dinfo.buffer_length = 0;
        }        
        disasm_buffer = (unsigned char*)malloc(buffer_length);
        memcpy(disasm_buffer, bin_buffer, buffer_length);
        //
        // What to disassemble.
        //
        pdisasm_ptr->dinfo.buffer = disasm_buffer;
        pdisasm_ptr->dinfo.buffer_length = buffer_length;
        pdisasm_ptr->dinfo.buffer_vma = vma;

        disassemble_init_for_target(&pdisasm_ptr->dinfo);

        Py_RETURN_NONE;
    }

    return pPyResult;
}

//
// Name     : pyopcodes_disassemble
//
// Purpose  : Call the internal disassembler function to obtain a
//              human-readable string with the disassembled code and the
//              spcified offset.
//
// Params   :   
//
// Returns  : A list of tuples of address and size and disassembled
//              instructions.
//
static PyObject * pyopcodes_disassemble(PyObject *self, PyObject *args)
{
    disassembler_pointer* pdisasm_ptr;
    unsigned int buffer_length = 0;
    bfd_vma /*unsigned int*/ vma = 0;
    unsigned char* bin_buffer  = NULL;

    PyObject* pPyResult   = NULL;

    if (PyArg_ParseTuple(args, "ns#" PY_VMA_FMT,
        &pdisasm_ptr, &bin_buffer, &buffer_length, &vma)) {
        // We only do this if a disassembler is not currently assigned. This
        // might happend becase the architure or the endian fields in the
        // disassembly_info structure have changed.
        //
        if (!pdisasm_ptr->pfn_disassemble) {
            //
            // Assign the disassembler function based on user-specified
            // parameters like architecture, specific machine and endianess.
            //
            pdisasm_ptr->pfn_disassemble = get_disassemble_function(
                pdisasm_ptr->dinfo.arch,
                pdisasm_ptr->dinfo.endian);

            if (!pdisasm_ptr->pfn_disassemble) {
                PyErr_SetString(
                    PyExc_TypeError, 
                    "Disassembler unavailable for current architecture.");
                return NULL;
            }
        }

        disassemble_init_for_target(&pdisasm_ptr->dinfo);

        //
        // What to disassemble.
        //
        pdisasm_ptr->dinfo.buffer = bin_buffer;
        pdisasm_ptr->dinfo.buffer_length = buffer_length;
        pdisasm_ptr->dinfo.buffer_vma = vma;

        // If we've got a valid disassembly function from libopcodes then
        // proceed to disassemble the given buffer.
        pPyResult = disassemble(pdisasm_ptr);
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return pPyResult;
}

//
// Name     : pyopcodes_set_architecture
//
// Purpose  : Set the machine to a user-specified value and create the initial
//              disassembler structure for further disassemly operantions
//              usage.
//
// Params   :   @arch : The constant value representing the architecture.
//
// Returns  : A valid disassembler_pointer structure.
//
static PyObject * pyopcodes_set_architecture(PyObject *self, PyObject *args)
{
    unsigned long long arch;
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the architecture, machine type for
    // that architecture and the endianess of the code about to be
    // disassembled.
    //
    if (PyArg_ParseTuple(args, "L", &arch)) {
        pdisasm_ptr = initialize_opcodes();

        if (pdisasm_ptr) {

            pdisasm_ptr->dinfo.arch = arch;

            // Mark as uninitialized because the architecture changed and might
            // change again until the disassembly operation takes place.
            pdisasm_ptr->pfn_disassemble = NULL;

            //powerpc_init_dialect(pdisasm_ptr->dinfo);
            return Py_BuildValue("n", pdisasm_ptr);
        }
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_get_architecture
//
// Purpose  :  Return the current architecture value.
//
// Params   :   @pdisasm_ptr : The constant value representing the architecture.
//
// Returns  : The current architecture value stored.
//
static PyObject * pyopcodes_get_architecture(PyObject *self, PyObject *args)
{
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the architecture, machine type for
    // that architecture and the endianess of the code about to be
    // disassembled.
    //
    if (PyArg_ParseTuple(args, "n", &pdisasm_ptr)) {

        if (pdisasm_ptr)
            return Py_BuildValue("L", pdisasm_ptr->dinfo.arch);
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_get_machine
//
// Purpose  : Return the current machine value.
//
// Params   :   @mach : The constant value representing the machine type.
//
// Returns  : -
//
static PyObject * pyopcodes_get_machine(PyObject *self, PyObject *args)
{
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the current disassembler_pointer
    // structure and the machine.
    //
    if (PyArg_ParseTuple(args, "n", &pdisasm_ptr)) {

        if (pdisasm_ptr)
            return Py_BuildValue("k", pdisasm_ptr->dinfo.mach);
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_set_machine
//
// Purpose  : Set the machine to a user-specified value.
//
// Params   :   @pdisasm_ptr: Current disassembler structure.
//              @machine : The new machine value used for diassembly.
//
// Returns  : The constant value representing the machine type.
//
static PyObject * pyopcodes_set_machine(PyObject *self, PyObject *args)
{
    unsigned long machine; // This is ok.
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the current disassembler_pointer
    // structure.
    //
    if (PyArg_ParseTuple(args, "nk", &pdisasm_ptr, &machine)) {

        pdisasm_ptr->dinfo.mach = machine;

        Py_RETURN_NONE;
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_get_endian
//
// Purpose  : Return the current endian value.
//
// Params   :   @pdisasm_ptr : The constant value representing the architecture.
//
// Returns  : The constant value representing the machine type.
//
static PyObject * pyopcodes_get_endian(PyObject *self, PyObject *args)
{
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the current disassembler_pointer
    // structure..
    //
    if (PyArg_ParseTuple(args, "n", &pdisasm_ptr)) {

        if (pdisasm_ptr)
            return Py_BuildValue("k", pdisasm_ptr->dinfo.endian);
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_set_endian
//
// Purpose  : Set the endian to a user-specified value.
//
// Params   :   @pdisasm_ptr: Current disassembler structure.
//              @endian : The new endian value used for diassembly.
//
// Returns  : -
//
static PyObject * pyopcodes_set_endian(PyObject *self, PyObject *args)
{
    unsigned long endian;
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the current disassembler_pointer
    // structure and the endian.
    //
    if (PyArg_ParseTuple(args, "nk", &pdisasm_ptr, &endian)) {

        pdisasm_ptr->dinfo.endian_code = endian;
        pdisasm_ptr->dinfo.endian = endian;

        // Mark as uninitialized because the endian changed and might
        // change again until the disassembly operation takes place.
        pdisasm_ptr->pfn_disassemble = NULL;

        Py_RETURN_NONE;
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_deinitialize
//
// Purpose  : Release current disassembler internal structure and resources.
//
// Params   : @pdisasm_ptr: Current disassembler structure.
//
// Returns  : -
//
static PyObject * pyopcodes_deinitialize(PyObject *self, PyObject *args)
{
    p_disassembler_pointer pdisasm_ptr;

    if (PyArg_ParseTuple(args, "n", &pdisasm_ptr)) {
        // Release all the resources and set them null.
        if (pdisasm_ptr) {
            if (pdisasm_ptr->sfile.buffer) {
                free (pdisasm_ptr->sfile.buffer);
            }
            if (pdisasm_ptr->dinfo.buffer) {
                free (pdisasm_ptr->dinfo.buffer);
            }
            free (pdisasm_ptr);
            pdisasm_ptr = 0;
        }

        Py_RETURN_NONE;
    }
    PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");

    return NULL;
}

//
// Name     : pyopcodes_initialize_bfd
//
// Purpose  : 
//
// Params   :   @bfd : BFD to use during initialization.
//
// Returns  : A valid disassembler_pointer structure.
//
static PyObject * pyopcodes_initialize_bfd(PyObject *self, PyObject *args)
{
    bfd* abfd;
    p_disassembler_pointer pdisasm_ptr;

    //
    // Retrieve python arguments indicating the architecture, machine type for
    // that architecture and the endianess of the code about to be
    // disassembled.
    //
    if (PyArg_ParseTuple(args, "n", &abfd)) {
        pdisasm_ptr = initialize_opcodes();

        if (pdisasm_ptr) {
            pdisasm_ptr->dinfo.arch = bfd_get_arch(abfd);
            pdisasm_ptr->dinfo.mach = bfd_get_mach(abfd);
            pdisasm_ptr->dinfo.endian_code = pdisasm_ptr->dinfo.endian = \
                bfd_big_endian(abfd) ? BFD_ENDIAN_BIG : BFD_ENDIAN_LITTLE;

            // Assign the disassembler function selected by BFD itself.
            pdisasm_ptr->pfn_disassemble = disassembler(abfd);

            if (pdisasm_ptr->pfn_disassemble) {
                return Py_BuildValue("n", pdisasm_ptr);
            }
            else {
                PyErr_SetString(
                    PyExc_TypeError,
                    "Disassembler unavailable for current architecture.");
                return NULL;
                // TODO
                //deinitialize_opcodes(pdisasm_ptr);
            }
        }
    }
    else {
        PyErr_SetString(PyExc_TypeError, "Invalid parameter(s)");
    }

    return NULL;
}

//
// Define methods
//
static struct PyMethodDef _opcodes_methods[] = 
{
#define declmethod(func,h) { #func , ( PyCFunction )pyopcodes_##func , \
    METH_VARARGS , h }
    declmethod(set_architecture, "Module initialization (not using BFD)."),
    declmethod(set_machine, "Set the mach in the disassembly_info structure."),
    declmethod(set_endian, "Set the endian in the disassembly_info structure."),
    declmethod(get_architecture, "Return the current architecture value."),
    declmethod(get_machine, "Return the machine value in the disassembly_info structure."),
    declmethod(get_endian, "Return the endian value in the disassembly_info structure."),
    declmethod(initialize_bfd, "Module initialization (using BFD)."),
    declmethod(disassemble, "Disassemble given code."),
    declmethod(initialize_smart_disassemble, "Initialize a smart disassemble session."),
    declmethod(start_smart_disassemble, "Disassemble given code until function end."),
    declmethod(deinitialize, "Delete current structure and release resources."),
    {NULL}
#undef declmethod
};

//
// Name     : init_opcodes
//
// Purpose  : Initialize Python extension module and libopcodes specifics.
//
// Params   : -
//
// Returns  : -
//
PyMODINIT_FUNC init_opcodes(void)
{
    if (!Py_InitModule("_opcodes", _opcodes_methods))
        return;

    // Add additional initialization here.
}
