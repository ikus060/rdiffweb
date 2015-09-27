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
"""
This module is used to load the appropriate translation for rdiffweb
application. Current implementation uses the HTTP Accept-Language header
to determine the best translation to be used for the current user. When
not found, this module default to use the `DefaultLanguage`as define by
the configuration of rdiffweb.

This module allows to switch the domain and language of use when processing a
request. This it mostly used to handle plugin translation.

To use the translation module in python code:

    from rdiffweb.i18n import ugettext as _
    ...
    _("my message")

See `rdw_templating`.
"""
from __future__ import unicode_literals

import cherrypy
import copy
import gettext
import logging
import os
import pkg_resources

_logger = logging.getLogger(__name__)

# Cache for Translations and Locale objects
_translations = {}


def ugettext(message):
    """
    Standard translation function. You can use it in all your exposed
    methods and everywhere where the response object is available.

    :parameters:
        message : Unicode
            The message to translate.

    :returns: The translated message.
    :rtype: Unicode
    """
    if not hasattr(cherrypy.response, "i18n"):
        return message
    return cherrypy.response.i18n.ugettext(message)


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
    return cherrypy.response.i18n.ungettext(singular, plural, num)


def _find(domain, localedirs, languages=None):
    """
    Replacement for gettext.find() to search in multiple directory. This
    function return tuples for each mo file found: (lang, translation).
    """
    # Get some reasonable defaults for arguments that were not supplied
    if languages is None:
        languages = []
        for envar in ['LANGUAGE', 'LC_ALL', 'LC_MESSAGES', 'LANG']:
            val = os.environ.get(envar)
            if val:
                languages = val.split(':')
                break
        if 'C' not in languages:
            languages.append('C')
    # now normalize and expand the languages
    nelangs = []
    for lang in languages:
        for nelang in gettext._expand_lang(lang):
            if nelang not in nelangs:
                nelangs.append(nelang)
    # select a language
    result = []
    for localedir in localedirs:
        for lang in nelangs:
            if lang == 'C':
                break
            mofile = os.path.join(localedir, lang, 'LC_MESSAGES', '%s.mo' % domain)
            if os.path.exists(mofile):
                entry = (lang, mofile)
                result.append(entry)
    return result


def _translation(domain, localedirs=None, languages=None):
    """
    Replacement for gettext.translation(). Return the best matching translation
    object for the given `domain`. This method search in localesdirs for a
    translation file (.mo) matching the `languages`.

    Return a null translation object if a translation matching `languages`
    can't be found.
    """

    # Use our internal find function to lookup for translation.
    mofiles = _find(domain, localedirs, languages)
    # If no mo file are found, return a null translation.
    if len(mofiles) <= 0:
        # Return a null translation.
        t = gettext.NullTranslations()
        t._lang = "en"
        return t
    # Lookup the mo files.
    result = None
    for lang, mofile in mofiles:
        # Search the cache to avoid parsing the same file again.
        key = os.path.abspath(mofile)
        t = _translations.get(key)
        if t is None:
            with open(mofile, 'rb') as fp:
                t = _translations.setdefault(key, gettext.GNUTranslations(fp))
        # Copy the translation object to allow setting fallbacks and
        # output charset. All other instance data is shared with the
        # cached object.
        t = copy.copy(t)
        if result is None:
            t._lang = lang
            result = t
        else:
            result.add_fallback(t)
    return result


def load_translation(domain="messages"):
    """
    Return a translation object for the given `domain`. This method is similar
    to gettext.translation. The localdir is determine using package and plugins
    path, the langues to look at is determine using the HTTP Accept-Language.

    The `DefaultLanguage` get the lowest priority.
    """
    # Define default language.
    default = "en_US"
    # Define default directory
    localesdirs = [pkg_resources.resource_filename(# @UndefinedVariable
        __package__, 'locales')]
    if cherrypy.request.app:
        app = cherrypy.request.app.root  # @UndefinedVariable
        # Get default language from app
        config = app.config  # @UndefinedVariable
        default = config.get_config("DefaultLanguage", "en_US")
        # Get more directory from app plugins.
        app.plugins.run(lambda x:
                        x.get_localesdir() is None
                        or localesdirs.append(x.get_localesdir()))

    # Determine the language to be used according to accept-language.
    langs = list()
    for x in cherrypy.request.headers.elements('Accept-Language'):
        x = x.value.replace('-', '_')
        if x not in langs:
            langs.append(x)
    if default is not None and default not in langs:
        langs.append(default)

    # Search for an appropriate translation.
    _logger.log(1, "loading translation [%s] from %s for %s" % (domain, localesdirs, langs))
    return _translation(domain, localesdirs, langs)


def _get_accept_lang():
    """
    Main function which will be invoked during the request by `I18nTool`.
    The translation object will be saved as `cherrypy.response.i18n`.
    """
    # Load the translation for default domain.
    t = load_translation()
    # Store the translation into the cherrypy context.
    cherrypy.response.i18n = t


def _set_content_lang():
    """
    Sets the Content-Language response header (if not already set) to the
    language of `cherrypy.response.i18n.locale`.
    """
    # Just to make it clear, this is to properly reply to the client telling
    # them the language used in the content.
    if ('Content-Language' not in cherrypy.response.headers and
            hasattr(cherrypy.response, 'i18n')):
        cherrypy.response.headers['Content-Language'] = str(
            cherrypy.response.i18n._lang)


class I18nTool(cherrypy.Tool):
    """
    Tool to load the appropriate translation.
    """

    def __init__(self):
        self._name = 'i18n'
        self._point = 'before_handler'
        self.callable = _get_accept_lang
        # Make sure, session tool (priority 50) is loaded before
        self._priority = 100

    def _setup(self):
        c = cherrypy.request.config
        if c.get('tools.staticdir.on', False) or \
           c.get('tools.staticfile.on', False):
            return
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', _set_content_lang)


cherrypy.tools.i18n = I18nTool()
