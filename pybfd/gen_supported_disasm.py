#!/usr/bin/env python
# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part PyBFD module (libbfd & libopcodes extension module)
#

import sys
import os
import re
import subprocess
from StringIO import StringIO

__all__ = [ "generate_supported_disassembler_header",
            "generate_supported_architectures_source",
            "get_supported_architectures",
            "get_supported_machines"]

known_archs = [
  #BFD_ARCH,            BFD_LITTLE_ENDIAN,          BFD_BIG_ENDIAN,             DESCRIPTION
  ("bfd_arch_m68k",     "print_insn_m68k",          "print_insn_m68k",          "Motorola 68xxx"),
  ("bfd_arch_vax",      "print_insn_vax",           "print_insn_vax",           "DEC Vax"),
  ("bfd_arch_i960",     "print_insn_i960",          "print_insn_i960",          "Intel 960"),
  ("bfd_arch_or32",     "print_insn_little_or32",   "print_insn_big_or32",      "OpenRISC 32"),
  ("bfd_arch_sparc",    "print_insn_sparc",         "print_insn_sparc",         "SPARC"),
  ("bfd_arch_spu",      "print_insn_spu",           "print_insn_spu",           "PowerPC SPU"),
  ("bfd_arch_mips",     "print_insn_little_mips",   "print_insn_big_mips",      "MIPS Rxxxx"),
  ("bfd_arch_i386",     "print_insn_i386",          "print_insn_i386",          "Intel 386"),
  ("bfd_arch_l1om",     "print_insn_i386",          "print_insn_i386",          "Intel L1OM"),
  ("bfd_arch_k1om",     "print_insn_i386",          "print_insn_i386",          "Intel K1OM"),
  ("bfd_arch_i860",     "print_insn_i860",          "print_insn_i860",          "Intel 860"),
  ("bfd_arch_i370",     "print_insn_i370",          "print_insn_i370",          "IBM 360/370 Mainframes"),
  ("bfd_arch_m88k",     "print_insn_m88k",          "print_insn_m88k",          "Motorola 88xxx"),
  ("bfd_arch_h8300",    "print_insn_h8300",         "print_insn_h8300",         "Renesas H8/300 (formerly Hitachi H8/300)"),
  ("bfd_arch_pdp11",    "print_insn_pdp11",         "print_insn_pdp11",         "DEC PDP-11"),
  ("bfd_arch_powerpc",  "print_insn_little_powerpc","print_insn_big_powerpc",   "PowerPC"),
  ("bfd_arch_rs6000",   "print_insn_rs6000",        "print_insn_rs6000",        "IBM RS/6000"),
  ("bfd_arch_hppa",     "print_insn_hppa",          "print_insn_hppa",          "HP PA RISC"),
  ("bfd_arch_d10v",     "print_insn_d10v",          "print_insn_d10v",          "Mitsubishi D10V"),
  ("bfd_arch_d30v",     "print_insn_d30v",          "print_insn_d30v",          "Mitsubishi D30V"),
  ("bfd_arch_dlx",      "print_insn_dlx",           "print_insn_dlx",           "DLX"),
  ("bfd_arch_m68hc11",  "print_insn_m68hc11",       "print_insn_m68hc11",       "Motorola 68HC11"),
  ("bfd_arch_m68hc12",  "print_insn_m68hc12",       "print_insn_m68hc1",        "Motorola 68HC12"),
  ("bfd_arch_z8k",      "print_insn_z8002",         "print_insn_z8002",         "Zilog Z8000"),
  ("bfd_arch_h8500",    "print_insn_h8500",         "print_insn_h8500",         "Renesas H8/500 (formerly Hitachi H8/500)"),
  ("bfd_arch_sh",       "print_insn_sh",            "print_insn_sh",            "Renesas / SuperH SH (formerly Hitachi SH)"),
  ("bfd_arch_alpha",    "print_insn_alpha",         "print_insn_alpha",         "Dec Alpha"),
  ("bfd_arch_arm",      "print_insn_little_arm",    "print_insn_big_arm",       "Advanced Risc Machines ARM."),
  ("bfd_arch_ns32k",    "print_insn_ns32k",         "print_insn_ns32k",         "National Semiconductors ns32000"),
  ("bfd_arch_w65",      "print_insn_w65",           "print_insn_w65",           "WDC 65816"),
  ("bfd_arch_tic30",    "print_insn_tic30",         "print_insn_tic30",         "Texas Instruments TMS320C30"),
  ("bfd_arch_tic4x",    "print_insn_tic4x",         "print_insn_tic4x",         "Texas Instruments TMS320C3X/4X"),
  ("bfd_arch_tic54x",   "print_insn_tic54x",        "print_insn_tic54x",        "Texas Instruments TMS320C54X"),
  ("bfd_arch_tic6x",    "print_insn_tic6x",         "print_insn_tic6x",         "Texas Instruments TMS320C6X"),
  ("bfd_arch_tic80",    "print_insn_tic80",         "print_insn_tic80",         "TI TMS320c80 (MVP)"),
  ("bfd_arch_v850",     "print_insn_v850",          "print_insn_v85",           "NEC V850"),
  ("bfd_arch_m32c",     "print_insn_m32c",          "print_insn_m32c",          "Renesas M16C/M32C."),
  ("bfd_arch_m32r",     "print_insn_m32r",          "print_insn_m32r",          "Renesas M32R (formerly Mitsubishi M32R/D)"),
  ("bfd_arch_mn10200",  "print_insn_mn10200",       "print_insn_mn10200",       "Matsushita MN10200"),
  ("bfd_arch_mn10300",  "print_insn_mn10300",       "print_insn_mn10300",       "Matsushita MN10300"),
  ("bfd_arch_fr30",     "print_insn_fr30",          "print_insn_fr30",          "Fujitsu FR30"),
  ("bfd_arch_frv",      "print_insn_frv",           "print_insn_frv",           "Fujitsu FRV"),
  ("bfd_arch_moxie",    "print_insn_moxie",         "print_insn_moxie",         "The moxie processor"),
  ("bfd_arch_mcore",    "print_insn_mcore",         "print_insn_mcore",         "Motorola MCore"),
  ("bfd_arch_mep",      "print_insn_mep",           "print_insn_mep",           "Toshiba Media Embedded Processor (MEP)"),
  ("bfd_arch_ia64",     "print_insn_ia64",          "print_insn_ia64",          "HP/Intel ia64"),
  ("bfd_arch_ip2k",     "print_insn_ip2k",          "print_insn_ip2",           "Ubicom IP2K microcontrollers."),
  ("bfd_arch_iq2000",   "print_insn_iq2000",        "print_insn_iq2000",        "Vitesse IQ2000."),
  ("bfd_arch_mt",       "print_insn_mt",            "print_insn_mt",            "Morpho Technologies MT"),
  ("bfd_arch_pj",       "print_insn_pj",            "print_insn_pj",            "Pico Java architecture"),
  ("bfd_arch_avr",      "print_insn_avr",           "print_insn_avr",           "Atmel AVR microcontrollers."),
  ("bfd_arch_bfin",     "print_insn_bfin",          "print_insn_bfin",          "ADI Blackfin"),
  ("bfd_arch_cr16",     "print_insn_cr16",          "print_insn_cr16",          "National Semiconductor CompactRISC (ie CR16)."),
  ("bfd_arch_cr16c",    "print_insn_cr16",          "print_insn_cr16",          "National Semiconductor CompactRISC."),
  ("bfd_arch_crx",      "print_insn_crx",           "print_insn_crx",           "National Semiconductor CRX."),
  ("bfd_arch_rx",       "print_insn_rx",            "print_insn_rx",            "Renesas RX."),
  ("bfd_arch_s390",     "print_insn_s390",          "print_insn_s390",          "IBM s390"),
  ("bfd_arch_score",    "print_insn_little_score",  "print_insn_big_score",     "Sunplus score"),
  ("bfd_arch_openrisc", "print_insn_openrisc",      "print_insn_openrisc",      "OpenRISC"),
  ("bfd_arch_mmix",     "print_insn_mmix",          "print_insn_mmix",          "Donald Knuth educational processor."),
  ("bfd_arch_xstormy16","print_insn_xstormy16",     "print_insn_xstormy16",     "XStormy16"),
  ("bfd_arch_msp430",   "print_insn_msp430",        "print_insn_msp430",        "Texas Instruments MSP430 architecture."),
  ("bfd_arch_xc16x",    "print_insn_xc16x",         "print_insn_xc16x",         "Infineon XC16X Series."),               
  ("bfd_arch_xtensa",   "print_insn_xtensa",        "print_insn_xtensa",        "Tensilica Xtensa cores."),
  ("bfd_arch_z80",      "print_insn_z80",           "print_insn_z80",           "Zilog Z80"),
  ("bfd_arch_lm32",     "print_insn_lm32",          "print_insn_lm32",          "Lattice Mico32"),
  ("bfd_arch_microblaze","print_insn_microblaze",   "print_insn_microblaze",    "Xilinx MicroBlaze."),
  ("bfd_arch_tilepro",  "print_insn_tilepro",       "print_insn_tilepro",       "Tilera TILEPro"),
  ("bfd_arch_tilegx",   "print_insn_tilegx",        "print_insn_tilegx",        "Tilera TILE-Gx"),
  ("bfd_arch_aarch64",  "print_insn_aarch64",       "print_insn_aarch64",       "ARM AArch64"),
  ("bfd_arch_rl78",     "print_insn_rl78",          "print_insn_rl78",          "RL78"),

  #
  # These architectures are so bizarre that bintuils has no generic dissasemble support.
  #
  # bfd_arch_we32k - AT&T WE32xxx
  # bfd_arch_tahoe - CCI/Harris Tahoe
  # bfd_arch_romp - IBM ROMP PC/RT
  # bfd_arch_convex - Convex
  # bfd_arch_m98k - Motorola 98xxx
  # bfd_arch_pyramid - Pyramid Technology
  # bfd_arch_arc  - ARC Cores
  # bfd_arch_cris - Axis CRIS
]

