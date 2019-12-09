.. py:currentmodule:: sopel.config.core_section

================================
The [core] configuration section
================================

.. highlight:: ini

A typical configuration file looks like this::

    [core]
    nick = Sopel
    host = chat.freenode.net
    use_ssl = true
    port = 6697
    owner = dgw
    channels =
        "#sopel"

which tells the bot what its name is, who its owner is, which server to
connect to, and which channels to join.

Everything else is pretty much optional.

The :class:`~sopel.config.core_section.CoreSection` class represents the
``[core]`` section. See its documentation for detailed descriptions of each of
its attributes.

This file can be generated with ``sopel configure``.

.. seealso::

    The :doc:`cli` chapter for ``sopel``'s subcommands.


.. contents::
    :local:
    :depth: 2


Identity & Admins
=================

Your bot's identity is configured by the following options:

* :attr:`~CoreSection.nick`: this is your bot's nick, as it will appear to
  other users on the server
* :attr:`~CoreSection.user` (optional): this is your bot's user name, as the
  server will see it
* :attr:`~CoreSection.name` (optional): the name of the bot as it will appear
  to a ``WHOIS <nick>`` request

For example, given the following hostmask ``Sopel!sopelbot@address``, then
``Sopel`` is the value from :attr:`~CoreSection.nick`, and ``sopelbot`` is the
value from :attr:`~CoreSection.user`::

    [core]
    nick = Sopel
    user = sopelbot
    name = Sopel 7.0

In that case, a ``WHOIS Sopel`` request will give ``Sopel 7.0`` for its name.

User Modes
----------

To have Sopel set additional user modes upon connection, use the
:attr:`~CoreSection.modes` setting::

    [core]
    modes = BpR

In this example, upon connection to the IRC server, Sopel will send this::

    MODE Sopel +BpR

Which means: this is a Bot (B), don't show channels it is in (p), and only
registered users (R) can send it messages. The list of supported modes depends
on the IRC server the bot connects to.

.. important::

   The list of available modes depends on the implementation of the IRC server,
   and its configuration.

   For example, the `user modes on freenode`__ is different from the list of
   available `user modes on an UnrealIRCd server`__.

   .. __: https://freenode.net/kb/answer/usermodes
   .. __: https://www.unrealircd.org/docs/User_modes

Owner & Admins
--------------

A Sopel instance must have exactly one owner. This is configured either by
:attr:`~CoreSection.owner_account` if the IRC server supports IRCv3 accounts,
or by :attr:`~CoreSection.owner`. If ``owner_account`` is set, ``owner`` will
be ignored.

The same instance can have multiple admins. Similarly, it can be configured
by :attr:`~CoreSection.admin_accounts` or by :attr:`~CoreSection.admins`. If
``admin_accounts`` is set, ``admins`` will be ignored.

Both ``owner_account`` and ``admin_accounts`` are safer to use than
nick-based matching, but the IRC server must support accounts.
(Most, sadly, do not as of mid-2019.)


IRC Server
==========

To connect to a server, your bot needs these directives:

* :attr:`~CoreSection.host`: the server's hostname. Can be a domain name
  (like ``chat.freenode.net``) or an IP address.
* :attr:`~CoreSection.port`: optional, the port to connect to. Usually 6697 for
  SSL connection and 6667 for unsecure connection, the default value the bot
  will use to connect to the server.
* :attr:`~CoreSection.use_ssl`: connect using SSL (see below)::

    [core]
    host = chat.freenode.net
    port = 6697
    use_ssl = true

You can also configure the host the bot will connect from with
:attr:`~CoreSection.bind_host`.

Ping Timeout
------------

By default, if Sopel doesn't get a PING from the server every 120s, it will
consider that the connection has timed out. This amount of time can be modified
with the :attr:`~CoreSection.timeout` directive.

SSL Connection
--------------

