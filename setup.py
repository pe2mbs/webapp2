# -*- coding: utf-8 -*-
"""Main webapp application package."""
#
# Main webapp application package
# Copyright (C) 2018-2023 Marc Bertens-Nguyen <m.bertens@pe2mbs.nl>
#
# This library is free software; you can redistribute it and/or modify
# it under the terms of the GNU Library General Public License GPL-2.0-only
# as published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.
#
from setuptools import setup, find_packages
from webapp.version import version, date, author, author_email


setup(
    name            = 'webapp',
    description     = 'Angular web service framework',
    author          = author,
    version         = version,
    author_email    = author_email,
    url             = 'https://github.com/pe2mbs/webapp',
    packages        = find_packages( include = [ 'webapp', 'webapp.*' ] ),
    install_requires= [
        'PyYAML',
        'pyyaml-include',
        'Flask',
        'flask-marshmallow',
        'marshmallow-sqlalchemy',
        'Flask-Bcrypt',
        'Flask-Caching',
        'Flask-Cors',
        'SQLAlchemy',
        'Flask-SQLAlchemy',
        'Flask-JWT-Extended',
        'Flask-Migrate',
        'Flask-MonitoringDashboard',
        'pytz',
        'Mako',
        'python-dateutil',
        'Click',
        'flask-socketio',
        'eventlet',
        'deprecated',
        'MarkupSafe',
        'itsdangerous',
        'pydantic'
    ]
)
