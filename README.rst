==============
libyang-python
==============

Python CFFI bindings to libyang__.

__ https://github.com/CESNET/libyang/

Installation
============

.. code-block:: bash

   pip install libyang

.. note::

   By default, the C library will be compiled and statically linked with the
   python ``_libyang.so`` extension.

   If you already have ``libyang.so`` installed on your system (with the
   development headers), you can link the python extension with it by exporting
   the ``LIBYANG_INSTALL=system`` variable when running pip:

   .. code-block:: bash

      LIBYANG_INSTALL=system pip install libyang

Supported Python Versions
=========================

This lib *should* work with both python 2 and 3. However only python 3 was
properly tested.

Examples
========

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
   <libyang.schema.List: server [name]>
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
   <libyang.schema.Leaf: name string>
   <libyang.schema.Container: udp-and-tcp>