It is possible to connect to an IRC server with an SSL connection. For that,
you need to set :attr:`~CoreSection.use_ssl` to true::

    [core]
    use_ssl = yes
    verify_ssl = yes
    ca_certs = path/to/sopel/ca_certs.pem

In that case:

* default port to connect to IRC will be 6697
* certificate will be verified if :attr:`~CoreSection.verify_ssl` is set to
  true

.. seealso::

   Sopel uses the built-in :func:`ssl.wrap_socket` function to wrap the socket
   used for the IRC connection.

.. note::

   Sopel will try to look at one of these files for the CA certs pem file
   required by :func:`ssl.wrap_socket`:

   * ``/etc/pki/tls/cert.pem``
   * ``/etc/ssl/certs/ca-certificates.crt`` (Debian)
   * ``/etc/ssl/cert.pem`` (FreeBSD base OpenSSL)
   * ``/usr/local/openssl/cert.pem`` (FreeBSD userland OpenSSL)
   * ``/etc/pki/tls/certs/ca-bundle.crt`` (RHEL 6 / Fedora)
   * ``/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem`` (RHEL 7 / CentOS)
   * ``/etc/pki/tls/cacert.pem`` (OpenELEC)
   * ``/etc/ssl/ca-bundle.pem`` (OpenSUSE)

   This is required if :attr:`~CoreSection.verify_ssl` is set to true. It is
   possible to set the file used with :attr:`~CoreSection.ca_certs`. This is
   useful if e.g. Sopel cannot find the CA certs file, or you need Sopel to
   trust a CA not trusted by the system.

Channels
--------

By default, Sopel won't join any channels. The list of channels to
join is configured by :attr:`~CoreSection.channels`::

    [core]
    channels =
        "#sopel"
        "#sopelunkers"

It is possible to slow down the initial joining of channels using
:attr:`~CoreSection.throttle_join`, for example if the IRC network kicks
clients that join too many channels too quickly.

Flood Prevention
----------------

In order to avoid flooding the server, Sopel has a built-in flood prevention
mechanism. It can be controlled with several directives:

* :attr:`~CoreSection.flood_burst_lines`: the number of messages
  that can be sent before triggering the throttle mechanism.
* :attr:`~CoreSection.flood_empty_wait`: time to wait once burst limit has been
  reached before sending a new message.
* :attr:`~CoreSection.flood_refill_rate`: how much time (in seconds) must be
  spent before recovering flood limit.

For example this configuration::

    [core]
    flood_burst_lines = 10
    flood_empty_wait = 0.5
    flood_refill_rate = 2

will allow 10 messages at once before triggering the throttle mechanism, then
it'll wait 0.5s before sending a new message, and refill the burst limit every
2 seconds.

The default configuration works fine with most tested networks, but individual
bots' owners are invited to tweak as necessary to respect their network's flood
policy.

.. versionadded:: 7.0

   Flood prevention has been modified in Sopel 7.0 and these configuration
   options have been added: ``flood_burst_lines``, ``flood_empty_wait``, and
   ``flood_refill_rate``.


Authentication
==============

Sopel provides two ways to authenticate: a simple method, and multi-stage
authentication. If only one authentication method is available, then it's best
to stick to the simple method, using :attr:`~CoreSection.auth_method`.

Simple method
-------------

This is the most common use case: the bot will authenticate itself using one
and only one method, being a server-based or nick-based authentication.

To configure the authentication method, :attr:`~CoreSection.auth_method` must
be configured. For **server-based** methods:

* ``sasl``
* ``server``

And for **nick-based** methods:

* ``nickserv``
* ``authserv``
* ``Q``
* ``userserv``

These additional options can be used to configure the authentication method
and the required credentials:

* :attr:`~CoreSection.auth_username`: account's username, if required
* :attr:`~CoreSection.auth_password`: account's password
* :attr:`~CoreSection.auth_target`: authentication method's target, if required
  by the ``auth_method``:

  * ``sasl``: the SASL mechanism (``PLAIN`` by default)
  * ``nickserv``: the service's nickame to send credentials to
    (``NickServ`` by default)
  * ``userserv``: the service's nickame to send credentials to
    (``UserServ`` by default)

