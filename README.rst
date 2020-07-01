==============
libyang-python
==============

Python CFFI bindings to libyang__.

__ https://github.com/CESNET/libyang/

|pypi-project|__ |python-versions|__ |build-status|__ |license|__

__ https://pypi.org/project/libyang
__ https://github.com/CESNET/libyang-python/actions
__ https://github.com/CESNET/libyang-python/actions
__ https://github.com/CESNET/libyang-python/blob/master/LICENSE

.. |pypi-project| image:: https://img.shields.io/pypi/v/libyang.svg
.. |python-versions| image:: https://img.shields.io/pypi/pyversions/libyang.svg
.. |build-status| image:: https://github.com/CESNET/libyang-python/workflows/CI/badge.svg
.. |license| image:: https://img.shields.io/github/license/CESNET/libyang-python.svg

Installation
============

::

   pip install libyang

This assumes ``libyang.so`` is installed in the system and that ``libyang.h`` is
available in the system include dirs.

You need the following system dependencies installed:

- Python development headers
- GCC
- FFI development headers

On a Debian/Ubuntu system::

   sudo apt-get install python3-dev gcc python3-cffi

Compilation Flags
-----------------

If libyang headers and libraries are installed in a non-standard location, you
can specify them with the ``LIBYANG_HEADERS`` and ``LIBYANG_LIBRARIES``
variables. Additionally, for finer control, you may use ``LIBYANG_EXTRA_CFLAGS``
and ``LIBYANG_EXTRA_LDFLAGS``::

   LIBYANG_HEADERS=/home/build/opt/ly/include \
   LIBYANG_LIBRARIES=/home/build/opt/ly/lib \
   LIBYANG_EXTRA_CFLAGS="-O3" \
   LIBYANG_EXTRA_LDFLAGS="-rpath=/opt/ly/lib" \
          pip install libyang

Examples
========

Schema Introspection
--------------------

.. code-block:: pycon

   >>> import libyang
   >>> ctx = libyang.Context('/usr/local/share/yang/modules')
   >>> module = ctx.load_module('ietf-system')
   >>> print(module)
   module: ietf-system
     +--rw system
     |  +--rw contact?          string
     |  +--rw hostname?         ietf-inet-types:domain-name
     |  +--rw location?         string
     |  +--rw clock
     |  |  +--rw (timezone)?
     |  |     +--:(timezone-utc-offset)
     |  |        +--rw timezone-utc-offset?   int16
     |  +--rw dns-resolver
     |     +--rw search*    ietf-inet-types:domain-name
     |     +--rw server* [name]
     |     |  +--rw name          string
     |     |  +--rw (transport)
     |     |     +--:(udp-and-tcp)
     |     |        +--rw udp-and-tcp
     |     |           +--rw address    ietf-inet-types:ip-address
     |     +--rw options
     |        +--rw timeout?    uint8 <5>
     |        +--rw attempts?   uint8 <2>
     +--ro system-state
        +--ro platform
        |  +--ro os-name?      string
        |  +--ro os-release?   string
        |  +--ro os-version?   string
        |  +--ro machine?      string
        +--ro clock
           +--ro current-datetime?   ietf-yang-types:date-and-time
           +--ro boot-datetime?      ietf-yang-types:date-and-time

     rpcs:
       +---x set-current-datetime
       |  +---- input
       |     +---w current-datetime    ietf-yang-types:date-and-time
       +---x system-restart
       +---x system-shutdown

   >>> xpath = '/ietf-system:system/ietf-system:dns-resolver/ietf-system:server'
   >>> dnsserver = next(ctx.find_path(xpath))
   >>> dnsserver
   <libyang.schema.SList: server [name]>
   >>> print(dnsserver.description())
   List of the DNS servers that the resolver should query.

   When the resolver is invoked by a calling application, it
   sends the query to the first name server in this list.  If
   no response has been received within 'timeout' seconds,
   the resolver continues with the next server in the list.
   If no response is received from any server, the resolver
   continues with the first server again.  When the resolver
   has traversed the list 'attempts' times without receiving
   any response, it gives up and returns an error to the
   calling application.

   Implementations MAY limit the number of entries in this
   list.
   >>> dnsserver.ordered()
   True
   >>> for node in dnsserver:
   ...     print(repr(node))
   ...
   <libyang.schema.SLeaf: name string>
   <libyang.schema.SContainer: udp-and-tcp>
   >>> ctx.destroy()
   >>>

Data Tree
---------

.. code-block:: pycon

   >>> import libyang
   >>> ctx = libyang.Context()
   >>> module = ctx.parse_module_str('''
   ... module example {
   ...   namespace "urn:example";
   ...   prefix "ex";
   ...   container data {
   ...     list interface {
   ...       key name;
   ...       leaf name {
   ...         type string;
   ...       }
   ...       leaf address {
   ...         type string;
   ...       }
   ...     }
   ...     leaf hostname {
   ...       type string;
   ...     }
   ...   }
   ... }
   ... ''')
   >>> print(module.print_mem('tree'))
   module: example
     +--rw data
        +--rw interface* [name]
        |  +--rw name       string
        |  +--rw address?   string
        +--rw hostname?    string
   >>> node = module.parse_data_dict({
   ...     'data': {
   ...         'hostname': 'foobar',
   ...         'interface': [
   ...             {'name': 'eth0', 'address': '1.2.3.4/24'},
   ...             {'name': 'lo', 'address': '127.0.0.1'},
   ...         ],
   ...     },
   ... })
   >>> print(node.print_mem('xml', pretty=True))
   <data xmlns="urn:example">
     <interface>
       <name>eth0</name>
       <address>1.2.3.4/24</address>
     </interface>
     <interface>
       <name>lo</name>
       <address>127.0.0.1</address>
     </interface>
     <hostname>foobar</hostname>
   </data>
   >>> node.print_dict()
   {'data': {'interface': [{'name': 'eth0', 'address': '1.2.3.4/24'}, {'name':
   'lo', 'address': '127.0.0.1'}], 'hostname': 'foobar'}}
   >>> node.free()
   >>> ctx.destroy()
   >>>

See the ``tests`` folder for more examples.
