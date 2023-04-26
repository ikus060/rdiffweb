# -*- coding: utf-8 -*-
# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2023 rdiffweb contributors
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

This tool provides locales and loads translations in the following order:
- `tools.i18n.default` value
- HTTP Accept-Language headers
- `tools.i18n.preferred_lang` callback function (optional)

The tool uses `babel<http://babel.edgewall.org>`_ for localization and
handling translations. Within your Python code you can use four functions
defined in this module and the loaded locale provided as
`cherrypy.response.i18n.locale`.

Example::

    from i18n import ugettext as _, ungettext

    class MyController(object):
        @cherrypy.expose
        def index(self):
            locale = cherrypy.response.i18n.locale
            s1 = _(u'Translateable string')
            s2 = ungettext(u'There is one string.',
                           u'There are more strings.', 2)
            return u'<br />'.join([s1, s2, locale.display_name])

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


import os
import threading
from contextlib import contextmanager

import cherrypy
from babel import dates
from babel.core import Locale, UnknownLocaleError
from babel.support import LazyProxy, NullTranslations, Translations

# Cache for Translations and Locale objects
_languages = {}

_override = threading.local()


@contextmanager
def preferred_lang(lang):
    """
    Re-define the preferred language to be used for translation within a given context.

    with i18n.preferred_lang('fr'):
        i18n.gettext('some string')
    """
    prev_lang = getattr(_override, 'lang', False)
    try:
        if lang and isinstance(lang, str):
            _override.lang = lang
        yield
    finally:
        _override.lang = prev_lang


def _search_translation(preferred_langs, dirname, domain):
    """
    Loads the first existing translations for known locale and saves the
    `Translations` object in a global cache for faster lookup on the next request.

    :parameters:
        langs : List
            List of languages as returned by `parse_accept_language_header`.
        dirname : String
            Directory of the translations (`tools.I18nTool.mo_dir`).
            Might be a list of directories.
        domain : String
            Gettext domain of the catalog (`tools.I18nTool.domain`).

    :returns: Translations, the corresponding Locale object.
    """
    if not isinstance(dirname, (list, tuple)):
        dirname = [dirname]
    if not isinstance(preferred_langs, list):
        preferred_langs = [preferred_langs]
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
    if not trans:
        trans = NullTranslations()
        locale = Locale.parse('en_US')
    trans.locale = locale
    _languages[(domain, lang)] = res = trans
    return res


def get_translation():
    """
    Get the best translation for the current context.
    """

    #
    # When override is in use. Let use it.
    #
    if getattr(_override, 'lang', False):
        default = cherrypy.config.get('tools.i18n.default')
        mo_dir = cherrypy.config.get('tools.i18n.mo_dir')
        domain = cherrypy.config.get('tools.i18n.domain')
        return _search_translation([_override.lang, default], mo_dir, domain)

    #
    # When we are in a request, determine the best translation using `preferred_lang`.
    # And store the value into the response variable to re-usability.
    #
    if hasattr(cherrypy.response, "i18n") and cherrypy.response.i18n._preferred_lang == cherrypy.request.preferred_lang:
        return cherrypy.response.i18n
    if getattr(cherrypy.request, "preferred_lang", False):
        preferred_lang = cherrypy.request.preferred_lang
        mo_dir = cherrypy.request._i18n_mo_dir
        domain = cherrypy.request._i18n_domain
        cherrypy.response.i18n = _search_translation(preferred_lang, mo_dir, domain)
        cherrypy.response.i18n._preferred_lang = preferred_lang
        return cherrypy.response.i18n

    #
    # When we are not in a request, get language from default server value.
    #
    default = cherrypy.config.get('tools.i18n.default')
    mo_dir = cherrypy.config.get('tools.i18n.mo_dir')
    domain = cherrypy.config.get('tools.i18n.domain')
    return _search_translation(default, mo_dir, domain)


def list_available_locales():
    """
    Return a list of available translations.
    """
    mo_dir = cherrypy.config.get('tools.i18n.mo_dir', False)
    domain = cherrypy.config.get('tools.i18n.domain')
    if not mo_dir:
        return
    for lang in os.listdir(mo_dir):
        trans = _search_translation(lang, mo_dir, domain)
        if type(trans) != NullTranslations:
            yield trans.locale


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
    return get_translation().ugettext(message)


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
    return get_translation().ungettext(singular, plural, num)


def gettext_lazy(message):
    """Like ugettext, but lazy.

    :returns: A proxy for the translation object.
    :rtype: LazyProxy
    """

    def func():
        return get_translation().ugettext(message)

    return LazyProxy(func, enable_cache=False)


def format_datetime(datetime=None, format='medium', tzinfo=None):
    """
    Wraper arround babel format_datetime to provide a default locale.
    """
    return dates.format_datetime(
        datetime=datetime, format=format, locale=get_translation().locale, tzinfo=tzinfo or dates.get_timezone()
    )


def format_date(date=None, format='medium', tzinfo=None):
    """
    Wraper arround babel format_datetime to provide a default locale.
    """
    date = dates._ensure_datetime_tzinfo(dates._get_datetime(date), tzinfo=tzinfo or dates.get_timezone())
    return dates.format_date(date=date, format=format, locale=get_translation().locale)


def _load_default_language(mo_dir, domain, default, **kwargs):
    """
    Initialize the language using the default value from the configuration.
    """
    cherrypy.request.preferred_lang = [default]
    cherrypy.request._i18n_mo_dir = mo_dir
    cherrypy.request._i18n_domain = domain
    cherrypy.request._i18n_func = kwargs.get('func', False)


def _load_accept_language(**kwargs):
    """
    When running within a request, load the prefered language from Accept-Language
    """

    preferred_lang = cherrypy.request.preferred_lang

    if cherrypy.request.headers.elements('Accept-Language'):
        count = 0
        for x in cherrypy.request.headers.elements('Accept-Language'):
            preferred_lang.insert(count, x.value.replace('-', '_'))
            count += 1


def _load_func_language(**kwargs):
    """
    When running a request where a current user is found, load prefered language from user preferance.
    """
    preferred_lang = cherrypy.request.preferred_lang

    func = getattr(cherrypy.request, '_i18n_func', False)
    if func:
        lang = func()
        if lang:
            preferred_lang.insert(0, lang)


def _set_content_language(**kwargs):
    """
    Sets the Content-Language response header (if not already set) to the
    language of `cherrypy.response.i18n.locale`.
    """
    if hasattr(cherrypy.response, 'i18n') and 'Content-Language' not in cherrypy.response.headers:
        cherrypy.response.headers['Content-Language'] = str(cherrypy.response.i18n.locale)


class I18nTool(cherrypy.Tool):
    """Tool to integrate babel translations in CherryPy."""

    def __init__(self):
        super().__init__('before_handler', _load_default_language, 'i18n')

    def _setup(self):
        cherrypy.Tool._setup(self)
        # Attach additional hooks as different priority to update preferred lang with more accurate preferences.
        cherrypy.request.hooks.attach('before_handler', _load_accept_language, priority=60)
        cherrypy.request.hooks.attach('before_handler', _load_func_language, priority=75)
        cherrypy.request.hooks.attach('before_finalize', _set_content_language)


cherrypy.tools.i18n = I18nTool()
