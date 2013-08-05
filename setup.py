#!/usr/bin/env python
# 
# Copyright (c) 2013 Groundworks Technologies
# 
# This code is part PyBFD module (libbfd & libopcodes extension module)
#

import os
import re
import sys
import platform

from traceback import print_exc
from distutils.core import setup, Extension
from distutils.ccompiler import new_compiler
from distutils.command.build_ext import build_ext
from distutils.command.build import build
from distutils.command.install import install

__author__      = "Groundworks Technologies OSS Team"
__contact__     = "oss@groundworkstech.com"
__description__ = "Python BFD extension module (libbfd extension module)"
__company__     = "Groundworks Technologies"
__year__        = "2013"
__version__     = "0.1.1"


MODULE_NAME = "pybfd"
PACKAGE_DIR = "pybfd"

final_supported_archs = list()
debug = False


class BuildCustomCommandLine( build ):
    description = "build"

    user_options = build.user_options
    user_options.append(
        ('with-static-binutils=', None, 'Path to specific bintutils')
    )
    def initialize_options(self):
        self.with_static_binutils = None
        build.initialize_options(self)

class InstallCustomCommandLine( install ):
    description = "install"
    
    user_options = install.user_options
    user_options.append(
        ('with-static-binutils=', None, 'Path to specific bintutils')
    )
    def initialize_options(self):
        self.with_static_binutils = None
        install.initialize_options(self)


