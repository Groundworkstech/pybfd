# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part Python pybfd module (libbfd extension module)
#

from bfd_base import BfdException, enum
import _bfd

__author__      = "Groundworks Technologies OSS Team"
__contact__     = "oss@groundworkstech.com"
__company__     = "Groundworks Technologies"
__year__        = "2013"
__versaion__    = "0.1"

class SectionFlags:
    NO_FLAGS = 0x000

    #
    # Tells the OS to allocate space for this section when loading.
    # This is clear for a section containing debug information only.
    #
    ALLOC = 0x001

    #
    # Tells the OS to load the section from the file when loading.
    # This is clear for a .bss section.
    #
    LOAD = 0x002

    #
    # The section contains data still to be relocated, so there is
    # some relocation information too.
    #
    RELOC = 0x004

    #
    # A signal to the OS that the section contains read only data.
    #
    READONLY = 0x008

    #
    # The section contains code only.
    #
    CODE = 0x010

    #
    # The section contains data only.
    #
    DATA = 0x020

    #
    # The section will reside in ROM.
    #
    ROM = 0x040

    #
    # The section contains constructor information. This section
    # type is used by the linker to create lists of constructors and
    # destructors used by <<g++>>. When a back end sees a symbol
    # which should be used in a constructor list, it creates a new
    # section for the type of name (e.g., <<__CTOR_LIST__>>), attaches
    # the symbol to it, and builds a relocation. To build the lists
    # of constructors, all the linker has to do is catenate all the
    # sections called <<__CTOR_LIST__>> and relocate the data
    # contained within - exactly the operations it would peform on
    # standard data.
    #
    CONSTRUCTOR = 0x080

    #
    # a data section could be
    #CONTENTS>>; a debug section could be
    #
    HAS_CONTENTS = 0x100

    #
    # An instruction to the linker to not output the section
    # even if it has information which would normally be written.
    #
    NEVER_LOAD = 0x200

    #
    # The section contains thread local data.
    #
    THREAD_LOCAL = 0x400

    #
    # The section has GOT references.  This flag is only for the
    # linker, and is currently only used by the elf32-hppa back end.
    # It will be set if global offset table references were detected
    # in this section, which indicate to the linker that the section
    # contains PIC code, and must be handled specially when doing a
    # static link.
    #
    HAS_GOT_REF = 0x800

    #
    # The section contains common symbols (symbols may be defined
    # multiple times, the value of a symbol is the amount of
    # space it requires, and the largest symbol value is the one
    # used).  Most targets have exactly one of these (which we
    # translate to bfd_com_section_ptr), but ECOFF has two.
    #
    IS_COMMON = 0x1000

    #
    # The section contains only debugging information.  For
    # example, this is set for ELF .debug and .stab sections.
    # strip tests this flag to see if a section can be
    # discarded.
    #
    DEBUGGING = 0x2000

    #
    # The contents of this section are held in memory pointed to
    # by the contents field.  This is checked by bfd_get_section_contents,
    # and the data is retrieved from memory if appropriate.
    #
    IN_MEMORY = 0x4000

    #
    # The contents of this section are to be excluded by the
    # linker for executable and shared objects unless those
    # objects are to be further relocated.
    #
    EXCLUDE = 0x8000

    #
    # The contents of this section are to be sorted based on the sum of
    # the symbol and addend values specified by the associated relocation
    # entries.  Entries without associated relocation entries will be
    # appended to the end of the section in an unspecified order.
    #
    SORT_ENTRIES = 0x10000

    #
    # When linking, duplicate sections of the same name should be
    # discarded, rather than being combined into a single section as
    # is usually done.  This is similar to how common symbols are
    # handled.  See LINK_DUPLICATES below.
    #
    LINK_ONCE = 0x20000

    #
    # If LINK_ONCE is set, this bitfield describes how the linker
    # should handle duplicate sections.
    #
    LINK_DUPLICATES = 0xc0000

    #
    # This value for LINK_DUPLICATES means that duplicate
    # sections with the same name should simply be discarded.
    #
    LINK_DUPLICATES_DISCARD = 0x0

    #
    # This value for LINK_DUPLICATES means that the linker
    # should warn if there are any duplicate sections, although
    # it should still only link one copy.
    #
    LINK_DUPLICATES_ONE_ONLY = 0x40000

    #
    # This value for LINK_DUPLICATES means that the linker
    # should warn if any duplicate sections are a different size.
    #
    LINK_DUPLICATES_SAME_SIZE = 0x80000

    #
    # This value for LINK_DUPLICATES means that the linker
    # should warn if any duplicate sections contain different
    # contents.
    #
    LINK_DUPLICATES_SAME_CONTENTS  = \
      (LINK_DUPLICATES_ONE_ONLY | LINK_DUPLICATES_SAME_SIZE)

    #
    # This section was created by the linker as part of dynamic
    # relocation or other arcane processing.  It is skipped when
    # going through the first-pass output, trusting that someone
    # else up the line will take care of it later.
    #
    LINKER_CREATED = 0x100000

    #
    # This section should not be subject to garbage collection.
    # Also set to inform the linker that this section should not be
    # listed in the link map as discarded.
    #
    KEEP = 0x200000

    #
    # This section contains "short" data, and should be placed
    # "near" the GP.
    #
    SMALL_DATA = 0x400000

    #
    # Attempt to merge identical entities in the section.
    # Entity size is given in the entsize field.
    #
    MERGE = 0x800000

    #
    # If given with MERGE, entities to merge are zero terminated
    # strings where entsize specifies character size instead of fixed
    # size entries.
    #
    STRINGS = 0x1000000

    #
    # This section contains data about section groups.
    #
    GROUP = 0x2000000

    #
    # The section is a COFF shared library section.  This flag is
    # only for the linker.  If this type of section appears in
    # the input file, the linker must copy it to the output file
    # without changing the vma or size.  FIXME: Although this
    # was originally intended to be general, it really is COFF
    # specific (and the flag was renamed to indicate this).  It
    # might be cleaner to have some more general mechanism to
    # allow the back end to control what the linker does with
    # sections.
    #
    COFF_SHARED_LIBRARY = 0x4000000

    #
    # This input section should be copied to output in reverse order
    # as an array of pointers.  This is for ELF linker internal use
    # only.
    #
    ELF_REVERSE_COPY = 0x4000000

    #
    # This section contains data which may be shared with other
    # executables or shared objects. This is for COFF only.
    #
    COFF_SHARED = 0x8000000

    #
    # When a section with this flag is being linked, then if the size of
    # the input section is less than a page, it should not cross a page
    # boundary.  If the size of the input section is one page or more,
    # it should be aligned on a page boundary.  This is for TI
    # TMS320C54X only.
    #
    TIC54X_BLOCK = 0x10000000

    #
    # Conditionally link this section; do not link if there are no
    # references found to any symbol in the section.  This is for TI
    # TMS320C54X only.
    #
    TIC54X_CLINK = 0x20000000

    #
    # Indicate that section has the no read flag set. This happens
    # when memory read flag isn't set.
    #
    COFF_NOREAD = 0x40000000

    #
    #  End of section flags.
    #


