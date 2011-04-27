# Copyright 2009-2011 Ram Rachum.
# This program is distributed under the LGPL2.1 license.

'''
This module defines the `` class.

See its documentation for more information.
'''

# blocktodo: Will need thread safety for when another thread is importing at
# the same time. probably make context manager for import lock from imp.

from __future__ import with_statement

import uuid
import __builtin__
import sys
import os.path

from garlicsim.general_misc.third_party import mock as mock_module

from garlicsim.general_misc.temp_value_setters import TempImportHookSetter
from garlicsim.general_misc import address_tools
from garlicsim.general_misc import dict_tools
from garlicsim.general_misc import import_tools

###############################################################################
#                                                                             #
# Importing stuff that would normally be auto-imported later. We're importing
# it now just so it will get into `sys.modules` so we could easily track
# changes to `sys.modules` when we do module-tasting.

import zlib
import encodings.utf_8 as _
try: # Available on Windows only:
    import encodings.mbcs as _
except ImportError:
    pass
#                                                                             #
###############################################################################

_known_false_positive_new_modules = set([
    'garlicsim.general_misc.zlib'
])


class MockImporter(object):
    def __init__(self, original_import, skip_first_import=False):
        self.original_import = original_import        
        self.skip_first_import = skip_first_import
        self.times_called = 0
        
    def __call__(self, name, *args, **kwargs):
        if self.skip_first_import and self.times_called == 0:
            self.times_called = 1
            return self.original_import(name, *args, **kwargs)
        else:
            self.times_called += 1
            return mock_module.Mock(name=name)


def taste_module(path_or_address):
    
    if address_tools.is_address(path_or_address):
        address = path_or_address
        path = import_tools.find_module(path_or_address)
    else:
        # blocktodo: implement address
        path = path_or_address
    
    is_zip_module = '.zip' in path
        
    if not is_zip_module:
        assert os.path.exists(path)
    
    # blocktodo: Make context manager for this
    old_sys_modules = sys.modules.copy()
    
    name = 'tasted_module_%s' % uuid.uuid4() if not is_zip_module else None
    
    mock_importer = MockImporter(
        original_import=__builtin__.__import__,
        skip_first_import = is_zip_module
    )
    
    with TempImportHookSetter(mock_importer):
        
        # Note that `import_by_path` is not affected by the import hook, unless
        # it's a zip import:
        tasted_module = import_tools.import_by_path(path,
                                                    name=name,
                                                    keep_in_sys_modules=False)
        
    new_modules_in_sys_modules = [module_name for module_name in sys.modules if
                                  module_name not in old_sys_modules]
    assert set(new_modules_in_sys_modules).issubset(
        _known_false_positive_new_modules
    )
    
    return tasted_module
        