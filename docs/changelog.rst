==========
Change Log
==========



This document records all notable changes to axiomapy.


1.77
____________

As of this release, the AxiomaSession Object will have a default client id. The AxiomaSession initiation will now only require username, password, and domain. The order of arguments will change from previous releases. Please refer to our examples for more details.

Tag-23.12
____________

As of this release, support for Python 3.12 was introduced. axioma-py is now compatible with Python 3.12.

Tag-24.6
____________

As of this release, Client Event Bus endpoints were introduced in axioma-py. The clients can now access events and market-data via axioma-py. Please refer to the documentation for details related to supported endpoints.

Tag-24.11
____________

As of this release:
    * Users will have access to Admin endpoints to related to External entities.
    * A new utility function was added to map external identity to user login.
    * The users no longer need to pass api_type while initiating the Session object.
Please refer to the documentation for complete endpoints guide.

Tag-24.12
____________

As of this release,
    * axioma-py will support httpx package 0.26.0 and above. Please upgrade your packages in order to use the latest version of the axioma-py.
    * A new endpoint was introduced to rollover positions in bulk.
    * axioma-py now requires Python 3.8 or above.
Please refer to the documentation for more details.