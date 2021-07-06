# Development

This section provide details for those who want to contributes to the development.

## Translation
Reference http://babel.edgewall.org/wiki/Documentation/setup.html

rdiffweb may be translated using `.po` files. This section describe briefly
how to translate rdiffweb. It's not a complete instruction set, it's merely a reminder.

Extract the strings to be translated:

    python setup.py extract_messages --output-file rdiffweb/locales/messages.pot

Create a new translation:

    python setup.py init_catalog --local fr
    
Update an existing translation:

    python setup.py update_catalog --local fr

## Running tests

Rdiffweb is provided with unit tests. To run them, execute a command similar to the following:

    python setup.py. nosetests

## Less & CSS(s)

For deployment reason, we need to pre-compile less file into css file
whenever you change the `.less`.

    python setup.py build_less

## Documentation

To generate documentation run `tox -e doc`.

It generates HTML documentation in folder `dist/html`

Ref.: https://gist.github.com/johncrossland/9f6f54d559e9136773172aa0a429b46f#pdf-output-from-markdown
