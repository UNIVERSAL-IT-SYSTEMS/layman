#!/usr/bin/python
# -*- coding: utf-8 -*-

"""
 LAYMAN CONFIGURATION

 File:       config.py

             Handles Basic layman configuration

 Copyright:
             (c) 2005 - 2009 Gunnar Wrobel
             (c) 2009        Sebastian Pipping
             (c) 2010 - 2011 Brian Dolbec
             Distributed under the terms of the GNU General Public License v2

 Author(s):
             Gunnar Wrobel <wrobel@gentoo.org>
             Sebastian Pipping <sebastian@pipping.org>
             Brian Dolbec <brian.dolbec@gmail.com>
"""

'''Defines the configuration options.'''

__version__ = "0.2"


import sys
import os
import ConfigParser

from layman.output import Message


def read_layman_config(config=None, defaults=None):
    """reads the config file defined in defaults['config']
    and updates the config

    @param config: ConfigParser.ConfigParser(self.defaults) instance
    @param defaults: dict
    @modifies config['MAIN']['overlays']
    """
    config.read(defaults['config'])
    if config.get('MAIN', 'overlay_defs'):
        try:
            filelist = os.listdir(config.get('MAIN', 'overlay_defs'))
        except OSError:
            return
        filelist = [f for f in filelist if f.endswith('.xml')]
        overlays = set(config.get('MAIN', 'overlays').split('\n'))
        for _file in filelist:
            path = os.path.join(config.get('MAIN', 'overlay_defs'), _file)
            if os.path.isfile(path):
                overlays.update(["file://" + path])
        config.set('MAIN', 'overlays', '\n'.join(overlays))



