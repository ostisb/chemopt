# -*- coding: utf-8 -*-
try:
    import configparser
except ImportError:
    # Due to PY27 compatibility
    import ConfigParser as configparser
import os
from warnings import warn

from chemopt.utilities._decorators import Substitution

values = {}
values['basis'] = ['STO-3G', '3-21G', '6-31G', '6-31G(d)', '6-31G(d,p)',
                   '6-31+G(d)', '6-311G(d)', 'cc-pVDZ', 'cc-pVTZ',
                   'AUG-cc-pVDZ', 'AUG-cc-pVTZ']
values['hamiltonian'] = ['RHF', 'MP2', 'B3LYP', 'CCSD', 'CCSD(T)']
values['calculation_type'] = [
    'Single Point', 'Equilibrium Geometry', 'Frequencies']
values['backend'] = {'molpro'}

fixed_defaults = {}
fixed_defaults['charge'] = 0
fixed_defaults['multiplicity'] = 1
fixed_defaults['calculation_type'] = 'Single Point'
fixed_defaults['forces'] = False
fixed_defaults['wfn_symmetry'] = 1
fixed_defaults['title'] = ''


def _give_default_file_path():
    HOME = os.path.expanduser('~')
    filepath = os.path.join(HOME, '.chemoptrc')
    return filepath


def provide_defaults():
    settings = {}
    settings['defaults'] = {}
    settings['defaults']['backend'] = 'molpro'
    settings['defaults']['molpro_exe'] = 'molpro'
    return settings


def write_configuration_file(filepath=_give_default_file_path(),
                             overwrite=False):
    """Create a configuration file.

    Writes the current state of defaults into a configuration file.

    .. note:: Since a file is permamently written, this function
        is strictly speaking not sideeffect free.

    Args:
        filepath (str): Where to write the file.
            The default is under both UNIX and Windows ``~/.chemoptrc``.
        overwrite (bool):

    Returns:
        None:
    """
    config = configparser.ConfigParser()
    config.read_dict(settings)

    if os.path.isfile(filepath) and not overwrite:
        try:
            raise FileExistsError
        except NameError:  # because of python2
            warn('File exists already and overwrite is False (default).')
    else:
        with open(filepath, 'w') as configfile:
            config.write(configfile)


def read_configuration_file(settings, filepath=_give_default_file_path()):
    """Read the configuration file.

    .. note:: This function changes ``cc.defaults`` inplace and is
        therefore not sideeffect free.

    Args:
        filepath (str): Where to read the file.
            The default is under both UNIX and Windows ``~/.chemoptrc``.

    Returns:
        None:
    """
    config = configparser.ConfigParser()
    config.read(filepath)

    def get_correct_type(section, key, config):
        """Gives e.g. the boolean True for the string 'True'"""
        def getstring(section, key, config):
            return config[section][key]

        def getinteger(section, key, config):  # pylint:disable=unused-variable
            return config[section].getint(key)

        def getboolean(section, key, config):
            return config[section].getboolean(key)

        def getfloat(section, key, config):  # pylint:disable=unused-variable
            return config[section].getfloat(key)
        special_actions = {}  # Something different than a string is expected
        try:
            return special_actions[section][key](section, key, config)
        except KeyError:
            return getstring(section, key, config)

    for section in config.sections():
        for k in config[section]:
            settings[section][k] = get_correct_type(section, k, config)
    return settings


settings = provide_defaults()
read_configuration_file(settings)
conf_defaults = settings['defaults']


def get_docstr(key, defaults):
    return "The default is '{}'. The allowed values are {}".format(
        defaults[key], values[key])


docstring = {}

docstring['hamiltonian'] = "The hamiltonian to use for calculating the \
electronic energy. The allowed values are {}.\n".format(values['hamiltonian'])

docstring['basis'] = "The basis set to use for calculating \
the electronic energy. The allowed values are {}.\n".format(values['basis'])

docstring['calculation_type'] = get_docstr('calculation_type', fixed_defaults)

docstring['multiplicity'] = "The spin multiplicity. \
The default is {}.\n".format(fixed_defaults['multiplicity'])

docstring['charge'] = "The overall charge of the molecule. \
The default is {}.\n".format(fixed_defaults['charge'])

docstring['forces'] = "Specify if energy gradients should be calculated. \
The default is {}.".format(fixed_defaults['forces'])

docstring['el_calc_input'] = "Specify the input filename for \
electronic calculations. \
If it is None, the filename of the calling python script is used \
(With the suffix ``.inp`` instead of ``.py``). \
The output will be ``os.path.splitext(el_calc_input)[0] + '.out'``.\n"


docstring['backend'] = "Specify which QM program suite shoud be used. \
Allowed values are {}, \
the default is '{}'.\n".format(values['backend'], conf_defaults['backend'])

docstring['molpro_exe'] = "Specify the command to invoke molpro. \
The default is '{}'.\n".format(conf_defaults['molpro_exe'])

docstring['title'] = "The title to be printed in input and output.\n"

docstring['wfn_symmetry'] = "The symmetry of the wavefunction specified \
with the molpro \
`notation <https://www.molpro.net/info/2015.1/doc/manual/node36.html>`_.\n"
substitute_docstr = Substitution(**docstring)