Multi-stage
-------------

In some cases, an IRC bot needs to use both server-based and
nick-based authentication.

* :attr:`~CoreSection.server_auth_method`: defines the server-based
  authentication method to use (``sasl`` or ``server``)
* :attr:`~CoreSection.nick_auth_method`: defines the nick-based authentication
  method to use ( ``nickserv``, ``authserv``, ``Q``, or ``userserv``)

.. important::

   If ``auth_method`` is defined then ``nick_auth_method`` (and its options)
   will be ignored.

.. versionadded:: 7.0

   The multi-stage authentication has been added in Sopel 7.0 with its
   configuration options.

Server-based
............

When :attr:`~CoreSection.server_auth_method` is defined, the settings
used are:

* :attr:`~CoreSection.server_auth_username`: account's username
* :attr:`~CoreSection.server_auth_password`: account's password
* :attr:`~CoreSection.server_auth_sasl_mech`: the SASL mechanism to use
  (defaults to ``PLAIN``)

Nick-based
..........

When :attr:`~CoreSection.nick_auth_method` is defined, the settings
used are:

* :attr:`~CoreSection.nick_auth_username`: account's username; may be
  optional for some authentication methods; defaults to the bot's nick
* :attr:`~CoreSection.nick_auth_password`: account's password
* :attr:`~CoreSection.nick_auth_target`: the target used to send authentication
  credentials; may be optional for some authentication methods; defaults to
  ``NickServ`` for ``nickserv``, and to ``UserServ`` for ``userserv``.


Database
========

Sopel uses SQLAlchemy to connect to and query its database. To configure the
type of database, set :attr:`~CoreSection.db_type` to one of these values:

* ``sqlite`` (default)
* ``mysql``
* ``postgres``
* ``mssql``
* ``oracle``
* ``firebird``
* ``sybase``

SQLite
------

There is only one option for SQLite, :attr:`~CoreSection.db_filename`, which
configures the path to the SQLite database file. Other options are ignored
when ``db_type`` is set to ``sqlite``.

Other Database
--------------

When ``db_type`` is *not* set to ``sqlite``, the following options
are available:

* :attr:`~CoreSection.db_host`
* :attr:`~CoreSection.db_user`
* :attr:`~CoreSection.db_pass`
* :attr:`~CoreSection.db_port` (optional)
* :attr:`~CoreSection.db_name` (optional)
* :attr:`~CoreSection.db_driver` (optional)

Both ``db_port`` and ``db_name`` are optional, depending on your setup and the
type of your database.

In all cases, Sopel uses a database driver specific to each type. This driver
can be configured manually with the ``db_driver`` options. See the SQLAlchemy
documentation for more information about `database drivers`__, and how to
install them.

.. __: https://docs.sqlalchemy.org/en/latest/dialects/

.. versionadded:: 7.0

   Using SQLAlchemy for the database has been added in Sopel 7.0, which
   supports multiple types of databases. The configuration options required for
   these new types have been added at the same time.


Commands & Plugins
==================

Users can interact with Sopel through its commands, from Sopel's core or
from Sopel's plugins. A command is a prefix with a name. The prefix can be
configured with :attr:`~CoreSection.prefix`::

    [core]
    prefix = \.

.. note::

   This directive expects a **regex** pattern, so special regex characters must
   be escaped, as shown in the example above.

Other directives include:

* :attr:`~CoreSection.help_prefix`: the prefix used in help messages
* :attr:`~CoreSection.alias_nicks`: additional names users might call the bot;
  used by nick-based commands
* :attr:`~CoreSection.auto_url_schemes`: URL schemes (like ``http`` or ``ftp``)
  that should trigger the detection of URLs in messages

Plugins
-------

