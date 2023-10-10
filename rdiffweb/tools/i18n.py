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

This tool provides locales and loads translations in the following order:

1. `with i18n.preferred_lang()`
2. `tools.i18n.func` callback function (optional)
3. HTTP Accept-Language headers
4. `tools.i18n.default` value

The tool uses `babel` <http://babel.edgewall.org> for localization and
handling translations. Within your Python code you can use four functions
defined in this module and the loaded locale provided as `i18n.get_translation()`

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
import pytz
from babel import dates
from babel.core import Locale, get_global
from babel.support import LazyProxy, NullTranslations, Translations

# Store current translation and preferred_lang
_current = threading.local()


@contextmanager
def preferred_lang(lang):
    """
    Re-define the preferred language to be used for translation within a given context.

    with i18n.preferred_lang('fr'):
        i18n.gettext('some string')
    """
    assert lang is None or isinstance(lang, str)
    prev_lang = getattr(_current, 'preferred_lang', [])
    prev_trans = getattr(_current, 'translation', None)
    try:
        # Update prefered lang and clear translation.
        _current.preferred_lang = [lang] + prev_lang
        _current.translation = None
        yield
    finally:
        # Restore previous value
        _current.preferred_lang = prev_lang
        _current.translation = prev_trans


@contextmanager
def preferred_timezone(timezone):
    """
    Re-define the preferred timezone to be used for date format within a given context.

    with i18n.preferred_lang('America/Montreal'):
        i18n.format_datetime(...)
    """
    assert timezone is None or isinstance(timezone, str)
    prev_timezone = getattr(_current, 'preferred_timezone', [])
    prev_tzinfo = getattr(_current, 'tzinfo', None)
    try:
        # Update prefered lang and clear translation.
        _current.preferred_timezone = [timezone] + prev_timezone
        _current.tzinfo = None
        yield
    finally:
        # Restore previous value
        _current.preferred_timezone = prev_timezone
        _current.tzinfo = prev_tzinfo


def _search_translation(langs, dirname, domain):
    """
    Loads the first existing translations for known locale.

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
    if not isinstance(langs, list):
        langs = [langs]
    t = Translations.load(dirname, langs, domain)
    # Ignore null translation
    if t.__class__ is NullTranslations:
        return None
    # Get Locale from file name
    lang = t.files[0].split('/')[-3]
    t.locale = Locale.parse(lang)
    return t


def get_timezone():
    """
    Get the best timezone information for the current context.
    """
    # When tzinfo is defined, use it
    tzinfo = getattr(_current, 'tzinfo', None)
    if tzinfo is not None:
        return tzinfo
    # Otherwise search for a valid timezone.
    tzinfo = None
    default_timezone = cherrypy.config.get('tools.i18n.default_timezone')
    preferred_timezone = getattr(_current, 'preferred_timezone', [default_timezone])
    for timezone in preferred_timezone:
        try:
            tzinfo = dates.get_timezone(timezone)
            break
        except Exception:
            pass
    # If we can't find a valid timezone using the default and preferred value, fall back to server timezone.
    if tzinfo is None:
        tzinfo = dates.get_timezone(None)
    _current.tzinfo = tzinfo
    return _current.tzinfo


def get_translation():
    """
    Get the best translation for the current context.
    """
    # When translation is defined, use it
    translation = getattr(_current, 'translation', None)
    if translation is not None:
        return translation

    # Otherwise, we need to search the translation.
    # `preferred_lang` should always has a sane value within a cherrypy request because of hooks
    # But we also need to support calls outside cherrypy.
    default = cherrypy.config.get('tools.i18n.default')
    preferred_lang = getattr(_current, 'preferred_lang', [default])
    mo_dir = cherrypy.config.get('tools.i18n.mo_dir')
    domain = cherrypy.config.get('tools.i18n.domain')
    trans = _search_translation(preferred_lang, mo_dir, domain)
    if trans is None:
        trans = NullTranslations()
        trans.locale = Locale('en')
    _current.translation = trans
    return _current.translation


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
        if trans is not None:
            yield trans.locale


def list_available_timezones():
    """
    Return list of available timezone.
    """
    # Babel only support a narrow list of timezone.
    babel_timezone = get_global('zone_territories').keys()
    return [t for t in pytz.all_timezones if t in babel_timezone]


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


gettext = ugettext


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


ngettext = ungettext


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
    The timezone used to format the date is determine with the following priorities:
    * value of tzinfo
    * value of get_timezone()
    * default server time.
    """
    # When formating date or english, let use en_GB as it's to most complete translation.
    return dates.format_datetime(
        datetime=datetime,
        format=format,
        locale=get_translation().locale,
        tzinfo=tzinfo or get_timezone(),
    )


