# Development

This section provide details for those who want to contributes to the development.

## Translation

Reference <http://babel.edgewall.org/wiki/Documentation/setup.html>

rdiffweb may be translated using `.po` files. This section describe briefly
how to translate rdiffweb. It's not a complete instruction set, it's merely a reminder.

Extract the strings to be translated:

    tox -e babel_extract

Create a new translation:

    tox -e babel_init -- --local fr

Update an existing translation:

    tox -e babel_update -- --local fr

Compile all existing translation:

    tox -e babel_compile

## Running tests

Rdiffweb is provided with unit tests. To run them, execute a command similar to the following:

    tox -e py3

## Generage favicon.ico with imagemagik

    convert -density 256x256 -background transparent favicon.svg -define icon:auto-resize -colors 256 favicon.ico

## Documentation

To generate documentation run `tox -e doc`.

It generates HTML documentation in folder `dist/html`

Ref.: <https://gist.github.com/johncrossland/9f6f54d559e9136773172aa0a429b46f#pdf-output-from-markdown>
