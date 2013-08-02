#!/usr/bin/env python
# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part PyBFD module (libbfd & libopcodes extension module)
#

import string
from collections import namedtuple

from sys import version_info
if version_info >= (2,6,0):
    def import_helper():
        from os.path import dirname
        import imp
        fp = None
        try:
            fp, pathname, description = imp.find_module('_opcodes', [dirname(__file__)])
        except ImportError:
            import _opcodes
            return _opcodes
        if fp is not None:
            try:
                _mod = imp.load_module('_opcodes', fp, pathname, description)
            finally:
                fp.close()
            return _mod
    _opcodes = import_helper()
    del import_helper
else:
    import _opcodes
del version_info

from bfd_archs import *
from bfd_base import *

__author__      = "Groundworks Technologies OSS Team"
__contact__     = "oss@groundworkstech.com"
__company__     = "Groundworks Technologies"
__year__        = "2013"
__versaion__    = "0.1"


class InstructionType:
    NON_INSN = 0    # Not a valid instruction.
    NON_BRANCH = 1  # Not a branch instruction.
    BRANCH = 2      # Unconditional branch.
    COND_BRANCH = 3 # Conditional branch.
    JSR = 4         # Jump to subroutine.
    COND_JSR = 5    # Conditional jump to subroutine.
    DREF = 6        # Data reference instruction.
    DREF2 = 7       # Two data references in instruction.

PYBFD_DISASM_CONTINUE = 0
PYBFD_DISASM_STOP = 1


class OpcodesException(Exception):
    """Generic opcodes module exception."""
    pass


class Opcodes(object):
    """Class for libOpcodes abstraction."""

    def __init__(self, *args, **kwargs):
        """..."""
        # Hold the native internal structure.
        self._ptr = None

        # Determine if the specified paramter is a BFD or a tuple specifying
        # arch/machine/endian.
        try:            
            # FIXME: why we don't use isintance?
            if args[0].__class__.__name__ == "Bfd":
                self.initialize_bfd(args[0])
            else:
                self.initialize_non_bfd(*args)
        except IndexError, err:
            pass
        except TypeError, err:
            raise OpcodesException(err)

    def initialize_bfd(self, abfd):
        """Initialize underlying libOpcodes library using BFD."""
        self._ptr = _opcodes.initialize_bfd(abfd._ptr)              

        # Already done inside opcodes.c
        #self.architecture = abfd.architecture
        #self.machine = abfd.machine
        #self.endian = abfd.endian

        # force intel syntax
        if self.architecture == ARCH_I386:
            if abfd.arch_size == 32:
                self.machine = MACH_I386_I386_INTEL_SYNTAX
                #abfd.machine = MACH_I386_I386_INTEL_SYNTAX
            elif abfd.arch_size == 64:
                self.machine = MACH_X86_64_INTEL_SYNTAX
                #abfd.machine = MACH_X86_64_INTEL_SYNTAX

    def initialize_non_bfd(self, architecture=None, machine=None,
        endian=ENDIAN_UNKNOWN):
        """Initialize underlying libOpcodes library not using BFD."""

        if None in [architecture, machine, endian]:
            return

        self.architecture = architecture
        self.machine = machine
        self.endian = endian

    def initialize_smart_disassemble(self, data, start_address=0):
        """
        Set the binary buffer to disassemble with other related information
        ready for an instruction by instruction disassembly session.
        
        """
        _opcodes.initialize_smart_disassemble(
            self._ptr, data, start_address)

    def start_smart_disassemble(self, start_address, callback):
        """
        Invok the callback function for every instruction disassembled at the
        previously initialized smart session with the given offset from the
        start address supplied (also in the initialization).

        """
        _opcodes.start_smart_disassemble(self._ptr, start_address, callback)

    def print_single_instruction_callback(self, address, size, branch_delay_insn,
        insn_type, target, target2, disassembly):
        """
        Callack on each disassembled instruction to print its information.
        
        """
        print "0x%X SZ=%d BD=%d IT=%d\t%s" % \
            (address, size, branch_delay_insn, insn_type, disassembly)

        return PYBFD_DISASM_CONTINUE  # keep moving

    def disassemble(self, data, start_address=0):
        """
        Return a list containing the virtual memory address, instruction length
        and disassembly code for the given binary buffer.
        
        """
        return _opcodes.disassemble(self._ptr, data, start_address)

    @property
    def architecture(self):
        return _opcodes.get_architecture(self._ptr)

    @architecture.setter
    def architecture(self, architecture):
        if self._ptr is not None:
            self._ptr = _opcodes.deinitialize(self._ptr)

        self._ptr = _opcodes.set_architecture(architecture)

        self._architecture = architecture

    @property
    def machine(self):
        return _opcodes.get_machine(self._ptr)

    @machine.setter
    def machine(self, machine):
        _opcodes.set_machine(self._ptr, machine)
        self._machine = machine

    @property
    def endian(self):
        return _opcodes.get_endian(self._ptr)

    @endian.setter
    def endian(self, endian):
        _opcodes.set_endian(self._ptr, endian)
        self._endian = endian

    @property
    def architecture_name(self):
        """Return the current architecture name accoding to its index."""
        return get_architecture_name(self.architecture)

def main():
    """Test case for simple opcode disassembly."""
    test_targets = (    
        [ARCH_I386, MACH_I386_I386_INTEL_SYNTAX, ENDIAN_MONO, "\x55\x89\xe5\xE8\xB8\xFF\xFF\xFF", 0x1000],
        [ARCH_I386, MACH_X86_64_INTEL_SYNTAX, ENDIAN_MONO, "\x55\x48\x89\xe5\xE8\xA3\xFF\xFF\xFF", 0x1000],
        [ARCH_ARM, MACH_ARM_2, ENDIAN_LITTLE, "\x04\xe0\x2d\xe5\xED\xFF\xFF\xEB", 0x1000],
        [ARCH_MIPS, MACH_MIPSISA32, ENDIAN_BIG, "\x0C\x10\x00\x97\x00\x00\x00\x00", 0x1000],
        [ARCH_POWERPC, MACH_PPC, ENDIAN_BIG, "\x94\x21\xFF\xE8\x7C\x08\x02\xA6", 0x1000],
        #[ARCH_XTENSA, MACH_XTENSA, ENDIAN_BIG, "\x6C\x10\x06\xD7\x10", 0x1000],
        )

    for target_arch, target_mach, target_endian, binary, address in test_targets:
        #
        # Initialize libopcodes with the current architecture.
        #
        opcodes = Opcodes(target_arch, target_mach, target_endian)

        # Print some architecture-specific information.
        print "\n[+] Architecture %s - Machine %d" % \
            (opcodes.architecture_name, opcodes.machine)

        print "[+] Disassembly:"

        # Print all the disassembled instructions.
        for vma, size, disasm in opcodes.disassemble(binary, address):
            print "0x%X (size=%d)\t %s" % (vma, size, disasm)

if __name__ == "__main__":
    main()

