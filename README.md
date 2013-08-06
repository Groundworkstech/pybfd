```
_______             _______   ________  _______  
|       \           |       \ |        \|       \ 
| $$$$$$$\ __    __ | $$$$$$$\| $$$$$$$$| $$$$$$$\
| $$__/ $$|  \  |  \| $$__/ $$| $$__    | $$  | $$
| $$    $$| $$  | $$| $$    $$| $$  \   | $$  | $$
| $$$$$$$ | $$  | $$| $$$$$$$\| $$$$$   | $$  | $$
| $$      | $$__/ $$| $$__/ $$| $$      | $$__/ $$
| $$       \$$    $$| $$    $$| $$      | $$    $$
 \$$       _\$$$$$$$ \$$$$$$$  \$$       \$$$$$$$ 
          |  \__| $$                              
           \$$    $$                              
            \$$$$$$                               
```
PyBFD
=====

## What is PyBFD?

**A Python interface to the GNU Binary File Descriptor (BFD) library.**

It's a complete (or at least tries to be) wrapper around the low level
functionality provided by GNU Binutils libopcodes and libbfd.
This allows the user to manipulate all the supported architectures and file
formats that Binutils tools does.

## Supported architectures

The PyBFD package installer (setup.py) will automatically detect the installed
version of Binutils and extract all its supported architectures.

This includes THREE possibilities:

* The number of supported architectures will depend on the installed version of
    Binutils and the targets specified when it was built.
    Most probably the default installation of Binutils will only support the
    host architecture (i.e. if your host is X86 then Binutils will support only
    x86).

