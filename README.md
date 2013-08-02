pybfd
=====

A Python interface to the GNU Binary File Descriptor (BFD) library.


Usage
=====

```python

    # Import the disassembly library (libopcodes)
    from opcodes import Opcodes, OpcodesException
    from bfd import Bfd, BfdException

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
            opcodes.initialize_smart_disassemble(content, bfd.start_address)

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
