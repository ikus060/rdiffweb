# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2021 rdiffweb contributors
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

The tool uses `babel<http://babel.edgewall.org>`_ for localization and
handling translations. Within your Python code you can use four functions
defined in this module and the loaded locale provided as
`cherrypy.response.i18n.locale`.

Example::

    from i18n_tool import ugettext as _, ungettext

    class MyController(object):
        @cherrypy.expose
        def index(self):
            loc = cherrypy.response.i18n.locale
            s1 = _(u'Translateable string')
            s2 = ungettext(u'There is one string.',
                           u'There are more strings.', 2)
            return u'<br />'.join([s1, s2, loc.display_name])

If you have code (e.g. database models) that is executed before the response
object is available, use the *_lazy functions to mark the strings
translateable. They will be translated later on, when the text is used (and
hopefully the response object is available then).

Example::

    from i18n_tool import ugettext_lazy

    class Model:
        def __init__(self):
            name = ugettext_lazy(u'Name of the model')

For your templates read the documentation of your template engine how to
integrate babel with it. I think `Genshi<http://genshi.edgewall.org>`_ and
`Jinja 2<http://jinja.pocoo.org`_ support it out of the box.


Settings for the CherryPy configuration::

    [/]
    tools.I18nTool.on = True
    tools.I18nTool.default = Your language with territory (e.g. 'en_US')
    tools.I18nTool.mo_dir = Directory holding the locale directories
    tools.I18nTool.domain = Your gettext domain (e.g. application name)

The mo_dir must contain subdirectories named with the language prefix
for all translations, containing a LC_MESSAGES dir with the compiled
catalog file in it.

Example::

    [/]
    tools.I18nTool.on = True
    tools.I18nTool.default = 'en_US'
    tools.I18nTool.mo_dir = '/home/user/web/myapp/i18n'
    tools.I18nTool.domain = 'myapp'

    Now the tool will look for a file called myapp.mo in
    /home/user/web/myapp/i18n/en/LC_MESSACES/
    or generic: <mo_dir>/<language>/LC_MESSAGES/<domain>.mo

That's it.

:License: BSD
:Author: Thorsten Weimann <thorsten.weimann (at) gmx (dot) net>
:Date: 2010-02-08
"""

from collections import namedtuple

import cherrypy
from babel.core import Locale, UnknownLocaleError
from babel.support import LazyProxy, NullTranslations, Translations

Lang = namedtuple('Lang', 'locale trans')

# Cache for Translations and Locale objects
_languages = {}


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


def gettext_lazy(message):
    """Like ugettext, but lazy.

    :returns: A proxy for the translation object.
    :rtype: LazyProxy
    """

    def get_translation():
        if not hasattr(cherrypy.response, "i18n"):
            return message
        return cherrypy.response.i18n.trans.ugettext(message)

    return LazyProxy(get_translation, enable_cache=False)


def _search_translation(preferred_langs, dirname, domain):
    """
    Loads the first existing translations for known locale and saves the
    `Lang` object in a global cache for faster lookup on the next request.

    :parameters:
        langs : List
            List of languages as returned by `parse_accept_language_header`.
        dirname : String
            Directory of the translations (`tools.I18nTool.mo_dir`).
            Might be a list of directories.
        domain : String
            Gettext domain of the catalog (`tools.I18nTool.domain`).

    :returns: Lang object with two attributes (Lang.trans = the translations
              object, Lang.locale = the corresponding Locale object).
    :rtype: Lang
    :raises: ImproperlyConfigured if no locale where known.
    """
    if not isinstance(dirname, (list, tuple)):
        dirname = [dirname]
    locale = None
    trans = None
    for lang in preferred_langs:
        try:
            locale = Locale.parse(lang)
            if (domain, lang) in _languages:
                return _languages[(domain, lang)]
            # Get all translation from all directories.
            trans = None
            for d in dirname:
                t = Translations.load(d, lang, domain)
                if not isinstance(t, Translations):
                    continue
                if trans:
                    trans.add_fallback(t)
                else:
                    trans = t
        except (ValueError, UnknownLocaleError):
            continue
        # If the translation was found, exit loop
        if isinstance(trans, Translations):
            break
    if locale is None:
        raise ImproperlyConfigured('Default locale not known.')
    _languages[(domain, lang)] = res = Lang(locale, trans or NullTranslations())
    return res


def _get_i18n(mo_dir, default, domain):
    """Main function which will be invoked during the request by `I18nTool`.
    If the SessionTool is on and has a lang key, this language get the
    highest priority. Default language get the lowest priority.
    The `Lang` object will be saved as `cherrypy.response.i18n` and the
    language string will also saved as `cherrypy.session['_lang_']` (if
    SessionTool is on).

    :parameters:
        mo_dir : String
            `tools.I18nTool.mo_dir`
        default : String
            `tools.I18nTool.default`
        domain : String
            `tools.I18nTool.domain`
    """
    # Get prefered languages from the HTTP Request header.
    preferred_langs = [x.value.replace('-', '_') for x in cherrypy.request.headers.elements('Accept-Language')]

    sessions_on = cherrypy.request.config.get('tools.sessions.on', False)

    # If session is enabled, but the request doesn't contains `Accept-Language`,
    # reload the language from session data.
    if sessions_on and not preferred_langs and cherrypy.session.get('_lang_', ''):
        preferred_langs.insert(0, cherrypy.session.get('_lang_', '__'))

    # Last, we append the default locale in the lookup list.
    preferred_langs.append(default)

    # Search for a translation object.
    loc = cherrypy.response.i18n = _search_translation(preferred_langs, mo_dir, domain)

    # If session is enabled, keep current locale in session data to be
    # reloaded the next time.
    if sessions_on:
        cherrypy.session['_lang_'] = str(loc.locale)  # @UndefinedVariable


def _set_content_language():
    """
    Sets the Content-Language response header (if not already set) to the
    language of `cherrypy.response.i18n.locale`.
    """
    if hasattr(cherrypy.response, 'i18n') and 'Content-Language' not in cherrypy.response.headers:
        cherrypy.response.headers['Content-Language'] = str(cherrypy.response.i18n.locale)


class I18nTool(cherrypy.Tool):
    """Tool to integrate babel translations in CherryPy."""

    def __init__(self):
        self._name = 'i18n'
        self._point = 'before_handler'
        self.callable = _get_i18n
        # Make sure, session tool (priority 50) is loaded before
        self._priority = 60

    def _setup(self):
        c = cherrypy.request.config
        if c.get('tools.staticdir.on', False) or c.get('tools.staticfile.on', False):
            return
        cherrypy.Tool._setup(self)
        cherrypy.request.hooks.attach('before_finalize', _set_content_language)


cherrypy.tools.i18n = I18nTool()