class BareConfig(object):
    '''Handles the configuration only.'''

    def __init__(self, output=None, stdout=None, stdin=None, stderr=None,
        config=None, read_configfile=False, quiet=False, quietness=4,
        verbose=False, nocolor=False, width=0
        ):
        '''
        Creates a bare config with defaults and a few output options.

        >>> a = BareConfig()
        >>> a['overlays']
        '\\nhttp://www.gentoo.org/proj/en/overlays/repositories.xml'
        >>> sorted(a.keys())
        ['bzr_command', 'cache', 'config', 'cvs_command', 'darcs_command',
        'git_command', 'local_list', 'make_conf', 'mercurial_command',
        'nocheck', 'overlays', 'proxy', 'quietness', 'rsync_command', 'storage',
        'svn_command', 'tar_command', 'umask', 'width', ...]
        '''
        self._defaults = {'config'    : '/etc/layman/layman.cfg',
                    'storage'   : '/var/lib/layman',
                    'cache'     : '%(storage)s/cache',
                    'local_list': '%(storage)s/overlays.xml',
                    'make_conf' : '%(storage)s/make.conf',
                    'nocheck'   : 'yes',
                    'proxy'     : '',
                    'umask'     : '0022',
                    'overlays'  :
                    'http://www.gentoo.org/proj/en/overlays/repositories.xml',
                    'overlay_defs': '/etc/layman/overlays',
                    'bzr_command': '/usr/bin/bzr',
                    'cvs_command': '/usr/bin/cvs',
                    'darcs_command': '/usr/bin/darcs',
                    'git_command': '/usr/bin/git',
                    'g-common_command': '/usr/bin/g-common',
                    'mercurial_command': '/usr/bin/hg',
                    'rsync_command': '/usr/bin/rsync',
                    'svn_command': '/usr/bin/svn',
                    'tar_command': '/bin/tar',
                    'T/F_options': ['nocheck'],
                    'bzr_addopts' : '',
                    'bzr_syncopts' : '',
                    'cvs_addopts' : '',
                    'cvs_syncopts' : '',
                    'darcs_addopts' : '',
                    'darcs_syncopts' : '',
                    'git_addopts' : '',
                    'git_syncopts' : '',
                    'mercurial_addopts' : '',
                    'mercurial_syncopts' : '',
                    'rsync_syncopts' : '',
                    'svn_addopts' : '',
                    'svn_syncopts' : '',
                    'g-common_generateopts' : '',
                    'g-common_syncopts' : '',
                    'bzr_postsync' : '',
                    'cvs_postsync' : '',
                    'darcs_postsync' : '',
                    'git_postsync' : '',
                    'mercurial_postsync' : '',
                    'rsync_postsync' : '',
                    'svn_postsync' : '',
                    'tar_postsync' : '',
                    'g-common_postsync' : '',
                    }
        self._options = {
                    'config': config if config else self._defaults['config'],
                    'stdout': stdout if stdout else sys.stdout,
                    'stdin': stdin if stdin else sys.stdin,
                    'stderr': stderr if stderr else sys.stderr,
                    'output': output if output else Message(),
                    'quietness': 4,
                    'nocolor': False,
                    'width': 0,
                    'verbose': False,
                    'quiet': False,
                    }
        self.config = None
        if read_configfile:
            self.read_config(self.get_defaults())


    def read_config(self, defaults):
            self.config = ConfigParser.ConfigParser(defaults)
            self.config.add_section('MAIN')
            read_layman_config(self.config, defaults)


    def keys(self):
        '''Special handler for the configuration keys.
        '''
        self._options['output'].debug(
            'Retrieving %s options' % self.__class__.__name__, 8)
        keys = [i for i in self._options]
        self._options['output'].debug(
            'Retrieving %s defaults' % self.__class__.__name__, 8)
        keys += [i for i in self._defaults
                 if not i in keys]
        self._options['output'].debug(
            'Retrieving %s done...' % self.__class__.__name__, 8)
        return keys


    def get_defaults(self):
        """returns our defaults dictionary"""
        _defaults = self._defaults.copy()
        _defaults['config'] = self._options['config']
        return _defaults


    def get_option(self, key):
        """returns the current option's value"""
        return self._get_(key)


    def set_option(self, option, value):
        """Sets an option to the value """
        self._options[option] = value
        # handle quietness
        if option == 'quiet':
            if self._options['quiet']:
                self._set_quietness(1)
                self._options['quietness'] = 0
            else:
                self._set_quietness(4)
        if option == 'quietness':
            self._set_quietness(value)

    def _set_quietness(self, value):
            self._options['output'].set_info_level(int(self['quietness']))
            self._options['output'].set_warn_level(int(self['quietness']))

    def __getitem__(self, key):
        return self._get_(key)

    def _get_(self, key):
        self._options['output'].debug(
            'Retrieving %s option: %s' % (self.__class__.__name__, key), 8)
        if key == 'overlays':
            overlays = ''
            if (key in self._options
                and not self._options[key] is None):
                overlays = '\n'.join(self._options[key])
            if self.config and self.config.has_option('MAIN', 'overlays'):
                overlays += '\n' + self.config.get('MAIN', 'overlays')
            if overlays:
                return  overlays
        if (key in self._options
            and not self._options[key] is None):
            return self._options[key]
        if self.config and self.config.has_option('MAIN', key):
            if key in self._defaults['T/F_options']:
                return t_f_check(self.config.get('MAIN', key))
            return self.config.get('MAIN', key)
        self._options['output'].debug('Retrieving BareConfig default', 8)
        if key in self._defaults:
            if '%(storage)s' in self._defaults[key]:
                return self._defaults[key] %{'storage': self._defaults['storage']}
            return self._defaults[key]
        return None

    @staticmethod
    def t_f_check(option):
        """evaluates the option and returns
        True or False
        """
        return option.lower() in ['yes', 'true', 'y', 't']


class OptionConfig(BareConfig):
    """This subclasses BareCongig adding functions to make overriding
    or resetting defaults and/or setting options much easier
    by using dictionaries.
    """

    def __init__(self, options=None, defaults=None):
        """
        @param options: dictionary of {'option': value, ...}
        @rtype OptionConfig class instance.
        """
        BareConfig.__init__(self)

        self.update_defaults(defaults)

        self.update(options)

        return

    def update(self, options):
        """update the options with new values passed in via options

        @param options
        """
        if options is not None:
            keys = sorted(options)
            if 'quiet' in keys:
                self.set_option('quiet', options['quiet'])
                options.pop('quiet')
            if 'quietness' in keys and not options['quiet']:
                self._set_quietness(options['quietness'])
                options.pop('quietness')
            self._options.update(options)
        return

    def update_defaults(self, new_defaults):
        """update the options with new values passed in via options

        @param options
        """
        if new_defaults is not None:
            self._defaults.update(new_defaults)
        return