supported_archs_header = """
#ifndef __SUPPORTED_DISASM_H_
#define __SUPPORTED_DISASM_H_

#include "bfd_headers.h"

//
// Supported architectures
//
typedef struct _supported_disasm
{
    enum bfd_architecture   bfd_arch;
    disassembler_ftype      bfd_print_insn_endian_little;
    disassembler_ftype      bfd_print_insn_endian_big;
} supported_disasm, *p_supported_disasm;


supported_disasm p_supported_disasm_list[]= {
%s
};

#endif // __SUPPORTED_DISASM_H_
"""

header_arch_entry = "    {%s, %s, %s}"

pybfd_arch_entry = "    py_const_def(%s, %s)"

pybfd_mach_entry = "    py_const_def(%s, %s)"

gen_bfd_archs_code = r"""
#include "bfd_headers.h"
#include <stdio.h>

#define py_comment_ml(cmt) fprintf(fd, "#\n# " cmt "\n#\n");

#define py_empty_line fprintf(fd, "\n");

#define py_const_def(c,v) fprintf(fd, #c " = %%d\n", v);

//
// Name : write_architectures_constants
//
void write_architectures_constants(FILE* fd)
{
    py_comment_ml("Supported architectures.")

%s
}

//
// Name : write_endianess_constants
//
void write_endianess_constants(FILE* fd)
{
    py_comment_ml("Supported endianess.")

    py_const_def(ENDIAN_BIG      , BFD_ENDIAN_BIG)
    py_const_def(ENDIAN_LITTLE   , BFD_ENDIAN_LITTLE)
    py_const_def(ENDIAN_UNKNOWN  , BFD_ENDIAN_UNKNOWN)
    py_const_def(ENDIAN_MONO     , BFD_ENDIAN_UNKNOWN)

    py_empty_line
}

//
// Name : write_machines_constants
//
void write_machines_constants(FILE* fd)
{
    py_comment_ml("Supported machines")

%s
}

//
// Name : main
//
int main(int argc, char* argv[])
//int _start(int argc, char** argv[])
{
    FILE *fd = stdout;
    //
    // Step 1. Create file header.
    //
    py_comment_ml("This file was automagically generated.")

    //
    // Step 2. Create architectures list.
    //
    write_architectures_constants(fd);

    //
    // Step 3. Create endian list.
    //
    write_endianess_constants(fd);

    //
    // Step 4. Create machines list.
    //
    write_machines_constants(fd);

    fclose(fd);

    return 0;
}

"""

