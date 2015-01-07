#!/usr/bin/env python
# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part PyBFD module (libbfd & libopcodes extension module)
#

from sys import argv, exit
from types import FileType, StringType, IntType
from os import dup
from os.path import islink
from traceback import print_exc, print_stack

from sys import version_info
if version_info >= (2,6,0):
    def import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_bfd', [dirname(__file__)])
        except ImportError:
            import _bfd
            return _bfd
        if fp is not None:
            try:
                _mod = imp.load_module('_bfd', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _bfd = import_helper()
    del import_helper
else:
    import _bfd
del version_info

from bfd_archs import *
from section import *
from symbol import *
from bfd_base import *

__author__ = "Groundworks Technologies OSS Team"
__contact__ = "oss@groundworkstech.com"
__company__ = "Groundworks Technologies"
__year__ = "2013"
__version__ = "0.1"
__title__ = "Binutils libbfd Python module"

BfdAttributes = enum(
    "FILENAME",
    "CACHEABLE",
    "FORMAT",
    "TARGET",
    "FLAVOUR",
    "FAMILY_COFF",
    "IS_BIG_ENDIAN",
    "IS_LITTLE_ENDIAN",
    "HEADER_BIG_ENDIAN",
    "HEADER_LITTLE_ENDIAN",
    "FILE_FLAGS",
    "APPLICABLE_FILE_FLAGS",
    "APPLICABLE_SECTION_FLAGS",
    "MY_ARCHIEVE",
    "HAS_MAP",
    "IS_THIN_ARCHIEVE",
    "HAS_GAP_IN_ELF_SHNDX",
    "VALID_RELOC_TYPES",
    "USRDATA",
    "START_ADDRESS",
    "SYMCOUNT",
    "OUTSYMBOLS",
    "COUNT_SECTIONS",
    "DYNAMIC_SYMCOUNT",
    "SYMBOL_LEADING_CHAR"
    )


class Bfd(object):
    """
    Main BFD wrapper class. This class allows the user to handle a BFD object
    (open a file to get its symbols, read resction content, etc..
    
    """

    DEFAULT_TARGET = "default"

    def __init__(self, _file=None, target=DEFAULT_TARGET):
        """Initialize underlying libbfd library."""
        # Hold the native bfd object.
        self._ptr = None

        # Hold a dict of every section present in the bfd.
        self._sections = {}

        # Hold a dict of every symbol present in the bfd.
        self._symbols = {}

        # Initially set the file format to unknown until a file is opened.
        self._format = BfdFormat.UNKNOWN

        if _file:
            self.open(_file, target)

    #def __del__(self):
    #    """Deinitialize BFD and release instance."""
    #    self.close()

    @property
    def _ptr(self):
        """Return the native BFD structure pointer."""
        return self.__ptr

    @_ptr.setter
    def _ptr(self, ptr):
        """Store the native BFD structure pointer."""
        self.__ptr = ptr

    def open(self, _file, target=DEFAULT_TARGET):
        """
        Open the existing file for reading.

        @param _file : A filename of file descriptor.
        @param target: A user-specific BFD target name.

        @return : None
        """
        # Close any existing BFD structure instance. 
        self.close()

        #
        # STEP 1. Open the BFD pointer.
        #
        # Determine if the user passed a file-descriptor or a _file and
        # proceed accordingly.
        if type(_file) is FileType:
            # The user specified a file descriptor.
            filename = _file.name

            if islink(filename):
                raise BfdException("Symlinks file-descriptors are not valid")
                    
            try:
                self._ptr = _bfd.fdopenr(filename, target, dup(_file.fileno()))
            except Exception, err:
                raise BfdException(
                    "Unable to open file-descriptor %s : %s" % (filename, err))

        elif type(_file) is StringType:
            # The user spcified a filaname so first check if file exists.
            filename = _file
            try:
                with open(_file): pass
            except IOError:
                raise BfdException("File %s does not exist." % filename)

            #
            # Proceed to open the specified file and create a new BFD.
            #
            try:
                self._ptr = _bfd.openr(filename, target)
            except (TypeError, IOError), err:
                raise BfdException(
                    "Unable to open file %s : %s" % (filename, err))

        elif type(_file) is IntType:
            # The user specified an already-open BFD pointer so we avoid any
            # further open operation and move on to file format recognition.
            self._ptr = _file

        else:
            raise BfdException(
                "Invalid file type specified for open operation (%r)" % _file)

        #
        # STEP 2. Determine file format of the BFD.
        #
        # Now that the BFD is open we'll proceed to determine its file format.
        # We'll use the objdump logic to determine it and raise an error in
        # case we were unable to get it right.
        #
        try:
            # Type opening it as an archieve and if it success then check
            # subfiles.
            if _bfd.check_format(self._ptr, BfdFormat.ARCHIVE):
                # Set current format and store the inner file list.
                self.file_format = BfdFormat.ARCHIVE

                self.__populate_archive_files()
            else:
                # DO NOT USE bfd_check_format_matches() becuase its not tested.
                # An implementation example if on objdump.c at function
                # display_bfd().
                if _bfd.check_format(self._ptr, BfdFormat.OBJECT):
                    self.file_format = BfdFormat.OBJECT

                elif _bfd.check_format(self._ptr, BfdFormat.CORE):
                    self.file_format = BfdFormat.CORE

                else:
                    pass
                    raise BfdException(_bfd.get_last_error_message())

        except TypeError, err:
            raise BfdException(
                "Unable to initialize file format : %s" % err)

        #
        # STEP 3. Extract inner sections and symbolic information.
        #
        if self._ptr is not None:
            # If the file is a valid BFD file format but not an archive then
            # get its sections and symbolic information (if any).
            if self.file_format in [BfdFormat.OBJECT, BfdFormat.CORE]:
                self.__populate_sections()
                self.__populate_symbols()

    def __populate_archive_files(self):
        """Store the list of files inside an archive file."""
        self.archive_files = []
        for _ptr in _bfd.archive_list_files(self._ptr):
            try:
                self.archive_files.append(Bfd(_ptr))
            except BfdException, err:
                #print "Error populating archive file list : %s" % err
                #print_exc()
                pass

    @property
    def archive_files(self):
        """Return the list of BFDs inside an archive file."""
        return self._archive_files

    @archive_files.setter
    def archive_files(self, files):
        """Store the list of BFDs inside an archive file."""
        self._archive_files = files

    @property
    def archive_filenames(self):
        """Return the list of files inside an archive file."""
        try:
            return _bfd.archive_list_filenames(self._ptr)
        except TypeError, err:
            raise BfdException(err)

    @property
    def file_format(self):
        """Return the current format of the open bdf."""
        return self._format

    @file_format.setter
    def file_format(self, _format):
        """Store the current format of the open bdf."""
        self._format = _format

    @property
    def is_archive(self):
        """Indicate if currently open bfd is an archive or not."""
        return self.file_format == BfdFormat.ARCHIVE

    @property
    def is_object(self):
        """Indicate if currently open bfd is a compiled binary file or not."""
        return self.file_format == BfdFormat.OBJECT

    @property
    def is_core_dump(self):
        """Indicate if currently open bfd is a core dump or not."""
        return self.file_format == BfdFormat.CORE

    @property
    def file_format_name(self):
        """Return the current format name of the open bdf."""
        try:
            return BfdFormatNamesLong[self.file_format]
        except IndexError, err:
            raise BfdException("Invalid format specified (%d)" % self.file_format)

    @property
    def _error_code(self):
        """Return the internal BFD error code.
        Only for internal use.

        """
        return _bfd.get_error()

    @_error_code.setter
    def _error_code(self, error):
        """Set the internal BFD error code to a user specified values.
        Only for internal use.

        """
        _bfd.set_error(error)

    def __populate_sections(self):
        """Get a list of the section present in the bfd to populate our
        internal list.

        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        for section in _bfd.get_sections_list(self._ptr):
            try:
                bfd_section = BfdSection(self._ptr, section)
                self._sections[bfd_section.name] = bfd_section
            except BfdSectionException, err:
                #print "Exception during section pasing : %s" % err
                pass

    def __populate_symbols(self):
        """Get a list of the symbols present in the bfd to populate our
        internal list.

        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        try:
            symbols = _bfd.get_symbols(self._ptr)

            # Temporary dictionary ordered by section index. This is necessary
            # because the symbolic information return the section index it belongs
            # to.
            sections = {}
            for section in self.sections:
                sections[self.sections[section].index] = self.sections[section]

            for symbol in symbols:
                # Extract each field for further processing.
                symbol_section_index = symbol[0]
                symbol_name = symbol[1]
                symbol_value = symbol[2]
                symbol_flags = symbol[3]

                # Get the effective address of the current symbol.
                symbol_flags = tuple(
                    [f for f in SYMBOL_FLAGS_LIST if symbol_flags & f == f] )

                # Create a new symbol instance to hold symbolic information.
                new_symbol = Symbol(
                    sections.get(symbol_section_index, None),
                    symbol_name,
                    symbol_value,
                    symbol_flags)

                if new_symbol.section is None:
                    continue
                symbol_address = new_symbol.section.vma + new_symbol.value
                #if new_symbol.flags in \
                #    [SymbolFlags.LOCAL , SymbolFlags.GLOBAL , SymbolFlags.EXPORT]:
                #    symbol_address = new_symbol.section.vma + new_symbol.value
                #else:
                #    # TODO: Enhance this!
                #    # Discard any other symbol information.
                #    continue

                self._symbols[symbol_address] = new_symbol

            del sections
        except BfdSectionException, err:
            raise BfdException("Exception on symbolic ifnormation parsing.")

    def close(self):
        """Close any existing BFD structure before open a new one."""
        if self._ptr:
            #try:
            #    # Release inner BFD files in case we're an archive BFD.
            #    if self.is_archive:
            #        [inner_bfd.close() for inner_bfd in self.archive_files]
            #except TypeError, err:
            #    pass

            try:
                _bfd.close(self._ptr)
            except TypeError, err:
                raise BfdException("Unable to close bfd (%s)" % err)
            finally:
                self._ptr = None

    @property
    def sections(self):
        return self._sections

    @property
    def symbols(self):
        return self._symbols

    @property
    def filename(self):
        """Return the filename of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.FILENAME)

    @property
    def cacheable(self):
        """Return the cacheable attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.CACHEABLE)

    @property
    def format(self):
        """Return the format attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.FORMAT)

    @property
    def target(self):
        """Return the target of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.TARGET)

    @property
    def architecture(self):
        """Return the architecture of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_architecture(self._ptr)

    @property
    def architecture_name(self):
        """Return the current architecture name accoding to its index."""
        return get_architecture_name(self.architecture)

    @property
    def machine(self):
        """Return the flavour attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.FLAVOUR)

    @machine.setter
    def machine(self, value):
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.set_bfd_attribute(self._ptr, BfdAttributes.FLAVOUR, value)

    @property
    def family_coff(self):
        """Return the family_coff attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.FAMILY_COFF)

    @property
    def endian(self):
        if self.big_endian:
            return ENDIAN_BIG
        elif self.little_endian:
            return ENDIAN_LITTLE        
        return ENDIAN_UNKNOWN

    @property
    def big_endian(self):
        """Return the big endian attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.IS_BIG_ENDIAN)

    @property
    def little_endian(self):
        """
        Return the little_endian attribute of the BFD file being processed.
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.IS_LITTLE_ENDIAN)

    @property
    def header_big_endian(self):
        """
        Return the header_big_endian attribute of the BFD file being processed.

        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.HEADER_BIG_ENDIAN)

    @property
    def header_little_endian(self):
        """Return the header_little_endian attribute of the BFD file being
        processed.
        
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.HEADER_LITTLE_ENDIAN)

    @property
    def file_flags(self):
        """Return the file flags attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.FILE_FLAGS)

    @file_flags.setter
    def file_flags(self, _file_flags):
        """Set the new file flags attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.set_file_flags(self._ptr, _file_flags)

    @property
    def applicable_file_flags(self):
        """
        Return the applicable file flags attribute of the BFD file being
        processed.

        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.APPLICABLE_FILE_FLAGS)

    @property
    def my_archieve(self):
        """Return the my archieve attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.MY_ARCHIEVE)

    @property
    def has_map(self):
        """Return the has map attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.HAS_MAP)

    @property
    def is_thin_archieve(self):
        """
        Return the is thin archieve attribute of the BFD file being processed.
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.IS_THIN_ARCHIEVE)

    @property
    def has_gap_in_elf_shndx(self):
        """Return the has gap in elf shndx attribute of the BFD file being
        processed.
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.HAS_GAP_IN_ELF_SHNDX)

    @property
    def valid_reloction_types(self):
        """Return the valid_reloc_types attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.VALID_RELOC_TYPES)

    @property
    def user_data(self):
        """Return the usrdata attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.USRDATA)

    @property
    def start_address(self):
        """Return the start address attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.START_ADDRESS)

    @start_address.setter
    def start_address(self, _start_address):
        """Store the new start address attribute of the BFD file being
        processed.
        
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.set_start_address(self._ptr, _start_address)

    @property
    def gp_size(self):
        """Return the start address attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr)

    @gp_size.setter
    def gp_size(self, _gp_size):
        """Store the new start address attribute of the BFD file being
        processed.
        
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.set_gp_size(self._ptr, _gp_size)

    @property
    def symbols_count(self):
        """Return the symcount attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.SYMCOUNT)

    @property
    def out_symbols(self):
        """Return the out symbols attribute of the BFD file being processed."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.OUTSYMBOLS)

    @property
    def sections_count(self):
        """Return the sections_count attribute of the BFD file being processed."""
        # This should match the 'sections' attribute length so instead should
        # use :
        #
        #   len(bfd.sections)
        #
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(self._ptr, BfdAttributes.COUNT_SECTIONS)

    @property
    def dynamic_symbols_count(self):
        """Return the dynamic symbols count attribute of the BFD file being
        processed.
        
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.DYNAMIC_SYMCOUNT)

    @property
    def symbol_leading_char(self):
        """Return the symbol leading char attribute of the BFD file being
        processed.
        
        """
        if not self._ptr:
            raise BfdException("BFD not initialized")

        return _bfd.get_bfd_attribute(
            self._ptr, BfdAttributes.SYMBOL_LEADING_CHAR)

    @property
    def architectures(self):
        """Return a list of the supported architectures."""
        return _bfd.arch_list()

    @property
    def targets(self):
        """
        Return a list of the supported targets (format + architecture
        combinations).

        """
        return _bfd.target_list()

    @property
    def arch_size(self):
        """Return the architecure size in bits."""
        if not self._ptr:
            raise BfdException("BFD not initialized")

        try:
            return _bfd.get_arch_size(self._ptr)
        except Exception, err:
            raise BfdException("Unable to determine architeure size.")

    def flag_name_shost(self, flag):
        """Return the flag name according to its value."""
        if flag in BFD_FLAGS_NAMES_SHORT:
            return BFD_FLAGS_NAMES_SHORT[flag]

        return None

    @property
    def printable_arch(self):
        """Return printable representation of current BFD architecture."""
        return ""

    @property
    def printable_mach(self):
        """Return printable representation of current BFD machine."""
        return ""

    def __str__(self):
        """Return string representation of the current BFD."""
        _str = "I'm a bfd."
        return _str

def main():

    print "%s %s - %s (C) %s\n" % (__title__, __version__, __company__, __year__)

    # Import the disassembly library (libopcodes)
    from opcodes import Opcodes, OpcodesException

    if len(argv) == 1:
        print "Usage : %s <filename>" % argv[0]
        return

    bfd = None

    try:
        #
        # Initialize BFD instance.
        # We can either pass a filename or a file descriptor and they will be used
        # in the same way.
        #
        print "[+] Creating BFD instance..."
        #fd = open(argv[1], "r")
        bfd = Bfd(argv[1])

        # Print the file format and in case that its an archive then just show
        # its files and leave.
        print "[+] File format     : %s" % bfd.file_format_name

        if bfd.is_archive:
            print "[-] List of internal files:"
            #for inner_filename in bfd.archive_filenames:
            #    print "\t%s" % inner_filename

            for inner_bfd in bfd.archive_files:
                print "\t%-40s - sections : %d - symbols : %s" % \
                    (inner_bfd.filename,
                    len(inner_bfd.sections),
                    len(inner_bfd.symbols))

            # The bfd.close() is executed bellow in the finally clause.
            return

        #
        # Display some information about the currently open file.
        #
        print "[+] Architecture    : %s (%d)" % \
            (bfd.architecture_name, bfd.architecture)
        print "[+] BFD target name : %s" % bfd.target
        print "[+] Entry point     : 0x%X" % bfd.start_address
        print "[+] Sections        : %d" % len(bfd.sections)
        #print "\n".join([str(s) for s in bfd.sections])

        #
        # Get the .text section for further usage.
        #
        section_name = ".text"
        section = bfd.sections.get(section_name)
        if not section:
            print "[-] No section \'%s\' available." % section_name
            return

        #
        # Display its name (we get it from the section instance) and its index
        # inside the binary file.
        #
        print "[+] Selected section information:"
        print "\tName   : %s" % section.name
        print "\tIndex  : %d" % section.index

        # Dump the section content to a buffer
        content = section.content

        # Display approximate section length.
        length = len(content) / 1024

        if length == 0:
            length = len(content) % 1024
            length_unit = "Bytes"
        else:
            length_unit = "Kbytes"

        print "\tLength : %(length)d %(length_unit)s" % vars()

        #
        # At this point we'll disassemble the entire section content. We'll obtain
        # instruction address, size, type and disassembly (in text format).
        #
        try:
            # Create opcodes instance to start code section disassembly.
            opcodes = Opcodes(bfd)

            # Set the code area we'll move through.
            opcodes.initialize_smart_disassemble(content, section.vma)

            # Set an internal -ready to use- callback function to print disassembly
            # information from the current section content.
            opcodes.start_smart_disassemble(0, opcodes.print_single_instruction_callback)

        except OpcodesException, err:
            print "[-] Opcodes exception : %s" % err

        #for vma, size, disasm in opcodes.disassemble(content, bfd.start_address):
        #    print "0x%X (%d)\t %s" % (vma, size, disasm)
        #    print disasm, opcodes.build_instruction(vma, size, disasm)
        #    pass

    except BfdException, err:
        #print_exc()
        print "Error : %s" % err

    finally:
        if bfd:
            # Check is we're working with an archive and close archived files
            # before closing the container.
            try:
                # Release inner BFD files in case we're an archive BFD.
                if bfd.is_archive:
                    [inner_bfd.close() for inner_bfd in bfd.archive_files]
            except TypeError, err:
                pass

            # Release the current BFD and leave. 
            bfd.close()

if __name__ == "__main__":
    try:
        main()
    except Exception, err:
        #print_exc()
        print "Exception : %s" % err
