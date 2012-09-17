#!/usr/bin/env python

import os
from waflib import Utils

APPNAME = 'VapourSynth'
VERSION = '1.0' # May want to change this.

TOP = os.curdir
OUT = 'build'

def options(opt):
    opt.load('compiler_cxx')
    opt.load('qt4')

    opt.add_option('--mode', action = 'store', default = 'debug', help = 'the mode to compile in (debug/release)')

def configure(conf):
    def add_options(flags, options):
        for option in options:
            if option not in conf.env[flags]:
                conf.env.append_value(flags, option)

    conf.load('cxx')
    conf.load('compiler_cxx')
    conf.load('qt4')

    # Load Yasm explicitly, then the Nasm module which
    # supports both Nasm and Yasm.
    conf.find_program('yasm', var = 'AS', mandatory = True)
    conf.load('nasm')

    if conf.env.CXX_NAME == 'gcc':
        add_options('CXXFLAGS',
                    ['-Wno-format-security'])

    add_options('ASFLAGS',
                ['-w',
                 '-Worphan-labels',
                 '-Wunrecognized-char'])

    if conf.env.DEST_CPU == 'x86_64':
        add_options('ASFLAGS',
                    ['-DARCH_X86_64=1'])

        if conf.env.DEST_OS == 'darwin':
            fmt = 'macho64'
        elif conf.env.DEST_OS == 'win32':
            fmt = 'win64'
        else:
            fmt = 'elf64'
    else:
        add_options('ASFLAGS',
                    ['-DARCH_X86_64=0'])

        if conf.env.DEST_OS == 'darwin':
            fmt = 'macho32'
        elif conf.env.DEST_OS == 'win32':
            fmt = 'win32'
        else:
            fmt = 'elf32'

    add_options('ASFLAGS',
                ['-f{0}'.format(fmt)])

    if conf.options.mode == 'debug':
        if conf.env.CXX_NAME == 'gcc':
            add_options('CXXFLAGS',
                        ['-DVS_DEBUG',
                         '-g',
                         '-ggdb',
                         '-ftrapv'])

        add_options('ASFLAGS',
                    ['-DVS_DEBUG'])
    elif conf.options.mode == 'release':
        if conf.env.CXX_NAME == 'gcc':
            add_options('CXXFLAGS',
                        ['-O3'])
    else:
        conf.fatal('--mode must be either debug or release.')

def build(bld):
    def search_paths(paths):
        for path in paths:
            yield os.path.join(path, '*.cpp')
            yield os.path.join(path, '*.asm')

    bld(features = 'qt4 cxx asm cxxshlib',
        includes = 'include',
        source = bld.path.ant_glob(search_paths([os.path.join('src', 'core')])),
        use = ['QTCORE'],
        target = 'vapoursynth')
