# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part PyBFD module (libbfd & libopcodes extension module)
#

from bfd_archs import *


class BfdFormat:
  UNKNOWN = 0   # File format is unknown.
  OBJECT = 1    # Linker/assembler/compiler output.
  ARCHIVE = 2   # Object archive file
  CORE = 3      # Core dump.


BfdFormatNamesLong = {
    BfdFormat.UNKNOWN       : "File format is unknown.",
    BfdFormat.OBJECT        : "Linker/assembler/compiler output.",
    BfdFormat.ARCHIVE       : "Object archive file",
    BfdFormat.CORE          : "Core dump."
}


class BfdError:
  NO_ERROR = 0,
  SYSTEM_CALL = 1
  INVALID_TARGET = 2
  WRONG_FORMAT = 3
  WRONG_OBJECT_FORMAT = 4
  INVALID_OPERATION = 5
  NO_MEMORY = 6
  NO_SYMBOLS = 7
  NO_ARMAP = 8
  NO_MORE_ARCHIVED_FILES = 9
  MALFORMED_ARCHIVE = 10
  FILE_NOT_RECOGNIZED = 11
  FILE_AMBIGUOUSLY_RECOGNIZED = 12
  NO_CONTENTS = 13
  NONREPRESENTABLE_SECTION = 14
  NO_DEBUG_SECTION = 15
  BAD_VALUE = 16
  FILE_TRUNCATED = 17
  FILE_TOO_BIG = 18
  ON_INPUT = 19
  INVALID_ERROR_COD = 20


class BfdFlags:
    # Values that may appear in the flags field of a BFD.  These also appear in the
    # object_flags field of the bfd_target structure, where they indicate the set
    # of flags used by that backend (not all flags are meaningful for all object
    # file formats) (FIXME: at the moment, the object_flags values have mostly just
    # been copied from backend to another, and are not necessarily correct).

    BFD_NO_FLAGS   = 0x00

    # BFD contains relocation entries.
    HAS_RELOC      = 0x01

    # BFD is directly executable.
    EXEC_P         = 0x02

    # BFD has line number information (basically used for F_LNNO in a COFF header).
    HAS_LINENO     = 0x04

    # BFD has debugging information.
    HAS_DEBUG      = 0x08

    # BFD has symbols.
    HAS_SYMS       = 0x10

    # BFD has local symbols (basically used for F_LSYMS in a COFF header).
    HAS_LOCALS     = 0x20

    # BFD is a dynamic object.
    DYNAMIC        = 0x40

    # Text section is write protected (if D_PAGED is not set, this is like an a.out
    # NMAGIC file) (the linker sets this by default, but clears it for -r or -N).
    WP_TEXT        = 0x80

    # BFD is dynamically paged (this is like an a.out ZMAGIC file) (the linker sets
    # this by default, but clears it for -r or -n or -N).
    D_PAGED        = 0x100

    # BFD is relaxable (this means that bfd_relax_section may be able to do
    # something) (sometimes bfd_relax_section can do something even if this is not
    # set).
    BFD_IS_RELAXABLE = 0x200

    # This may be set before writing out a BFD to request using a traditional
    # format.  For example, this is used to request that when writing out an a.out
    # object the symbols not be hashed to eliminate duplicates.
    BFD_TRADITIONAL_FORMAT = 0x400

    # This flag indicates that the BFD contents are actually cached in memory.  If
    # this is set, iostream points to a bfd_in_memory struct.
    BFD_IN_MEMORY = 0x800

    # The sections in this BFD specify a memory page.
    HAS_LOAD_PAGE = 0x1000

    # This BFD has been created by the linker and doesn't correspond to any input
    # file,
    BFD_LINKER_CREATED = 0x2000

    # This may be set before writing out a BFD to request that it be written using
    # values for UIDs, GIDs, timestamps, etc. that will be consistent from run to
    # run.
    BFD_DETERMINISTIC_OUTPUT = 0x4000

    # Compress sections in this BFD.
    BFD_COMPRESS = 0x8000

    # Decompress sections in this BFD.
    BFD_DECOMPRESS = 0x10000

    # BFD is a dummy, for plugins.
    BFD_PLUGIN = 0x20000

    # Flags bits to be saved in bfd_preserve_save.
    BFD_FLAGS_SAVED  = \
      BFD_IN_MEMORY | BFD_COMPRESS | BFD_DECOMPRESS | BFD_PLUGIN

    # Flags bits which are for BFD use only.
    BFD_FLAGS_FOR_BFD_USE_MASK  = \
      BFD_IN_MEMORY | BFD_COMPRESS | BFD_DECOMPRESS | BFD_LINKER_CREATED \
       | BFD_PLUGIN | BFD_TRADITIONAL_FORMAT | BFD_DETERMINISTIC_OUTPUT

