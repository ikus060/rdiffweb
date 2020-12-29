from wtforms.form import Form
import cherrypy

SUBMIT_METHODS = {'POST', 'PUT', 'PATCH', 'DELETE'}


class _ProxyFormdata():
    """
    Custom class to proxy default form data into WTForm from cherrypy variables.
    """

    def __contains__(self, key):
        return key in cherrypy.request.params

    def getlist(self, key):
        # Default to use cherrypy params.
        params = cherrypy.request.params
        if key in params:
            if isinstance(params[key], list):
                return params[key]
            else:
                return [params[key]]
        # Return default empty list.
        return []


_AUTO = _ProxyFormdata()


class CherryForm(Form):
    """
    Custom implementation of WTForm for cherrypy to support kwargs parms.
    
    If ``formdata`` is not specified, this will use cherrypy.request.params
    Explicitly pass ``formdata=None`` to prevent this.
    """

    def __init__(self, formdata=_AUTO, **kwargs):
        super().__init__(formdata=formdata, **kwargs)

    def is_submitted(self):
        """
        Consider the form submitted if there is an active request and
        the method is ``POST``, ``PUT``, ``PATCH``, or ``DELETE``.
        """
        return cherrypy.request.method in SUBMIT_METHODS

    def validate_on_submit(self):
        """
        Call `validate` only if the form is submitted.
        This is a shortcut for ``form.is_submitted() and form.validate()``.
        """
        return self.is_submitted() and self.validate()
