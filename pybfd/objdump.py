#!/usr/bin/env python
# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part Python pybfd module (libbfd & libopcodes extension module)
#

from sys import argv, exit
from argparse import ArgumentParser, FileType, REMAINDER, Action
from textwrap import dedent

import bfd
from bfd_archs import *
from bfd_base import *
from opcodes import *
from section import *
from symbol import SYMBOL_FLAGS_NAMES_SHORT

__author__      = "Groundworks Technologies OSS Team"
__contact__     = "oss@groundworkstech.com"
__company__     = "Groundworks Technologies"
__year__        = "2013"
__version__     = "0.1"
__description__ = "Python libbfd extension module"

# Inidicate if at least a parameter was specified.
done = False


class BfdActionNoParam(Action):
    """Base class for BFD actions invoked by the argument parser."""

    def __call__(self, parser, namespace, values, option_string=None):
        # Initialize BFD instance and proceed to display the requested
        # information.
        self.bfd = bfd.Bfd()

        self.do_action(parser, namespace, values, option_string)

        global done
        done = True


class ListFormatAndArchitecturesInformationAction(BfdActionNoParam):
    """List object formats and architectures supported."""

    def do_action(self, parser, namespace, values, option_string):

        print "%s %s (%s)" % (parser.prog, __version__, __description__)

        for arch in self.bfd.architectures:
            print " %s" % arch,

        for target in self.bfd.targets:
            print "  %s" % target


class BfdActionWithFileParam(Action):
    """Base class for BFD actions invoked by the argument parser."""

    def __call__(self, parser, namespace, values, option_string=None):
        # Initialize BFD instance and proceed to display the requested
        # information.
        for fd in values:
            try:
                # Create a new BFD from the current file descriptor.
                self.bfd = bfd.Bfd(fd)

                # Display current filename and corresponding architecture.
                print "\n%s:     file format %s\n" % \
                    (self.bfd.filename, self.bfd.architecture)

                # Process the BFD with the user-requested action.
                self.do_action(parser, namespace, values, option_string)

                # Close BFD file and move on.
                self.bfd.close()

                fd.close()

            except BfdException, err:
                print err
            except Exception, err:
                pass

        global done
        done = True


class DumpArchieveHeadersAction(BfdActionWithFileParam):
    """Dump section headers on the user-specified bfd(s)."""

    def do_action(self, parser, namespace, values, option_string):
        raise Exception("Not implemented")


class DumpFileHeadersAction(BfdActionWithFileParam):
    """Dump section headers on the user-specified bfd(s)."""

    def do_action(self, parser, namespace, values, option_string):

        file_flags = self.bfd.file_flags & ~bfd.BFD_FLAGS_FOR_BFD_USE_MASK

        print "architecture: %s:%s, flags 0x%08x:" % \
            (self.bfd.printable_arch, self.bfd.printable_mach,
            #(self.bfd.printable_arch, self.bfd_printable_mach,
            self.bfd.file_flags)

        #bfd_printable_arch_mach (
        #    bfd_get_arch (abfd), bfd_get_mach (abfd)));
        #(_("\n"), abfd->flags & ~BFD_FLAGS_FOR_BFD_USE_MASK);

        for flag in bfd.BFD_FLAGS:
            _flag = flag & file_flags
            if _flag != 0:
                print "%s," % self.bfd.flag_name_shost(flag),

        print "\nstart address 0x%08x" % self.bfd.start_address


class DumpSectionHeadersAction(BfdActionWithFileParam):
    """Dump section headers on the user-specified bfd(s)."""

    def do_action(self, parser, namespace, values, option_string):
        _str = "Sections:\n"

        if (self.bfd.arch_size == 32):
            _str += "Idx Name          Size      VMA       LMA       File off  Algn"
            mem_size_fmt = "%08x"
        else:
            _str += "Idx Name          Size      VMA               LMA               File off  Algn"
            mem_size_fmt = "%016x"

        _str += "\n"

        #
        # Iterate through every section present.
        #
        for section_name in self.bfd.sections:

            section = self.bfd.sections[section_name]

            _str += "%3d %-13s %08x  %s  %s  %08X  2**%d\n" % (
                section.index,
                section.name,
                section.size,
                mem_size_fmt % section.vma,
                mem_size_fmt % section.lma,
                section.file_offset,
                section.alignment
                )

        print _str


class DisassembleSectionAction(BfdActionWithFileParam):
    """Disassemble section content on the user-specified bfd(s)."""

    def do_action(self, parser, namespace, values, option_string):
        #
        # Iterate through every section present.
        #
        opcodes = Opcodes(self.bfd)

        for section_name in self.bfd.sections:

            section = self.bfd.sections[section_name]

            # Skip non-code sections.
            if (section.flags & (SectionFlags.CODE | \
                SectionFlags.HAS_CONTENTS)) != \
                (SectionFlags.CODE | SectionFlags.HAS_CONTENTS):
                continue

            #
            # Obtain the section content and request its disassembly.
            #
            print "\nDisassembly of section %s\n" % section.name
            for vma, size, disasm in opcodes.disassemble(
                section.content, section.vma):
                print "%8x (%d)\t%s" % (vma, size, disasm)


class DisassembleSectionsAction(BfdActionWithFileParam):
    """Disassemble all sections content on the user-specified bfd(s)."""

    def do_action(self, parser, namespace, values, option_string):
        #
        # Iterate through every section present.
        #
        opcodes = Opcodes(self.bfd)

        for section_name in self.bfd.sections:

            section = self.bfd.sections[section_name]

            #
            # Obtain the section content and request its disassembly.
            #
            print "\nDisassembly of section %s\n" % section.name
            for vma, size, disasm in opcodes.disassemble(section.content, section.vma):
                print "%8x (%d)\t%s" % (vma, size, disasm)


