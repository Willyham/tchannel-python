===============
Getting Started
===============

The code matching this guide is `here
<https://github.com/uber/tchannel-python/tree/master/examples/keyvalue>`_.


-------------
Initial Setup
-------------

Create a directory called ``keyvalue`` to work inside of:

.. code-block:: bash

    $ mkdir ~/keyvalue
    $ cd ~/keyvalue

Inside of this directory we're also going to create a ``keyvalue`` module, which
requires an ``__init__.py`` and a ``setup.py`` at the root:

.. code-block:: bash

    $ mkdir keyvalue
    $ touch keyvalue/__init__.py

Setup a `virtual environment <https://virtualenv.pypa.io/en/latest/>`_ for your
service and install the tornado and tchannel:

.. code-block:: bash

    $ virtualenv env
    $ source env/bin/activate
    $ pip install tchannel thrift tornado


---------------------------
Thrift Interface Definition
---------------------------

Create a `Thrift <https://thrift.apache.org/>`_ file under
``thrift/service.thrift`` that defines an interface for your service:

.. code-block:: bash

    $ mkdir thrift
    $ vim thrift/service.thrift
    $ cat thrift/service.thrift


.. code-block:: idl

    exception NotFoundError {
        1: string key,
    }

    service KeyValue {
        string getValue(
            1: string key,
        ) throws (
            1: NotFoundError notFound,
        )

        void setValue(
            1: string key,
            2: string value,
        )
    }

\
This defines a service named ``KeyValue`` with two functions:

``getValue``
    a function which takes one string parameter, and returns a string.
``setValue``
    a void function that takes in two parameters.

Once you have defined your service, generate corresponding Thrift types by
running the following:

.. code-block:: bash

    $ thrift --gen py:new_style,dynamic,slots,utf8strings \
        -out keyvalue thrift/service.thrift

This generates client- and server-side code to interact with your service.

You may want to verify that your thrift code was generated successfully:

.. code-block:: bash

    $ python -m keyvalue.service.KeyValue


-------------
Python Server
-------------

To serve an application we need to instantiate a TChannel instance, which we
will register handlers against. Open up ``keyvalue/server.py`` and write
something like this:

.. code-block:: python

    from __future__ import absolute_import

    from tornado import ioloop
    from tornado import gen

    from service import KeyValue
    from tchannel.tornado import TChannel


    app = TChannel('keyvalue-server')


    @app.register(KeyValue)
    def getValue(request, response):
        pass


    @app.register(KeyValue)
    def setValue(request, response):
        pass


    def run():
        app.listen()


    if __name__ == '__main__':
        run()
        ioloop.IOLoop.current().start()

Here we have created a TChannel instance and registered two no-op handlers with
it. The name of these handlers map directly to the Thrift service we defined
earlier.

**NOTE:** Method handlers do not need to be declared at import-time, since this
can become unwieldy in complex applications. We could also define them like
so:

.. code-block:: python

    def run():
        app = TChannel('keyvalue-server')
        app.register(KeyValue, handler=Get)
        app.register(KeyValue, handler=Set)
        app.listen()
        ioloop.IOLoop.current().start()

A TChannel server only has one requirement: a name for itself. By default an
ephemeral port will be chosen to listen on (although an explicit port can be
provided).

(As your application becomes more complex, you won't want to put everything in
a single file like this. Good code structure is beyond the scope of this
guide.)

Let's make sure this server is in a working state:

.. code-block:: bash

    python keyvalue/server.py
    ^C

The process should hang until you kill it, since it's listening for requests to
handle. You shouldn't get any exceptions.


--------
Handlers
--------

To implement our service's endpoints let's create an in-memory dictionary that
our endpoints will manipulate:

.. code-block:: python

    values = {}


    @app.register(KeyValue)
    def getValue(request, response):
        key = request.args.key
        value = values.get(key)

        if value is None:
            raise KeyValue.NotFoundError(key)

        return value


    @app.register(KeyValue)
    def setValue(request, response):
        key = request.args.key
        value = request.args.value
        values[key] = value

You can see that the return value of ``Get`` will be coerced into the expected
Thrift shape. If we needed to return an additional field, we could accomplish
this by returning a dictionary.

