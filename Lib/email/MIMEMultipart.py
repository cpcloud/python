# Copyright (C) 2002-2004 Python Software Foundation
# Author: barry@python.org (Barry Warsaw)

"""Base class for MIME multipart/* type messages.
"""

from email import MIMEBase



class MIMEMultipart(MIMEBase.MIMEBase):
    """Base class for MIME multipart/* type messages."""

    def __init__(self, _subtype='mixed', boundary=None, _subparts=None,
                 **_params):
        """Creates a multipart/* type message.

        By default, creates a multipart/mixed message, with proper
        Content-Type and MIME-Version headers.

        _subtype is the subtype of the multipart content type, defaulting to
        `mixed'.

        boundary is the multipart boundary string.  By default it is
        calculated as needed.

        _subparts is a sequence of initial subparts for the payload.  It
        must be an iterable object, such as a list.  You can always
        attach new subparts to the message by using the attach() method.

        Additional parameters for the Content-Type header are taken from the
        keyword arguments (or passed into the _params argument).
        """
        MIMEBase.MIMEBase.__init__(self, 'multipart', _subtype, **_params)
        if _subparts:
            for p in _subparts:
                self.attach(p)
        if boundary:
            self.set_boundary(boundary)