SECTION_FLAGS_LIST = (
    SectionFlags.NO_FLAGS,
    SectionFlags.ALLOC,
    SectionFlags.LOAD,
    SectionFlags.RELOC,
    SectionFlags.READONLY,
    SectionFlags.CODE,
    SectionFlags.DATA,
    SectionFlags.ROM,
    SectionFlags.CONSTRUCTOR,
    SectionFlags.HAS_CONTENTS,
    SectionFlags.NEVER_LOAD,
    SectionFlags.THREAD_LOCAL,
    SectionFlags.HAS_GOT_REF,
    SectionFlags.IS_COMMON,
    SectionFlags.DEBUGGING,
    SectionFlags.IN_MEMORY,
    SectionFlags.EXCLUDE,
    SectionFlags.SORT_ENTRIES,
    SectionFlags.LINK_ONCE,
    SectionFlags.LINK_DUPLICATES,
    SectionFlags.LINK_DUPLICATES_DISCARD,
    SectionFlags.LINK_DUPLICATES_ONE_ONLY,
    SectionFlags.LINK_DUPLICATES_SAME_SIZE,
    SectionFlags.LINK_DUPLICATES_SAME_CONTENTS,
    SectionFlags.LINKER_CREATED,
    SectionFlags.KEEP,
    SectionFlags.SMALL_DATA,
    SectionFlags.MERGE,
    SectionFlags.STRINGS,
    SectionFlags.GROUP,
    SectionFlags.COFF_SHARED_LIBRARY,
    SectionFlags.ELF_REVERSE_COPY,
    SectionFlags.COFF_SHARED,
    SectionFlags.TIC54X_BLOCK,
    SectionFlags.TIC54X_CLINK,
    SectionFlags.COFF_NOREAD,
    )

