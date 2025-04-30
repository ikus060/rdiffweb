# rdiffweb, A web interface to rdiff-backup repositories
# Copyright (C) 2012-2025 rdiffweb contributors
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
# along with this program.  If not, see <https://www.gnu.org/licenses/>.

import inspect
import textwrap

import cherrypy

from rdiffweb.controller import Controller


@cherrypy.expose
class OpenAPI(Controller):
    """
    Return a Json listing all the available routes as OpenAPI format.
    """

    def _create_parameters(self, node, cp_config):
        """
        Build list of parameters based on function signature.
        """
        if not callable(node):
            return []

        is_poppath = cp_config.get('tools.poppath.on', False)

        # Get list of parameters from method signature

        params = inspect.signature(node).parameters
        if not params:
            return []

        parameters = []
        for name, param in params.items():
            if name in ['args', 'kwargs']:
                continue
            param_object = {
                'name': name,
                # If poppath is enabled, 'path' parameters should be in path
                'in': 'path' if is_poppath and name == 'path' else 'query',
                'schema': {'type': 'string'},
            }
            if param.default == inspect.Signature.empty:
                # If no default value. We assumed it to be a vpath.
                param_object['required'] = True
                param_object['in'] = 'path'
            elif is_poppath and name == 'path':
                # If poppath is enabled, 'path' parameters is required
                param_object['required'] = True
            else:
                param_object['schema']['default'] = str(param.default)
            parameters.append(param_object)
        return parameters

    def _create_method_object(self, node, cp_config, method):
        # Get Summary and description
        description = textwrap.dedent(node.__doc__ or "No description available").strip()
        summary = description.split('\n')[0]

        # Define default content-type as HTML
        content_type = "text/html"

        # If static, default to application/octet-stream
        is_staticfile = cp_config.get('tools.staticfile.on', False)
        if is_staticfile:
            content_type = 'application/octet-stream'

        # Get content type from headers.
        headers_on = cp_config.get('tools.response_headers.on', False)
        if headers_on:
            headers = cp_config.get('tools.response_headers.headers', [])
            headers = dict(headers)
            content_type = headers.get('Content-Type', content_type)

        # If json out, define content-type as json
        is_json_out = cp_config.get('tools.json_out.on', False)
        if is_json_out:
            content_type = 'application/json'

        is_json_in = cp_config.get('tools.json_in.on', False)

        # Get allowed method from allow tools
        method_object = {
            "summary": summary,
            "description": description,
            "responses": {"200": {"description": "OK", "content": {content_type: {}}}},
        }

        # Define method parameters
        method_object['parameters'] = self._create_parameters(node, cp_config)

        # Replace parameters and response if static dir
        is_staticdir = cp_config.get('tools.staticdir.on', False)
        if method == 'get' and is_staticdir:
            method_object['parameters'] = [
                {
                    'name': 'filename',
                    'in': 'path',
                    'required': True,
                    'schema': {'type': 'string'},
                }
            ]
            method_object['responses']["404"] = {'description': 'File not found'}

        # Define a request body if json_in is enabled
        if method == 'post' and is_json_in:
            method_object['requestBody'] = {'required': True, 'content': {'application/json': {}}}

        return method_object

    def _create_path_object_api(self, path, node, cp_config):

        # For RESTapi merge all function method into a single path_object
        for method in ['get', 'delete', 'post', 'put', 'list']:
            func = getattr(node, method, False)
            if func and callable(func):
                # Build co_config for this node
                nodeconf = dict(cp_config)
                nodeconf.update(getattr(func, '_cp_config', {}))
                # Build Path object from the method's function
                method_object = self._create_method_object(func, nodeconf, method=method)

                # Handle required vpath.
                if method_object['parameters'] and method_object['parameters'][0]['in'] == 'path':
                    vpath = method_object['parameters'][0]['name']
                    yield '%s/{%s}' % (path.rstrip('/'), vpath), method, method_object
                else:
                    yield path, 'get' if method == 'list' else method, method_object

    def _create_path_object(self, path, node, cp_config):
        # Clean-up the path
        if path.endswith('/index'):
            # Strip `index`
            path = path[:-5]
        elif path.endswith('/default'):
            # Strip `/default`
            path = path[:-8]
        elif path.endswith('_json'):
            # Replace _json by '.json'
            path = path[:-5] + '.json'

        methods = cp_config.get('tools.allow.methods', [])
        for method in methods:
            method = method.lower()
            method_object = self._create_method_object(node, cp_config, method=method)

            # Handle required vpath.
            if method_object['parameters'] and method_object['parameters'][0]['in'] == 'path':
                vpath = method_object['parameters'][0]['name']
                yield '%s/{%s}' % (path.rstrip('/'), vpath), method, method_object
            else:
                yield path, method, method_object

    def _walk_exposed_nodes(self, root_node):
        """
        Walk the object tree to find all @cherrypy.expose function
        """
        config = dict(cherrypy.config)
        config.update(root_node._cp_config)
        stack = [(root_node, "", config)]

        visited = set()
        routes = []
        while stack:
            node, base_url, cp_config = stack.pop()

            if id(node) in visited:
                continue
            visited.add(id(node))

            for attr_name in dir(node):
                if attr_name.startswith("_") or attr_name == 'app':
                    # Ignore special members
                    continue

                child_node = getattr(node, attr_name)

                # Ignore invalid nodes
                if isinstance(child_node, (str, int, float, bool, list, tuple, dict, set, type(None))):
                    continue

                path = f"{base_url}/{attr_name}".replace("//", "/")

                # Build config for the node
                child_cp_config = dict(cp_config)
                child_cp_config.update(getattr(child_node, '_cp_config', {}))

                # Add node to the list of paths if exposed
                if getattr(child_node, 'exposed', False):
                    routes.append((path, child_node, child_cp_config))

                # Add sub-node to stack for further processing
                stack.append((child_node, path, child_cp_config))

        return routes

    def _generate_spec(self, root_node):
        paths = {}
        # Collect all exposed node
        sorted_nodes = sorted(list(self._walk_exposed_nodes(root_node)))
        # Assemble all the nodes
        for path, node, config in sorted_nodes:
            # Check if RESTapi
            generator = self._create_path_object_api if path.startswith('/api') else self._create_path_object
            for path, method, data in generator(path, node, config):
                paths.setdefault(path, {}).setdefault(method, {}).update(data)

        return {
            "openapi": "3.0.0",
            "info": {
                "title": self._footername,
                "description": "Auto-generated OpenAPI documentation",
                "version": self.app.version,
            },
            "servers": [
                {
                    "url": cherrypy.url('/'),
                }
            ],
            "paths": paths,
        }

    def get(self):
        """Generate OpenAPI JSON for a given CherryPy root application."""
        root = cherrypy.tree.apps[""].root
        return self._generate_spec(root)


if __name__ == "__main__":
    import json
    import sys

    from rdiffweb.core.config import parse_args
    from rdiffweb.rdw_app import RdiffwebApp

    cfg = parse_args(args=['--database-uri', 'sqlite://'])
    app = cherrypy.request.app = RdiffwebApp(cfg)

    api_spec = OpenAPI()._generate_spec(app.root)
    if len(sys.argv) >= 2:
        fn = sys.argv[1]
        with open(fn, 'w') as fp:
            json.dump(api_spec, fp)
    else:
        print(json.dumps(api_spec))
