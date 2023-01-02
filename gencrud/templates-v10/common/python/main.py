#
#   Python backend and Angular frontend code generation by gencrud
#   Copyright (C) 2018-2023 Marc Bertens-Nguyen m.bertens@pe2mbs.nl
#
#   This library is free software; you can redistribute it and/or modify
#   it under the terms of the GNU Library General Public License GPL-2.0-only
#   as published by the Free Software Foundation.
#
#   This library is distributed in the hope that it will be useful, but
#   WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#   Library General Public License for more details.
#
#   You should have received a copy of the GNU Library General Public
#   License GPL-2.0-only along with this library; if not, write to the
#   Free Software Foundation, Inc., 51 Franklin Street, Fifth Floor,
#   Boston, MA 02110-1301 USA
#
import os
import logging
from webapp.common.util import discoverModules
from webapp.common.menu import registerMenu, createMenuHash

__version__     = '1.0.0'
__copyright__   = '(c) Copyright 2018-2023, all rights reserved, GPL2 only'
__author__      = 'Marc Bertens-Nguyen'
__date__        = '2023-01-01'


def registerApi( *args, **kwargs ):
    logger = logging.getLogger( 'core' )
    for module in discoverModules( os.path.dirname( __file__ ) ):
        logger.debug( f'registering module {module}' )
        module.registerApi( *args, **kwargs )
        if hasattr( module, 'registerExtensions' ):
            module.registerExtensions()

        if hasattr( module, 'registerShellContext' ):
            module.registerShellContext()

        if hasattr( module, 'registerCommands' ):
            module.registerCommands()

    return

