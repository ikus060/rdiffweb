# Development

This section provide details for those who want to contributes to the development.

## Translation

Reference <http://babel.edgewall.org/wiki/Documentation/setup.html>

rdiffweb may be translated using `.po` files. This section describe briefly
how to translate rdiffweb. It's not a complete instruction set, it's merely a reminder.

Extract the strings to be translated:

    python setup.py extract_messages

Create a new translation:

    python setup.py init_catalog --local fr

Update an existing translation:

    python setup.py update_catalog --local fr

## Running tests

Rdiffweb is provided with unit tests. To run them, execute a command similar to the following:

    tox -e py3

## Generage favicon.ico with imagemagik

    convert -density 256x256 -background transparent favicon.svg -define icon:auto-resize -colors 256 favicon.ico

## Documentation

To generate documentation run `tox -e doc`.

It generates HTML documentation in folder `dist/html`

Ref.: <https://gist.github.com/johncrossland/9f6f54d559e9136773172aa0a429b46f#pdf-output-from-markdown>
