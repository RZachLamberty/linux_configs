#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Module: config_sync.py
Author: zlamberty
Created: 2015-12-30

Description:
    Sync local configuration files. Two modes -- copy from local, which will
    pull all local configuration files into the files/ subdirectory, and publish
    to local, which will take the versions found in the repo and publish them to
    the corresponding locations in the local environment

Usage:
<usage>

"""

import argparse
import csv
import os
import shutil


# ----------------------------- #
#   Module Constants            #
# ----------------------------- #

HERE = os.path.dirname(os.path.realpath(__file__))
FCONFIG = os.path.join(HERE, 'config', 'config_files.csv')
LOCALDIR = os.path.expanduser('~')
REPODIR = os.path.join(HERE, 'files')


# ----------------------------- #
#   Main routine                #
# ----------------------------- #

def load_configs(fconfig=FCONFIG):
    with open(fconfig, 'rb') as f:
        return [(_['local'], _['repo']) for _ in csv.DictReader(f)]


CONFIGS = load_configs()


def copy_from_local(configs=CONFIGS, repodir=REPODIR):
    """ configs is a list of (src, relative dst) tuples. For any src path that
        exists on the local machine, copy that file to the repo file directory
        dstdir

    """
    for (src, reldst) in configs:
        src = os.path.expanduser(src)
        if os.access(src, os.R_OK):
            dst = os.path.join(repodir, reldst)

            # make sure path exists before copying
            dd = os.path.dirname(dst)
            if not os.path.isdir(dd):
                os.makedirs(dd)

            # copy
            print 'copying {}... '.format(src),
            shutil.copyfile(src, dst)
            print 'complete.'


def publish_to_local(configs=CONFIGS, repodir=REPODIR):
    """ configs is a list of (local dst, relative repo src) tuples. For any dst
        path that exists on the local machine, copy the corresponding relative
        src file into its place

    """
    for (localdst, relsrc) in configs:
        localdst = os.path.expanduser(localdst)
        reposrc = os.path.join(repodir, relsrc)
        if os.access(localdst, os.R_OK) and os.access(reposrc, os.R_OK):
            # copy
            print 'updating {}... '.format(localdst),
            shutil.copyfile(reposrc, localdst)
            print 'complete.'


# ----------------------------- #
#   Command line                #
# ----------------------------- #

def parse_args():
    parser = argparse.ArgumentParser(""" Given a configuration file such as config/config_files.csv of

            (local config file name, relative path in some (probably local) repo)

        key-value pairs, you can do one of two things:

        1. copy all the current system versions to the local repo
        2. copy all the repo versions to the current system

    """)

    fconfig = "Configuration file (currently only csvs are supported)"
    parser.add_argument("-f", "--fconfig", help=fconfig, default=FCONFIG)

    repodir = "The directory of version-controlled config files"
    parser.add_argument("-r", "--repodir", help=repodir, default=REPODIR)

    cp = 'Copy local configuration files to the repository'
    parser.add_argument('-c', '--copy', help=cp, action='store_true')

    ud = 'Update the local configuration files based on those in the repository'
    parser.add_argument('-u', '--update', help=ud, action='store_true')

    return parser.parse_args()


if __name__ == '__main__':
    args = parse_args()

    if args.cp and args.u:
        raise ValueError("copy OR update, but not both")

    configs = load_configs(args.fconfig)
    repodir = args.repodir

    if args.copy:
        copy_from_local(configs=configs, repodir=repodir)
    elif args.update:
        publish_to_local(configs=configs, repodir=repodir)
    else:
        print "nothing selected!"