class CustomBuildExtension( build_ext ):
    PLATFORMS = {
        "linux2": {
            "libs": [
                "/usr/lib"
            ],
            "includes": [
                "/usr/include"
            ],
            "possible-lib-ext": [
                ".so",
            ]
        },
        "darwin": {
            "libs": [
                "/opt/local/lib", # macports
                "/usr/local/lib", # homebrew
            ],
            "includes": [
                "/opt/local/include", # macports
                "/usr/local/include", # homebrew
            ],
            "possible-lib-ext": [
                ".a", # homebrew
                ".dylib" # macports
            ]
        }
    }

    def __init__(self, *args, **kargs):
        self.libs = None
        self.includes = None 
        self.platform = None
        build_ext.__init__(self, *args, **kargs) 
    def initialize_options(self):
        self.with_static_binutils = None # options..
        build_ext.initialize_options(self)
    def finalize_options(self):
        self.set_undefined_options(
            'build', 
            ('with_static_binutils','with_static_binutils'))
        self.set_undefined_options(
            'install', 
            ('with_static_binutils','with_static_binutils'))
        build_ext.finalize_options(self)

    def check_includes(self, incdir):
        files = ["bfd.h", "dis-asm.h"]
        for filename in files:
            if not os.path.isfile( os.path.join( incdir, filename) ):
                return False
        return True

    def find_binutils_libs(self, libdir, lib_ext):
        """Find Binutils libraries."""
        bfd_expr = re.compile("(lib(?:bfd)|(?:opcodes))(.*?)\%s" % lib_ext )        
        libs = {}
        for root, dirs, files in os.walk(libdir):
            for f in files:
                m = bfd_expr.search(f)
                if m:
                    lib, version = m.groups()
                    if version in libs:
                        libs[ version ].append( f )
                    else:
                        libs[ version ] = [f,]

        # first, search for multiarch files.
        # check if we found more than one version of the multiarch libs.
        multiarch_libs = dict( [(v,_l) for v, _l in libs.items() \
            if v.find("multiarch") != -1 ] )

        if len(multiarch_libs) > 1:
            raise Exception("unable to determine correct binutils version.")
        elif len(multiarch_libs) == 1:
            return multiarch_libs.values()[0]
        # or use the default libs, or .. none 
        return libs.get("",[])

    def prepare_libs_for_cc(self, lib):
        c = self.compiler.compiler_type
        if c == "unix":
            name, ext = os.path.splitext(lib)
            if name.startswith("lib"):
                return lib[3:-len(ext)]
        raise Exception("unable to prepare libraries for %s" % c )

    def generate_source_files( self ):
        """
        Genertate source files to be used during the compile process of the
        extension module.
        This is better than just hardcoding the values on python files because
        header definitions might change along differente Binutils versions and
        we'll be able to catch the changes and keep the correct values.

        """
        from pybfd.gen_supported_disasm import get_supported_architectures, \
                                               get_supported_machines, \
                                               generate_supported_architectures_source, \
                                               generate_supported_disassembler_header, \
                                               gen_supported_archs   

        #
        # Step 1 . Get the patch to libopcodes and nm utility for further
        # usage.
        #
        libs_dir, libs = self.libs

        libopcodes = [os.path.join(libs_dir,lib) \
            for lib in libs if lib.startswith("libopcodes")][0]
        print "[+] Detecting libbfd/libopcodes compiled architectures"

        if self.with_static_binutils: # use the nm from the binutils distro
        
            nms = [
                os.path.join( libs_dir, "..", "bin", "nm" ), # default name of nm
                os.path.join( libs_dir, "..", "bin", "gnm" ) # in OSX brew install binutils's nm as gnm.
            ]
            path_to_nm = None
            for nm_fullpath in nms:
                if os.path.isfile( nm_fullpath ):
                    path_to_nm = nm_fullpath
                    break
            if path_to_nm == None:
                raise Exception("no suitable 'nm' found.")            
        else:
            path_to_nm = "nm"  # Use the nm in the $PATH (TODO: its assume that nm exists)
        #
        # Step 2 .
        #
        # Prepare the libs to be used as option of the compiler.

        path_to_bfd_header = os.path.join( self.includes, "bfd.h")
        supported_machines = get_supported_machines(path_to_bfd_header)

        supported_archs = get_supported_architectures(
            path_to_nm,
            libopcodes, 
            supported_machines,
            self.with_static_binutils == None)

        source_bfd_archs_c = generate_supported_architectures_source(supported_archs, supported_machines)
        print "[+] Generating .C files..."
        gen_file = os.path.join(PACKAGE_DIR, "gen_bfd_archs.c")
        with open(gen_file, "w+") as fd:
            fd.write(source_bfd_archs_c)
        print "[+]   %s" % gen_file

        if self.with_static_binutils:
           link_to_libs = [] # ...
        else:
           link_to_libs = [self.prepare_libs_for_cc(lib) for lib in libs]
      
        c_compiler = new_compiler()        
        objects = c_compiler.compile(
            [os.path.join(PACKAGE_DIR, "gen_bfd_archs.c"), ],
            include_dirs = [self.includes,]
            )
        program = c_compiler.link_executable(
            objects,
            libraries = link_to_libs,
            library_dirs = [libs_dir, ],
            output_progname = "gen_bfd_archs",
            output_dir = PACKAGE_DIR
        )
        gen_tool = os.path.join(PACKAGE_DIR, "gen_bfd_archs")
        gen_file = os.path.join(self.build_lib, PACKAGE_DIR, "bfd_archs.py")
        cmd = "%s > %s" % (
                    gen_tool,
                    gen_file  )

        print "[+] Generating .py files..."
        # generate C dependent definitions
        os.system( cmd )
        # generate python specific data
        with open(gen_file, "a") as f:
            f.write( gen_supported_archs(supported_archs) )

        # Remove unused files.
        for obj in objects:
            os.unlink(obj)
        os.unlink(gen_tool)

        print "[+]   %s" % gen_file

        #
        # Step 3 . Generate header file to be used by the PyBFD extension
        #           modules bfd.c and opcodes.c.
        #
        gen_source = generate_supported_disassembler_header(supported_archs)

        if len(supported_archs) == 0:
            raise Exception("Unable to determine libopcodes' supported " \
                "platforms from '%s'" % libopcodes)

        print "[+] Generating .h files..."
        gen_file = os.path.join(PACKAGE_DIR, "supported_disasm.h")
        with open(gen_file, "w+") as fd:
            fd.write(gen_source)
        print "[+]   %s" % gen_file

        return supported_archs

    def _darwin_current_arch(self):
        """Add Mac OS X support."""
        if sys.platform == "darwin":
            if sys.maxsize > 2 ** 32: # 64bits.
                return platform.mac_ver()[2] # Both Darwin and Python are 64bits.
            else: # Python 32 bits
                return platform.processor() 

    def build_extensions(self):
        """Compile the python extension module for further installation."""
        global final_supported_archs

        ext_extra_objects = []
        ext_libs = []
        ext_libs_dir = []
        ext_includes = []

        self.platform = CustomBuildExtension.PLATFORMS.get( sys.platform, None )
        if self.platform == None:
            raise Exception("unsupported platform: %s" % sys.platform)

        if self.with_static_binutils: # the user has specified a custom binutils distro.
            print "[+] Using specific binutils static distribution"
            print "[+]   %s" % self.with_static_binutils
            self.platform["libs"] = [os.path.join( self.with_static_binutils, "lib"),]
            self.platform["includes"] = [os.path.join( self.with_static_binutils, "include"),]
            self.platform["possible-lib-ext"] = [".a",] # for all unix platforms.

        # check for known includes
        for inc in self.platform["includes"]:
            if self.check_includes(inc):
                self.includes = inc # found a valid include dir with bintuils
                break
        if self.includes == None:
            raise Exception("unable to determine correct include path for bfd.h / dis-asm.h")

        print "[+] Using binutils headers at:"
        print "[+]   %s" % self.includes

        # we'll use this include path for building.
        ext_includes = [self.includes, ]

        # Try to guess libopcodes / libbfd libs.
        libs_dirs = self.platform["libs"]
        print "[+] Searching binutils libraries..."
        for libdir in libs_dirs:
            for possible_lib_ext in self.platform["possible-lib-ext"]:
                libs = self.find_binutils_libs(libdir, possible_lib_ext)
                if libs:
                    self.libs = libdir, libs
                    break

        if self.libs == None:
            raise Exception("unable to find binutils libraries.")

        for lib in self.libs[1]:
            print "[+]   %s" % os.path.join(self.libs[0], lib)
        #
        # check for libopcodes / libbfd
        #
        libraries_path, libs = self.libs
        if not all( [lib.startswith("libopcodes") or lib.startswith("libbfd") for lib in libs] ):
            raise Exception("missing expected library (libopcodes / libbfd) in %s." % libraries_path)

        ext_libs_dir.append( libraries_path )
    
        if self.with_static_binutils:
            # use libs as extra objects...
            ext_extra_objects.extend( [os.path.join(libraries_path,lib) for lib in libs] )
        else:
            ext_libs = [self.prepare_libs_for_cc(lib) for lib in libs]

        # add dependecy to libiberty
        if self.with_static_binutils or sys.platform == "darwin": # in OSX we always needs a static lib-iverty.
            
            lib_liberty_partialpath = [libraries_path,]
            if sys.platform == "darwin": # in osx the lib-iberty is prefixe by "machine" ppc/i386/x86_64
                lib_liberty_partialpath.append( self._darwin_current_arch() )
            lib_liberty_partialpath.append( "libiberty.a" )
            
            lib_liberty_fullpath = os.path.join(*lib_liberty_partialpath ) # merge the prefix and the path
            if not os.path.isfile(lib_liberty_fullpath):
                raise Exception("missing expected library (libiberty) in %s." % libraries_path)
            ext_extra_objects.append(lib_liberty_fullpath)
        
        # generate .py / .h files that depends of libopcodes / libbfd currently selected
        final_supported_archs = self.generate_source_files()
        
        # final hacks for OSX
        if sys.platform == "darwin":
            # fix arch value.
            os.environ["ARCHFLAGS"] = "-arch %s" % self._darwin_current_arch()
            # In OSX we've to link against libintl.
            ext_libs.append("intl")

            # TODO: we have to improve the detection of gettext/libintl in OSX.. this is a quick fix.
            dirs = [
                "/usr/local/opt/gettext/lib", # homebrew
                "/opt/local/lib" # macports
            ]
            for d in dirs:
                if os.path.exists(d):
                    ext_libs_dir.append(d)            

        # fix extensions.    
        for extension in self.extensions:
            extension.include_dirs.extend( ext_includes )
            extension.extra_objects.extend( ext_extra_objects )
            extension.libraries.extend( ext_libs )
            extension.library_dirs.extend( ext_libs_dir )

        return build_ext.build_extensions(self)
         