* On certain distributions there is a 'multiarch' package of Binutils. This is
    the same Binutils supporting the same host architecture as well as several
    well-known (and others not being in use since Woodstock :-P). It does not
    include ALL the supported architectures in Binutils but will include the
    ones you'll bump into 99% of the time so that should be enough in most of
    the cases. 
    Also, on Mac OSX Binutils can be installed using [MacPorts](www.macports.org) or [Homebrew](http://brew.sh/).

* You can download and compile Binutils from GNU FTP server. The only rules to
    follow are that it must be compiled as a static library with PIC
    (Position-Independent Code) enabled.
    Binutils source code can be obtained from <http://ftp.gnu.org/gnu/binutils/>

## Supported platforms

* **Linux** (developed under Ubuntu but all Debian derived distros should work).
* **Mac OS X** (MacPorts and Homebrew)
  * on OSX libintl must be installed to compile this extension (i.e. brew install gettext)

Notice: Microsoft Windows is not supported at this time but there are plans to
        support it as well in a near future.

## Installation

There are a couple of ways to download and install PyBFD. Both of them include
downloading the source code and compiling it. 

To install it with the system Binutils it can be done with just one command using
**easy_install** (this is the preferred way for new users !!!).

The other way consists on downloading (either from [PyPi](https://pypi.python.org/pypi/pybfd) or grabbing the latest
source code from [GitHub](https://github.com/Groundworkstech/pybfd)) and compile and link against a version of Binutils
installed on a specific location (i.e. other than /usr/lib).

## Automatically download and install using easy_install

In the following example the package binutils-multiarch was installed:

    $ easy_install pybfd

    <... some output removed ...>

    [+] pybfd 0.1.0 / Supported architectures:
            bfd_arch_m68k        : Motorola 68xxx
            bfd_arch_sparc       : SPARC
            bfd_arch_spu         : PowerPC SPU
            bfd_arch_mips        : MIPS Rxxxx
            bfd_arch_i386        : Intel 386
            bfd_arch_l1om        : Intel L1OM
            bfd_arch_k1om        : Intel K1OM
            bfd_arch_powerpc     : PowerPC
            bfd_arch_rs6000      : IBM RS/6000
            bfd_arch_hppa        : HP PA RISC
            bfd_arch_sh          : Renesas / SuperH SH (formerly Hitachi SH)
            bfd_arch_alpha       : Dec Alpha
            bfd_arch_arm         : Advanced Risc Machines ARM.
            bfd_arch_m32r        : Renesas M32R (formerly Mitsubishi M32R/D)
            bfd_arch_ia64        : HP/Intel ia64
            bfd_arch_s390        : IBM s390
            bfd_arch_aarch64     : ARM AArch64

## Pull source code and compile with a specific Binutils

* First we have to download and install Binutils with the required
architectures (see supported architectures section).
* Then grab the latest PyBFD version and compile/link against it.

```
    $ git clone https://github.com/Groundworkstech/pybfd.git
    $ cd pybfd
    $ python ./setup.py install --with-static-binutils=/path/to/specific/binutils

    <... some output removed ...>

    [+] pybfd 0.1.0 / Supported architectures:
        bfd_arch_m68k        : Motorola 68xxx
        bfd_arch_vax         : DEC Vax
        bfd_arch_i960        : Intel 960
        bfd_arch_or32        : OpenRISC 32
        bfd_arch_sparc       : SPARC
        bfd_arch_spu         : PowerPC SPU
        bfd_arch_mips        : MIPS Rxxxx
        bfd_arch_i386        : Intel 386
        bfd_arch_l1om        : Intel L1OM
        bfd_arch_k1om        : Intel K1OM
        bfd_arch_i860        : Intel 860
        bfd_arch_i370        : IBM 360/370 Mainframes
        bfd_arch_m88k        : Motorola 88xxx
        bfd_arch_h8300       : Renesas H8/300 (formerly Hitachi H8/300)
        bfd_arch_pdp11       : DEC PDP-11
        bfd_arch_powerpc     : PowerPC
        bfd_arch_rs6000      : IBM RS/6000
        bfd_arch_hppa        : HP PA RISC
        bfd_arch_d10v        : Mitsubishi D10V
        bfd_arch_d30v        : Mitsubishi D30V
        bfd_arch_dlx         : DLX
        bfd_arch_m68hc11     : Motorola 68HC11
        bfd_arch_z8k         : Zilog Z8000
        bfd_arch_h8500       : Renesas H8/500 (formerly Hitachi H8/500)
        bfd_arch_sh          : Renesas / SuperH SH (formerly Hitachi SH)
        bfd_arch_alpha       : Dec Alpha
        bfd_arch_arm         : Advanced Risc Machines ARM.
        bfd_arch_ns32k       : National Semiconductors ns32000
        bfd_arch_w65         : WDC 65816
        bfd_arch_tic30       : Texas Instruments TMS320C30
        bfd_arch_tic4x       : Texas Instruments TMS320C3X/4X
        bfd_arch_tic54x      : Texas Instruments TMS320C54X
        bfd_arch_tic6x       : Texas Instruments TMS320C6X
        bfd_arch_tic80       : TI TMS320c80 (MVP)
        bfd_arch_m32c        : Renesas M16C/M32C.
        bfd_arch_m32r        : Renesas M32R (formerly Mitsubishi M32R/D)
        bfd_arch_mn10200     : Matsushita MN10200
        bfd_arch_mn10300     : Matsushita MN10300
        bfd_arch_fr30        : Fujitsu FR30
        bfd_arch_frv         : Fujitsu FRV
        bfd_arch_moxie       : The moxie processor
        bfd_arch_mcore       : Motorola MCore
        bfd_arch_mep         : Toshiba Media Embedded Processor (MEP)
        bfd_arch_ia64        : HP/Intel ia64
        bfd_arch_iq2000      : Vitesse IQ2000.
        bfd_arch_mt          : Morpho Technologies MT
        bfd_arch_pj          : Pico Java architecture
        bfd_arch_avr         : Atmel AVR microcontrollers.
        bfd_arch_bfin        : ADI Blackfin
        bfd_arch_cr16        : National Semiconductor CompactRISC (ie CR16).
        bfd_arch_cr16c       : National Semiconductor CompactRISC.
        bfd_arch_crx         : National Semiconductor CRX.
        bfd_arch_rx          : Renesas RX.
        bfd_arch_s390        : IBM s390
        bfd_arch_score       : Sunplus score
        bfd_arch_openrisc    : OpenRISC
        bfd_arch_mmix        : Donald Knuth educational processor.
        bfd_arch_xstormy16   : XStormy16
        bfd_arch_msp430      : Texas Instruments MSP430 architecture.
        bfd_arch_xc16x       : Infineon XC16X Series.
        bfd_arch_xtensa      : Tensilica Xtensa cores.
        bfd_arch_z80         : Zilog Z80
        bfd_arch_lm32        : Lattice Mico32
        bfd_arch_microblaze  : Xilinx MicroBlaze.
        bfd_arch_tilepro     : Tilera TILEPro
        bfd_arch_tilegx      : Tilera TILE-Gx
        bfd_arch_aarch64     : ARM AArch64
        bfd_arch_rl78        : RL78
```


The *--with-static-binutils* command line parameter allows the installer script 
to use a binutils installation different from the one installed on the system.
If the *-with-static-binutils* parameter is not specified then the installer 
script will lookup the system Binutils and detect its supported architectures and 
the resulting PyBFD installation will be the exact same as the one performed 
using *easy_install*.

## Sample python scripts

There are a couple of sample scripts included in the PyBFD package including a
partial (but completely useful) reimplementation of objdump in Python using
PyBFD called **objdump.py**.

A basic sample code is located in *bfd.py*, *opcodes.py* and a more complete
usage is shown in *objdump.py*.

## Basic usage example

Below is the code located at the end of *bfd.py* script:


```python
    #!/usr/bin/env python

    # Import the disassembly library (libopcodes)
    from pybfd.opcodes import Opcodes, OpcodesException
    from pybfd.bfd import Bfd, BfdException

    from sys import argv
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

            # The bfd.close() is executed below in the finally clause.
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

```