By default, Sopel will load all available plugins. To exclude a plugin, you
can put its name in the :attr:`~CoreSection.exclude` directive. Here, the
``reload`` and ``meetbot`` plugins are disabled::

    [core]
    exclude =
        reload
        meetbot

Alternatively, you can define a list of allowed plugins with
:attr:`~CoreSection.enable`: plugins not in this list will be ignored. In this
example, only the ``bugzilla`` and ``remind`` plugins are enabled (because
``meetbot`` is still excluded)::

    [core]
    enable =
        bugzilla
        remind
        meetbot
    exclude =
        reload
        meetbot

To detect plugins from extra directories, use the :attr:`~CoreSection.extra`
option.

Ignore User
-----------

To ignore users based on their hosts and/or nicks, you can use these options:

* :attr:`~CoreSection.host_blocks`
* :attr:`~CoreSection.nick_blocks`


Logging
=======

Sopel's outputs are redirected to a file named ``<base>.stdio.log``, located in
the **log directory**, which is configured by :attr:`~CoreSection.logdir`.

The ``<base>`` prefix refers to the configuration's
:attr:`~sopel.config.Config.basename` attribute.

It uses the built-in :func:`logging.basicConfig` function to configure its
logs with the following arguments:

* ``format``: set to :attr:`~CoreSection.logging_format` if configured
* ``datefmt``: set to :attr:`~CoreSection.logging_datefmt` if configured
* ``level``: set to :attr:`~CoreSection.logging_level`, default to ``WARNING``
  (see the Python documentation for `available logging levels`__)

.. __: https://docs.python.org/3/library/logging.html#logging-levels

Example of configuration for logging:

    [core]
    logging_level = INFO
    logging_format = [%(asctime)s] %(levelname)s - %(message)s
    logging_datefmt = %Y-%m-%d %H:%M:%S

.. versionadded:: 7.0

   Configuration options ``logging_format`` and ``logging_datefmt`` have been
   added to extend logging configuration.

.. versionchanged:: 7.0

   The log filename has been renamed from ``stdio.log`` to ``<base>.stdio.log``
   to prevent conflicts when running more than one instance of Sopel.

Log to a Channel
----------------

It is possible to send logs to an IRC channel, by configuring
:attr:`~CoreSection.logging_channel`. By default, it uses the same log level,
format, and date-format parameters as console logs. This can be overridden
with these settings:

* ``format`` with :attr:`~CoreSection.logging_channel_format`
* ``datefmt`` with :attr:`~CoreSection.logging_channel_datefmt`
* ``level`` with :attr:`~CoreSection.logging_channel_level`

Example of configuration to log errors only in the ``##bot_logs`` channel::

    [core]
    logging_level = INFO
    logging_format = [%(asctime)s] %(levelname)s - %(message)s
    logging_datefmt = %Y-%m-%d %H:%M:%S
    logging_channel = ##bot_logs
    logging_channel_level = ERROR
    logging_channel_format = %(message)s

.. versionadded:: 7.0

   Configuration options ``logging_channel_level``, ``logging_channel_format``
   and ``logging_channel_datefmt`` has been added to extend logging
   configuration.

Raw Logs
--------

It is possible to store raw logs of what Sopel receives and sends by setting
the flag :attr:`~CoreSection.log_raw` to true.

In that case, IRC messages received and sent are stored into a file named
``<base>.raw.log``, located in the log directory.

The ``<base>`` prefix refers to the configuration's
:attr:`~sopel.config.Config.basename` attribute.

.. versionchanged:: 7.0

   The log filename has been renamed from ``raw.log`` to ``<base>.raw.log``
   to prevent conflicts when running more than one instance of Sopel.


Other
=====

* :attr:`~CoreSection.homedir`
* :attr:`~CoreSection.default_time_format`
* :attr:`~CoreSection.default_timezone`
* :attr:`~CoreSection.not_configured`
* :attr:`~CoreSection.reply_errors`
* :attr:`~CoreSection.pid_dir`
