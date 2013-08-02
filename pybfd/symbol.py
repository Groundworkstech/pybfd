# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part PyBFD module (libbfd & libopcodes extension module)
#

from collections import namedtuple

from bfd_base import BfdException

__author__      = "Groundworks Technologies OSS Team"
__contact__     = "oss@groundworkstech.com"
__company__     = "Groundworks Technologies"
__year__        = "2013"
__versaion__    = "0.1"

__all__ = ["Symbol", "SymbolFlags", "SYMBOL_FLAGS_LIST", "SYMBOL_FLAGS_NAMES_SHORT"]


class SymbolFlags:
    #  Attributes of a symbol.
    NO_FLAGS = 0x00

    #  The symbol has local scope; <<static>> in <<C>>. The value
    #  is the offset into the section of the data.
    LOCAL = 1 << 0

    #  The symbol has global scope; initialized data in <<C>>. The
    #  value is the offset into the section of the data.
    GLOBAL = 1 << 1

    #  The symbol has global scope and is exported. The value is
    #  the offset into the section of the data.
    EXPORT = GLOBAL # No real difference.

    #  A normal C symbol would be one of:
    #  <<LOCAL>>, <<COMMON>>,  <<UNDEFINED>> or
    #  <<GLOBAL>>.

    #  The symbol is a debugging record. The value has an arbitrary
    #  meaning, unless DEBUGGING_RELOC is also set.
    DEBUGGING = 1 << 2

    #  The symbol denotes a function entry point.  Used in ELF,
    #  perhaps others someday.
    FUNCTION = 1 << 3

    #  Used by the linker.
    KEEP = 1 << 5
    KEEP_G = 1 << 6

    #  A weak global symbol, overridable without warnings by
    #  a regular global symbol of the same name.
    WEAK = 1 << 7

    #  This symbol was created to point to a section, e.g. ELF's
    #  STT_SECTION symbols.
    SECTION_SYM = 1 << 8

    #  The symbol used to be a common symbol, but now it is
    #  allocated.
    OLD_COMMON = 1 << 9

    #  In some files the type of a symbol sometimes alters its
    #  location in an output file - ie in coff a <<ISFCN>> symbol
    #  which is also <<C_EXT>> symbol appears where it was
    #  declared and not at the end of a section.  This bit is set
    #  by the target BFD part to convey this information.
    NOT_AT_END = 1 << 10

    #  Signal that the symbol is the label of constructor section.
    CONSTRUCTOR = 1 << 11

    #  Signal that the symbol is a warning symbol.  The name is a
    #  warning.  The name of the next symbol is the one to warn about;
    #  if a reference is made to a symbol with the same name as the next
    #  symbol, a warning is issued by the linker.
    WARNING = 1 << 12

    #  Signal that the symbol is indirect.  This symbol is an indirect
    #  pointer to the symbol with the same name as the next symbol.
    INDIRECT = 1 << 13

    #  FILE marks symbols that contain a file name.  This is used
    #  for ELF STT_FILE symbols.
    FILE = 1 << 14

    #  Symbol is from dynamic linking information.
    DYNAMIC = 1 << 15

    #  The symbol denotes a data object.  Used in ELF, and perhaps
    #  others someday.
    OBJECT = 1 << 16

    #  This symbol is a debugging symbol.  The value is the offset
    #  into the section of the data.  DEBUGGING should be set
    #  as well.
    DEBUGGING_RELOC = 1 << 17

    #  This symbol is thread local.  Used in ELF.
    THREAD_LOCAL = 1 << 18

    #  This symbol represents a complex relocation expression,
    #  with the expression tree serialized in the symbol name.
    RELC = 1 << 19

    #  This symbol represents a signed complex relocation expression,
    #  with the expression tree serialized in the symbol name.
    SRELC = 1 << 20

    #  This symbol was created by bfd_get_synthetic_symtab.
    SYNTHETIC = 1 << 21


    #  This symbol is an indirect code object.  Unrelated to INDIRECT.
    #  The dynamic linker will compute the value of this symbol by
    #  calling the function that it points to.  FUNCTION must
    #  also be also set.
    GNU_INDIRECT_FUNCTION = 1 << 22

    #  This symbol is a globally unique data object.  The dynamic linker
    #  will make sure that in the entire process there is just one symbol
    #  with this name and type in use.  OBJECT must also be set.
    GNU_UNIQUE = 1 << 23

SYMBOL_FLAGS_LIST = (
    SymbolFlags.NO_FLAGS,
    SymbolFlags.LOCAL,
    SymbolFlags.GLOBAL,
    SymbolFlags.EXPORT,
    SymbolFlags.DEBUGGING,
    SymbolFlags.FUNCTION,
    SymbolFlags.KEEP_G,
    SymbolFlags.WEAK,
    SymbolFlags.SECTION_SYM,
    SymbolFlags.OLD_COMMON,
    SymbolFlags.NOT_AT_END,
    SymbolFlags.CONSTRUCTOR,
    SymbolFlags.WARNING,
    SymbolFlags.INDIRECT,
    SymbolFlags.FILE,
    SymbolFlags.DYNAMIC,
    SymbolFlags.OBJECT,
    SymbolFlags.DEBUGGING_RELOC,
    SymbolFlags.THREAD_LOCAL,
    SymbolFlags.RELC,
    SymbolFlags.SRELC,
    SymbolFlags.SYNTHETIC,
    SymbolFlags.GNU_INDIRECT_FUNCTION,
    SymbolFlags.GNU_UNIQUE,
)

SYMBOL_FLAGS_NAMES_SHORT = {
    SymbolFlags.NO_FLAGS : "NO_FLAGS",
    SymbolFlags.LOCAL : "LOCAL",
    SymbolFlags.GLOBAL : "GLOBAL",
    SymbolFlags.EXPORT : "EXPORT",
    SymbolFlags.DEBUGGING : "DEBUGGING",
    SymbolFlags.FUNCTION : "FUNCTION",
    SymbolFlags.KEEP_G : "KEEP_G",
    SymbolFlags.WEAK : "WEAK",
    SymbolFlags.SECTION_SYM : "SECTION_SYM",
    SymbolFlags.OLD_COMMON : "OLD_COMMON",
    SymbolFlags.NOT_AT_END : "NOT_AT_END",
    SymbolFlags.CONSTRUCTOR : "CONSTRUCTOR",
    SymbolFlags.WARNING : "WARNING",
    SymbolFlags.INDIRECT : "INDIRECT",
    SymbolFlags.FILE : "FILE",
    SymbolFlags.DYNAMIC : "DYNAMIC",
    SymbolFlags.OBJECT : "OBJECT",
    SymbolFlags.DEBUGGING_RELOC : "DEBUGGING_RELOC",
    SymbolFlags.THREAD_LOCAL : "THREAD_LOCAL",
    SymbolFlags.RELC : "RELC",
    SymbolFlags.SRELC : "SRELC",
    SymbolFlags.SYNTHETIC : "SYNTHETIC",
    SymbolFlags.GNU_INDIRECT_FUNCTION : "GNU_INDIRECT_FUNCTION",
    SymbolFlags.GNU_UNIQUE : "GNU_UNIQUE",
}

# A pointer to the BFD which owns the symbol. This information is necessary so
# that a back end can work out what additional information (invisible to the
# application writer) is carried with the symbol.
Symbol = namedtuple("Symbol", "section, name, value, flags")