def format_date(datetime=None, format='medium', tzinfo=None):
    """
    Wraper arround babel format_date to provide a default locale.
    """
    return format_datetime(datetime=datetime, format=dates.get_date_format(format), tzinfo=tzinfo)


def get_timezone_name(tzinfo):
    locale = Locale(get_translation().locale.language)
    return dates.get_timezone_name(tzinfo, width='long', locale=locale)


def _load_default(mo_dir, domain, default, **kwargs):
    """
    Initialize the language using the default value from the configuration.
    """
    # Clear current translation
    _current.preferred_lang = [default]
    _current.preferred_timezone = [kwargs['default_timezone']] if 'default_timezone' in kwargs else []
    cherrypy.request._i18n_lang_func = kwargs.get('lang', kwargs.get('func', False))
    cherrypy.request._i18n_tzinfo_func = kwargs.get('tzinfo', False)
    # Clear current translation
    _current.translation = None
    # Clear current timezone
    _current.tzinfo = None


def _load_accept_language(**kwargs):
    """
    When running within a request, load the prefered language from Accept-Language
    """

    if cherrypy.request.headers.elements('Accept-Language'):
        count = 0
        for x in cherrypy.request.headers.elements('Accept-Language'):
            _current.preferred_lang.insert(count, x.value.replace('-', '_'))
            count += 1
    # Clear current translation
    _current.translation = None


def _load_func_language(**kwargs):
    """
    When running a request where a current user is found, load prefered language from user preferences.
    """
    func = getattr(cherrypy.request, '_i18n_lang_func', False)
    if not func:
        return
    try:
        lang = func()
    except Exception:
        return
    if not lang:
        return
    # Add custom lang to preferred_lang
    _current.preferred_lang.insert(0, lang)
    # Clear current translation
    _current.translation = None


def _load_func_tzinfo(**kwargs):
    """
    When running a request, load the prefered timezone information from user preferences.
    """
    func = getattr(cherrypy.request, '_i18n_tzinfo_func', False)
    if not func:
        return
    try:
        tzinfo = func()
    except Exception:
        return
    if not tzinfo:
        return
    # Add custom lang to preferred_lang
    _current.preferred_timezone.insert(0, tzinfo)
    # Clear current translation
    _current.tzinfo = None


def _set_content_language(**kwargs):
    """
    Sets the Content-Language response header (if not already set) to the
    language of `cherrypy.response.i18n.locale`.
    """
    if 'Content-Language' not in cherrypy.response.headers:
        cherrypy.response.headers['Content-Language'] = str(get_translation().locale)


class I18nTool(cherrypy.Tool):
    """Tool to integrate babel translations in CherryPy."""

    def __init__(self):
        super().__init__('before_handler', _load_default, 'i18n')

    def _setup(self):
        cherrypy.Tool._setup(self)
        # Attach additional hooks as different priority to update preferred lang with more accurate preferences.
        cherrypy.request.hooks.attach('before_handler', _load_accept_language, priority=60)
        cherrypy.request.hooks.attach('before_handler', _load_func_language, priority=75)
        cherrypy.request.hooks.attach('before_handler', _load_func_tzinfo, priority=75)
        cherrypy.request.hooks.attach('before_finalize', _set_content_language)


cherrypy.tools.i18n = I18nTool()