def main():
    try:
        #
        # Create a setup for the current package in order to allow the user to
        # create different packages (build, source, etc.).
        #
        setup(
            name = MODULE_NAME,
            version = __version__,
            packages = [PACKAGE_DIR],
            description = __description__,
            long_description = __description__,
            url = "https://github.com/Groundworkstech/pybfd",
            ext_modules = [
                # These extensions will be augmented using runtime information
                # in CustomBuildExtension
                Extension(
                    name = "pybfd._bfd",
                    sources = ["pybfd/bfd.c"],
                ),
                Extension(
                    name = "pybfd._opcodes",
                    sources = ["pybfd/opcodes.c"],
               )
            ],
            author = __author__,
            author_email = __contact__,
            license = "GPLv2",
            cmdclass = {
                "install": InstallCustomCommandLine,
                "build": BuildCustomCommandLine,
                "build_ext": CustomBuildExtension
            },
            classifiers = [
                "Development Status :: 4 - Beta",
                "Intended Audience :: Developers",
                "Intended Audience :: Science/Research",
                "Intended Audience :: Other Audience",
                "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
                "Operating System :: MacOS",
                "Operating System :: POSIX",
                "Programming Language :: C",
                "Programming Language :: Assembly",
                "Programming Language :: Python :: 2 :: Only",
                "Topic :: Security",
                "Topic :: Software Development :: Disassemblers",
                "Topic :: Software Development :: Compilers",
                "Topic :: Software Development :: Debuggers",
                "Topic :: Software Development :: Embedded Systems",
                "Topic :: Software Development :: Libraries",
                "Topic :: Utilities"
            ]
            )
        
        global final_supported_archs
        if final_supported_archs:
           print "\n[+] %s %s / Supported architectures:" % (MODULE_NAME, __version__)
           for arch, _, _, comment in final_supported_archs:
               print "\t%-20s : %s" % (arch, comment)

    except Exception, err:
        global debug
        if debug:
            print_exc()
        print "[-] Error : %s" % err

if __name__ == "__main__":
    main()
