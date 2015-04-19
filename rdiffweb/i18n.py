#!/usr/bin/python
# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2014 rdiffweb contributors
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.


"""Internationalization and Localization for CherryPy

**Tested with CherryPy 3.1.2**

This tool provides locales and loads translations based on the
HTTP-ACCEPT-LANGUAGE header. If no header is send or the given language
is not supported by the application, it falls back to
`tools.I18nTool.default`. Set `default` to the native language used in your
code for strings, so you must not provide a .mo file for it.

The tool uses gettext for localization and handling translations. Within your
Python code you can use four functions defined in this module and the loaded
locale provided as `cherrypy.response.i18n.locale`.

Example::

    from i18n import ugettext as _, ungettext

    class MyController(object):
        @cherrypy.expose
        def index(self):
            loc = cherrypy.response.i18n.locale
            s1 = _(u'Translateable string')
            s2 = ungettext(u'There is one string.',
                           u'There are more strings.', 2)
            return u'<br />'.join([s1, s2, loc.display_name])

Settings for the CherryPy configuration::

    [/]
    tools.i18n.on = True
    tools.i18n.default = Your language with territory (e.g. 'en_US')
    tools.i18n.mo_dir = Directory holding the locale directories
    tools.i18n.domain = Your gettext domain (e.g. application name)

The mo_dir must contain subdirectories named with the language prefix
for all translations, containing a LC_MESSAGES dir with the compiled
catalog file in it.

Example::

    [/]
    tools.i18n.on = True
    tools.i18n.default = 'en_US'
    tools.i18n.mo_dir = '/home/user/web/myapp/i18n'
    tools.i18n.domain = 'myapp'

    Now the tool will look for a file called myapp.mo in
    /home/user/web/myapp/i18n/en/LC_MESSACES/
    or generic: <mo_dir>/<language>/LC_MESSAGES/<domain>.mo

That's it.

:License: BSD
:Author: Thorsten Weimann <thorsten.weimann (at) gmx (dot) net>
:Date: 2010-02-08
"""

from __future__ import unicode_literals

import os
import inspect
import cherrypy
import gettext
import logging

from collections import namedtuple
Lang = namedtuple('Lang', 'locale trans')


# Cache for Translations and Locale objects
_languages = {}


# Define the logger
logger = logging.getLogger(__name__)


# Exception
class ImproperlyConfigured(Exception):
    """Raised if no known locale were found."""


# Public translation functions
def ugettext(message):
    """Standard translation function. You can use it in all your exposed
    methods and everywhere where the response object is available.

    :parameters:
        message : Unicode
            The message to translate.

    :returns: The translated message.
    :rtype: Unicode
    """
    if not hasattr(cherrypy.response, "i18n"):
        return message
    return cherrypy.response.i18n.trans.ugettext(message)


def ungettext(singular, plural, num):
    """Like ugettext, but considers plural forms.

    :parameters:
        singular : Unicode
            The message to translate in singular form.
        plural : Unicode
            The message to translate in plural form.
        num : Integer
            Number to apply the plural formula on. If num is 1 or no
            translation is found, singular is returned.

    :returns: The translated message as singular or plural.
    :rtype: Unicode
    """
    if not hasattr(cherrypy.response, "i18n"):
        return singular
    return cherrypy.response.i18n.trans.ungettext(singular, plural, num)


def load_translation(langs, dirname, domain):
    """Loads the first existing translations for known locale and saves the
    `Lang` object in a global cache for faster lookup on the next request.

    :parameters:
        langs : List
            List of languages as returned by `parse_accept_language_header`.
        dirname : String
            Directory of the translations (`tools.I18nTool.mo_dir`).
        domain : String
            Gettext domain of the catalog (`tools.I18nTool.domain`).

    :returns: Lang object with two attributes (Lang.trans = the translations
              object, Lang.locale = the corresponding Locale object).
    :rtype: Lang
    :raises: ImproperlyConfigured if no locale where known.
    """
    locale = None
    for lang in langs:
        short = lang[:2].lower()
        try:
            locale = lang
            if (domain, short) in _languages:
                return _languages[(domain, short)]
            trans = gettext.translation(domain,
                                        dirname,
                                        languages=[locale],
                                        fallback=True)
        except (ValueError, IOError):
            logger.debug("error loading translation")
            continue
        # If the translation was found, exit loop
        if isinstance(trans, gettext.GNUTranslations):
            break
    if locale is None:
        raise ImproperlyConfigured('Default locale not known.')
    _languages[(domain, short)] = res = Lang(locale, trans)
    return res


def get_lang(default, domain):
    """Main function which will be invoked during the request by `I18nTool`.
    If the SessionTool is on and has a lang key, this language get the
    highest priority. Default language get the lowest priority.
    The `Lang` object will be saved as `cherrypy.response.i18n` and the
    language string will also saved as `cherrypy.session['_lang_']` (if
    SessionTool is on).

    :parameters:
        default : String
            `tools.i18n.default`
        domain : String
            `tools.i18n.domain`
    """
    # Define the locales directory
    mo_dir = os.path.split(inspect.getfile(inspect.currentframe()))[0]
    mo_dir = os.path.realpath(os.path.abspath(mo_dir))
    mo_dir = os.path.join(mo_dir, 'locales/')

    # Determine the language to be used according to accept-language.
    langs = [x.value.replace('-', '_') for x in
             cherrypy.request.headers.elements('Accept-Language')]
    langs.append(default)
    logger.debug("accept-language: %s " % (langs))

    # Search for an appropriate translation.
    loc = load_translation(langs, mo_dir, domain)

    # Store the translation into the cherrypy context.
    cherrypy.response.i18n = loc
    logger.debug("use-language: %s " % str(loc.locale))


def set_lang():
    """
    Sets the Content-Language response header (if not already set) to the
    language of `cherrypy.response.i18n.locale`.
    """
    # Just to make it clear, this is to properly reply to the client telling
    # them the language used in the content.
    if ('Content-Language' not in cherrypy.response.headers and
            hasattr(cherrypy.response, 'i18n')):
        cherrypy.response.headers['Content-Language'] = str(
            cherrypy.response.i18n.locale)


class I18nTool(cherrypy.Tool):
    """Tool to integrate gettext translations in CherryPy."""

    def __init__(self):
        self._name = 'i18n'
        self._point = 'before_handler'
        self.callable = get_lang
        # Make sure, session tool (priority 50) is loaded before
        self._priority = 100

    def _setup(self):
        c = cherrypy.request.config
        if c.get('tools.staticdir.on', False) or \
           c.get('tools.staticfile.on', False):
            return
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', set_lang)


cherrypy.tools.i18n = I18nTool()