class DumpSectionContentAction(BfdActionWithFileParam):
    """Dump section content on the user-specified bfd(s)."""

    def dump(self, src, length=16, start=0, preffix=""):
        """Dump the specified buffer in hex + ASCII format."""
        FILTER = \
            "".join([(len(repr(chr(x)))==3) and chr(x) or '.' \
                for x in xrange(256)])

        result = list()

        for i in xrange(0, len(src), length):
            s           = src[i : i + length]
            hexa        = " ".join(["%02X" % ord(x) for x in s])
            printable   = s.translate(FILTER)

            result.append("%s%08X   %-*s   %s\n" % \
                (preffix, start + i, length * 3, hexa, printable))

        return ''.join(result)

    def do_action(self, parser, namespace, values, option_string):
        #
        # Iterate through every section present.
        #
        for section in self.bfd.sections:
            print "Contents of section %s:" % section.name
            content = section.content
            start = section.vma
            print self.dump(content, length=16, start=start)


class DumpFileSymbols(BfdActionWithFileParam):
    """Disassemble section content on the user-specified bfd(s)."""

    def do_action(self, parser, namespace, values, option_string):
        print "SYMBOL TABLE:"
        for symbol_address in self.bfd.symbols:
            symbol = self.bfd.symbols[symbol_address]
            print "%08x %15s %15s %08x %s" % \
                (symbol_address,
                symbol.section.name,
                symbol.name,
                symbol.value,
                ", ".join(
                    [name for flag, name in \
                        SYMBOL_FLAGS_NAMES_SHORT.iteritems() \
                        if flag in symbol.flags] ))

def init_parser():
    """Initialize option parser."""

    usage = "Usage: %(prog)s <option(s)> <file(s)>"
    description = " Display information from object <file(s)>.\n"
    description += " At least one of the following switches must be given:"

    #
    # Create an argument parser and an exclusive group.
    #
    parser = ArgumentParser(
        usage=usage, description=description, add_help=False)

    group = parser.add_mutually_exclusive_group()

    #
    # Add objdump parameters.
    #
    group.add_argument("-a", "--archive-headers",
        action=DumpArchieveHeadersAction,
        type=FileType("r"), nargs="+",
        help="Display archive header information")

    group.add_argument("-f", "--file-headers",
        action=DumpFileHeadersAction,
        type=FileType("r"), nargs="+",
        help="Display the contents of the overall file header")

    #group.add_argument("-p", "--private-headers",    action="store", type=FileType("r"), nargs="+", help="Display object format specific file header contents")
    #group.add_argument("-P", "--private=OPT,OPT...", action="store", type=FileType("r"), nargs="+", help="Display object format specific contents")

    group.add_argument("-h", "--section-headers",
        action=DumpSectionHeadersAction,
        type=FileType("r"), nargs="+",
        help="Display the contents of the section headers")

    #group.add_argument("-x", "--all-headers",        action="store", type=FileType("r"), nargs="+", help="Display the contents of all headers")

    group.add_argument("-d", "--disassemble",
        action=DisassembleSectionAction,
        type=FileType("r"), nargs="+",
        help="Display assembler contents of executable sections")


    group.add_argument("-D", "--disassemble-all",
        action=DisassembleSectionsAction,
        type=FileType("r"), nargs="+",
        help="Display assembler contents of executable sections")

    #group.add_argument("-S", "--source",             action="store", type=FileType("r"), nargs="+", help="Intermix source code with disassembly")

    group.add_argument("-s", "--full-contents",
        action=DumpSectionContentAction,
        type=FileType("r"), nargs="+",
        help="Display the full contents of all sections requested")

    #group.add_argument("-g", "--debugging",          action="store", type=FileType("r"), nargs="+", help="Display debug information in object file")
    #group.add_argument("-e", "--debugging-tags",     action="store", type=FileType("r"), nargs="+", help="Display debug information using ctags style")
    #group.add_argument("-G", "--stabs",              action="store", type=FileType("r"), nargs="+", help="Display (in raw form) any STABS info in the file")

    #-W[lLiaprmfFsoRt] or")
    #--dwarf[=rawline,=decodedline,=info,=abbrev,=pubnames,=aranges,=macro,=frames,")
    #      =frames-interp,=str,=loc,=Ranges,=pubtypes,")
    #      =gdb_index,=trace_info,=trace_abbrev,=trace_aranges]")
    #                       Display DWARF info in the file")

    group.add_argument("-t", "--syms",
        action=DumpFileSymbols,
        type=FileType("r"), nargs="+",
        help="Display the contents of the symbol table(s)")

    #-T, --dynamic-syms       Display the contents of the dynamic symbol table")
    #-r, --reloc              Display the relocation entries in the file")
    #-R, --dynamic-reloc      Display the dynamic relocation entries in the file")

    group.add_argument("-v", "--version", action="version",
        version="%%(prog)s %s (%s)" % (__version__, __description__),
        help="Display this program's version number")

    group.add_argument("-i", "--info",
        action=ListFormatAndArchitecturesInformationAction,
        nargs=REMAINDER,
        help="List object formats and architectures supported")

    group.add_argument("-H", "--help", action="store_true", default=False,
        help="Display this information")

    return parser

def main():

    # Initialize the command line parser and process the requested file(s).
    parser = init_parser()

    args = parser.parse_args()

    # Display help and leave if nothing was specified.
    if args.help or not done:
        parser.print_help()
        return

if __name__ == "__main__":
    main()