This example service doesn't do any network IO work. If we wanted to take
advantage of Tornado's `asynchronous
<http://tornado.readthedocs.org/en/latest/gen.html>`_ capabilities, we could
define our handlers as coroutines and yield to IO operations:

.. code-block:: python

    @app.register(KeyValue)
    @gen.coroutine
    def setValue(request, response):
        key = request.args.key
        value = request.args.value

        # Simulate some non-blocking IO work.
        yield gen.sleep(1.0)

        values[key] = value

You have probably noticed that all of these handlers are passed ``response`` and
`tchannel` objects, in addition to a ``request``. The ``response`` object is
available for advanced use cases where it doesn't make sense to return one
object as a response body -- for example, long-lived connections that gradually
stream the response back to the caller.

The `tchannel` object contains context about the current request (such as
Zipkin tracing information) and should be used to make requests to other
TChannel services. (Note that this API may change in the future.)

~~~~~~~~~~~~~~~~~
Transport Headers
~~~~~~~~~~~~~~~~~

In addition to the call arguments and headers, the ``request`` object also
provides some additional information about the current request under the
``request.transport`` object:

``transport.flags``
    Request flags used by the protocol for fragmentation and streaming.
``transport.ttl``
    The time (in milliseconds) within which the caller expects a response.
``transport.headers``
    Protocol level headers for the request. For more information on transport
    headers check the
    `Transport Headers <https://github.com/uber/tchannel/blob/master/docs/protocol.md#transport-headers>`_
    section of the protocol document.

---------
Hyperbahn
---------

As mentioned earlier, our service is listening on an ephemeral port, so we are
going to register it with the Hyperbahn routing mesh. Clients will use this
Hyperbahn mesh to determine how to communicate with your service.

Let's change our `run` method to advertise our service with a local Hyperbahn
instance:

.. code-block:: python

    import json
    import os

    @gen.coroutine
    def run():

        app.listen()
        print 'Listening on', app.hostport

        if os.path.exists('/path/to/hyperbahn_hostlist.json'):
            with open('/path/to/hyperbahn_hostlist.json', 'r') as f:
                hyperbahn_hostlist = json.load(f)
            yield app.advertise(routers=hyperbahn_hostlist)

The `advertise` method takes a seed list of Hyperbahn routers and the name of
the service that clients will call into. After advertising, the Hyperbahn will
connect to your process and establish peers for service-to-service
communication.

Consult the Hyperbahn documentation for instructions on how to start a process
locally.


---------
Debugging
---------

Let's spin up the service and make a request to it through Hyperbahn. Python
provides ``tcurl.py`` script, but we need to use the `Node
version <https://github.com/uber/tcurl>`_ for now since it has Thrift support.

.. code-block:: bash

    $ python keyvalue/server.py &
    $ tcurl -H /path/to/hyperbahn_host_list.json -t ~/keyvalue/thrift/service.thrift service KeyValue::setValue -3 '{"key": "hello", "value": "world"}'
    $ tcurl -H /path/to/hyperbahn_host_list.json -t ~/keyvalue/thrift/service.thrift service KeyValue::getValue -3 '{"key": "hello"}'
    $ tcurl -H /path/to/hyperbahn_host_list.json -t ~/keyvalue/thrift/service.thrift service KeyValue::getValue -3 '{"key": "hi"}'

Your service can now be accessed from any language over Hyperbahn + TChannel!


-------------
Python Client
-------------

Let's make a client call from Python in ``keyvalue/client.py``:

.. code-block:: python

    from tornado import gen
    from tornado import ioloop
    from tchannel.thrift import client_for
    from tchannel.tornado import TChannel

    from service import KeyValue

    KeyValueClient = client_for('keyvalue-server', KeyValue)

    @gen.coroutine
    def run():
        app_name = 'keyvalue-client'

        app = TChannel(app_name)
        app.advertise(routers=['127.0.0.1:21300'])

        client = KeyValueClient(app)

        yield client.setValue("foo", "bar")

        response = yield client.getValue("foo")

        print response


    if __name__ == '__main__':
        ioloop.IOLoop.current().run_sync(run)

Similar to the server case, we initialize a TChannel instance and advertise
ourselves on Hyperbahn (to establish how to communicate with `keyval-server`).
After this we create a client class to add TChannel functionality to our
generated Thrift code. We then set and retrieve a value from our server.