def generate_supported_disassembler_header(supported_archs):
    """Extract export symbols using binutils's nm utility from Binutils and
    generate a current header for PyBFD.

    """
    arch_entries = []

    for arch, little, big, comment in supported_archs:
        arch_entries.append( header_arch_entry % (arch, little, big) )

    return supported_archs_header % ( ",\n".join(arch_entries) )

def generate_supported_architectures_source(supported_archs, supported_machines):
    """Extract export symbols using binutils's nm utility from Binutils and
    generate a current header for PyBFD.

    """
    arch_entries = []
    mach_entries = []

    for arch, little, big, comment in supported_archs:
        arch_entries.append( pybfd_arch_entry % (arch[4 : ].upper(), arch) )

    for mach, value in supported_machines:
        mach_entries.append( pybfd_mach_entry % (mach[4 : ].upper(), value) )

    return gen_bfd_archs_code % (
        "\n".join(arch_entries),
        "\n".join(mach_entries))

def get_supported_architectures(path_to_nm, path_to_libopcodes, supported_machines, shared):
    # Build the command line.
    cmdline = [path_to_nm,]
    if sys.platform != "darwin" and shared:
        cmdline.append("--dynamic")  # Show dynamic symbols (for .so shared
                                     #  object).
    cmdline.append(path_to_libopcodes)

    # Run the nm utility.
    p = subprocess.Popen(cmdline, stdout = subprocess.PIPE)
    stdout, stderr = p.communicate()
    p.wait()

    sym_expr = re.compile("\sT\s(?:_?)(print_insn_.*)")
    
    bigs = dict( [(big,arch) for arch, big, little, comment in known_archs] )
    littles = dict( [(little,arch) for arch, big, little, comment in known_archs] )

    # Buffer the output.
    syms_found = set()
    output = StringIO(stdout)

    for line in output.getvalue().split("\n"):
        m = sym_expr.search( line )
        if m:
            syms_found.add( m.group(1) )

    supported_archs = []

    supported_machines = set( [m[0] for m in supported_machines] )

    for arch, little, big, comment in known_archs:

        if arch == "bfd_arch_k1om" and "bfd_mach_k1om" not in supported_machines:
            continue
        if arch == "bfd_arch_l1om" and "bfd_mach_l1om" not in supported_machines:
            continue

        if little in syms_found and big in syms_found:
            supported_archs.append( (arch, little, big, comment) )


    return supported_archs


def get_supported_machines(path_to_bfd_header):

    with open(path_to_bfd_header, "rt") as fd:
        bfd_header = fd.read()

    supported_machines = []

    machine_expr = re.compile("#define\s(bfd_mach_[a-zA-Z-0-9_]*)\s+(.*)")
    for line in bfd_header.splitlines():
        m = machine_expr.search( line )
        if m:
            supported_machines.append(m.groups())

    return supported_machines



bfd_supported_archs = """
SUPPORTED_ARCHS_NAMES = {
%s
}
SUPPORTED_ARCHS = [
%s
]
"""

bfd_supported_archs_name_entry = "    %s: '%s',"
bfd_supported_archs_entry = "    %s,"

def gen_supported_archs( supported_archs ):

    archs_names = []
    supported_arch_entries = []
    for arch, _, _ , comment in supported_archs:
        archs_names.append( bfd_supported_archs_name_entry  % (arch[4:].upper(), comment) )
        supported_arch_entries.append( bfd_supported_archs_entry % arch[4:].upper() )
    return bfd_supported_archs % ( "\n".join( archs_names ), "\n".join( supported_arch_entries ) )

        
        


