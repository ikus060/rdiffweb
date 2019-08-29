# Development

This section provide details for those who want to contributes to the development.

## Translation
Reference http://babel.edgewall.org/wiki/Documentation/setup.html

rdiffweb may be translated using `.po` files. This section describe briefly
how to translate rdiffweb. It's not a complete instruction set, it's merely a reminder.

Extract the strings to be translated.

    ./setup.py extract_messages --output-file rdiffweb/locales/messages.pot

    ./setup.py compile_catalog --directory rdiffweb/locales --locale fr

## Running tests

Rdiffweb is provided with unit tests. To run them, execute a command similar to the following:

    python setup.py. nosetests

## Less & CSS(s)

For deployment reason, we need to pre-compile less file into css file
whenever you change the `.less`.

    python setup.py build_less

## Javascript

Any changes to javascript file need to be manually compiled into .min.js.

    python setup.py minify_js