SECTION_FLAGS_NAMES = {
    SectionFlags.NO_FLAGS                       : "NO_FLAGS",
    SectionFlags.ALLOC                          : "ALLOC",
    SectionFlags.LOAD                           : "LOAD",
    SectionFlags.RELOC                          : "RELOC",
    SectionFlags.READONLY                       : "READONLY",
    SectionFlags.CODE                           : "CODE",
    SectionFlags.DATA                           : "DATA",
    SectionFlags.ROM                            : "ROM",
    SectionFlags.CONSTRUCTOR                    : "CONSTRUCTOR",
    SectionFlags.HAS_CONTENTS                   : "HAS_CONTENTS",
    SectionFlags.NEVER_LOAD                     : "NEVER_LOAD",
    SectionFlags.THREAD_LOCAL                   : "THREAD_LOCAL",
    SectionFlags.HAS_GOT_REF                    : "HAS_GOT_REF",
    SectionFlags.IS_COMMON                      : "IS_COMMON",
    SectionFlags.DEBUGGING                      : "DEBUGGING",
    SectionFlags.IN_MEMORY                      : "IN_MEMORY",
    SectionFlags.EXCLUDE                        : "EXCLUDE",
    SectionFlags.SORT_ENTRIES                   : "SORT_ENTRIES",
    SectionFlags.LINK_ONCE                      : "LINK_ONCE",
    SectionFlags.LINK_DUPLICATES                : "LINK_DUPLICATES",
    SectionFlags.LINK_DUPLICATES_DISCARD        : "LINK_DUPLICATES_DISCARD",
    SectionFlags.LINK_DUPLICATES_ONE_ONLY       : "LINK_DUPLICATES_ONE_ONLY",
    SectionFlags.LINK_DUPLICATES_SAME_SIZE      : "LINK_DUPLICATES_SAME_SIZE",
    SectionFlags.LINK_DUPLICATES_SAME_CONTENTS  : "LINK_DUPLICATES_SAME_CONTENTS ",
    SectionFlags.LINKER_CREATED                 : "LINKER_CREATED",
    SectionFlags.KEEP                           : "KEEP",
    SectionFlags.SMALL_DATA                     : "SMALL_DATA",
    SectionFlags.MERGE                          : "MERGE",
    SectionFlags.STRINGS                        : "STRINGS",
    SectionFlags.GROUP                          : "GROUP",
    SectionFlags.COFF_SHARED_LIBRARY            : "COFF_SHARED_LIBRARY",
    SectionFlags.ELF_REVERSE_COPY               : "ELF_REVERSE_COPY",
    SectionFlags.COFF_SHARED                    : "COFF_SHARED",
    SectionFlags.TIC54X_BLOCK                   : "TIC54X_BLOCK",
    SectionFlags.TIC54X_CLINK                   : "TIC54X_CLINK",
    SectionFlags.COFF_NOREAD                    : "COFF_NOREAD",
}

SectionAttributes = enum(
    "INDEX",
    "NAME",
    "SIZE",
    "VMA",
    "LMA",
    "ALIGNMENT",
    "FLAGS",
    "FILE_POS",
    "ENTSIZE"
    )


class BfdSectionException(BfdException):
    """Generic bfd section exception."""
    pass


class BfdSection(object):
    """BFD section module handler."""

    def __init__(self, bfd, section):
        """Initialize BFD section instance."""
        self._ptr = section
        self.bfd = bfd

        if not bfd:
            raise BfdSectionException("Invalid BFD specified.")

        if not section:
            raise BfdSectionException("Invalid BFD asection specified.")

    @property
    def bfd(self):
        return self._bfd

    @bfd.setter
    def bfd(self, bfd):
        self._bfd = bfd

    @property
    def ptr(self):
        return self._ptr

    @ptr.setter
    def ptr(self, ptr):
        self._ptr = ptr

    @property
    def index(self):
        #return self._index
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.INDEX)

    #@index.setter
    #def index(self, index):
    #    self._index = index

    @property
    def name(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.NAME)
        #return self._name

    #@name.setter
    #def name(self, name):
    #    self._name = name

    @property
    def size(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.SIZE)
        #return self._size

    #@size.setter
    #def size(self, size):
    #    self._size = size

    @property
    def vma(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.VMA)
        #return self._vma

    #@vma.setter
    #def vma(self, vma):
    #    self._vma = vma

    @property
    def lma(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.LMA)
        #return self._lma

    #@lma.setter
    #def lma(self, lma):
    #    self._lma = lma

    @property
    def alignment(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.ALIGNMENT)
        #return self._alignment

    #@alignment.setter
    #def alignment(self, alignment):
    #    self._alignment = alignment

    @property
    def flags(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.FLAGS)
        #return self._flags

    #@flags.setter
    #def flags(self, flags):
    #    self._flags = flags

    @property
    def file_offset(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.FILE_POS)
        #return self._file_offset

    #@file_offset.setter
    #def file_offset(self, file_offset):
    #    self._file_offset = file_offset

    @property
    def entry_size(self):
        return _bfd.get_section_attribute(self._ptr, SectionAttributes.ENTSIZE)

    @property
    def content(self):
        """Return the entire section content."""
        return _bfd.section_get_content(self.bfd, self._ptr, 0, self.size)

    def get_content(self, offset, size):
        """Return the specified number of bytes from the current section."""
        return _bfd.section_get_content(self.bfd, self._ptr, offset, size)

    def __str__(self):
        """Return section string representation."""
        return self.name