BFD_FLAGS_LIST = (
    BfdFlags.BFD_NO_FLAGS,
    BfdFlags.HAS_RELOC,
    BfdFlags.EXEC_P,
    BfdFlags.HAS_LINENO,
    BfdFlags.HAS_DEBUG,
    BfdFlags.HAS_SYMS,
    BfdFlags.HAS_LOCALS,
    BfdFlags.DYNAMIC,
    BfdFlags.WP_TEXT,
    BfdFlags.D_PAGED,
    BfdFlags.BFD_IS_RELAXABLE,
    BfdFlags.BFD_TRADITIONAL_FORMAT,
    BfdFlags.BFD_IN_MEMORY,
    BfdFlags.HAS_LOAD_PAGE,
    BfdFlags.BFD_LINKER_CREATED,
    BfdFlags.BFD_DETERMINISTIC_OUTPUT,
    BfdFlags.BFD_COMPRESS,
    BfdFlags.BFD_DECOMPRESS,
    BfdFlags.BFD_PLUGIN,
    BfdFlags.BFD_FLAGS_SAVED,
    BfdFlags.BFD_FLAGS_FOR_BFD_USE_MASK,
    )

BFD_FLAGS_NAMES_SHORT = {
    BfdFlags.BFD_NO_FLAGS : "BFD_NO_FLAGS",
    BfdFlags.HAS_RELOC : "HAS_RELOC",
    BfdFlags.EXEC_P : "EXEC_P",
    BfdFlags.HAS_LINENO : "HAS_LINENO",
    BfdFlags.HAS_DEBUG : "HAS_DEBUG",
    BfdFlags.HAS_SYMS : "HAS_SYMS",
    BfdFlags.HAS_LOCALS : "HAS_LOCALS",
    BfdFlags.DYNAMIC : "DYNAMIC",
    BfdFlags.WP_TEXT : "WP_TEXT",
    BfdFlags.D_PAGED : "D_PAGED",
    BfdFlags.BFD_IS_RELAXABLE : "BFD_IS_RELAXABLE",
    BfdFlags.BFD_TRADITIONAL_FORMAT : "BFD_TRADITIONAL_FORMAT",
    BfdFlags.BFD_IN_MEMORY : "BFD_IN_MEMORY",
    BfdFlags.HAS_LOAD_PAGE : "HAS_LOAD_PAGE",
    BfdFlags.BFD_LINKER_CREATED : "BFD_LINKER_CREATED",
    BfdFlags.BFD_DETERMINISTIC_OUTPUT : "BFD_DETERMINISTIC_OUTPUT",
    BfdFlags.BFD_COMPRESS : "BFD_COMPRESS",
    BfdFlags.BFD_DECOMPRESS : "BFD_DECOMPRESS",
    BfdFlags.BFD_PLUGIN : "BFD_PLUGIN",
    BfdFlags.BFD_FLAGS_SAVED : "BFD_FLAGS_SAVED",
    BfdFlags.BFD_FLAGS_FOR_BFD_USE_MASK : "BFD_FLAGS_FOR_BFD_USE_MASK",
    }

SUPPORTED_ENDIAN = [
    ENDIAN_BIG,
    ENDIAN_LITTLE,
    ENDIAN_UNKNOWN,
    ]

#
# Instruction attributes
#
IA_STOP = 0x00001 #  Instruction doesn't pass execution to the next instruction
IA_CALL = 0x00002 #  CALL instruction (should make a procedure here)
IA_CHG1 = 0x00004 #  The instruction modifies the first operand
IA_CHG2 = 0x00008 #  The instruction modifies the second operand
IA_CHG3 = 0x00010 #  The instruction modifies the third operand
IA_CHG4 = 0x00020 #  The instruction modifies 4 operand
IA_CHG5 = 0x00040 #  The instruction modifies 5 operand
IA_CHG6 = 0x00080 #  The instruction modifies 6 operand
IA_USE1 = 0x00100 #  The instruction uses value of the first operand
IA_USE2 = 0x00200 #  The instruction uses value of the second operand
IA_USE3 = 0x00400 #  The instruction uses value of the third operand
IA_USE4 = 0x00800 #  The instruction uses value of the 4 operand
IA_USE5 = 0x01000 #  The instruction uses value of the 5 operand
IA_USE6 = 0x02000 #  The instruction uses value of the 6 operand
IA_JUMP = 0x04000 #  The instruction passes execution using indirect jump or call (thus needs additional analysis)
IA_SHFT = 0x08000 #  Bit-shift instruction (shl,shr...)
IA_HLL  = 0x10000 #  Instruction may be present in a high level language function.

INSTRUCTION_ATTRIBUTES = (
    IA_STOP,
    IA_CALL,
    IA_CHG1,
    IA_CHG2,
    IA_CHG3,
    IA_CHG4,
    IA_CHG5,
    IA_CHG6,
    IA_USE1,
    IA_USE2,
    IA_USE3,
    IA_USE4,
    IA_USE5,
    IA_USE6,
    IA_JUMP,
    IA_SHFT,
    IA_HLL
)

def enum(*sequential, **named):
    enums = dict(zip(sequential, range(len(sequential))), **named)
    return type('Enum', (), enums)


class BfdException(Exception):
    """Generic BFD module exception."""
    pass

def get_architecture_name(arch_index):
    """Return the architecture name accoding to its index."""
    if arch_index in SUPPORTED_ARCHS_NAMES:
        return SUPPORTED_ARCHS_NAMES[arch_index]

    return None
