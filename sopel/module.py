# coding=utf-8
"""This contains decorators and tools for creating callable plugin functions.
"""
# Copyright 2013, Ari Koivula, <ari@koivu.la>
# Copyright © 2013, Elad Alfassa <elad@fedoraproject.org>
# Copyright 2013, Lior Ramati <firerogue517@gmail.com>
# Licensed under the Eiffel Forum License 2.

from __future__ import unicode_literals, absolute_import, print_function, division

import functools
import re

__all__ = [
    # constants
    'NOLIMIT', 'VOICE', 'HALFOP', 'OP', 'ADMIN', 'OWNER',
    # decorators
    'action_commands',
    'commands',
    'echo',
    'event',
    'example',
    'intent',
    'interval',
    'nickname_commands',
    'output_prefix',
    'priority',
    'rate',
    'require_account',
    'require_admin',
    'require_chanmsg',
    'require_owner',
    'require_privilege',
    'require_privmsg',
    'rule',
    'thread',
    'unblockable',
    'url',
]


NOLIMIT = 1
"""Return value for ``callable``\\s, which suppresses rate limiting for the call.

Returning this value means the triggering user will not be
prevented from triggering the command again within the rate limit. This can
be used, for example, to allow a user to retry a failed command immediately.

.. versionadded:: 4.0
"""

VOICE = 1
"""Privilege level for the +v channel permission

.. versionadded:: 4.1
"""

HALFOP = 2
"""Privilege level for the +h channel permission

.. versionadded:: 4.1
"""

OP = 4
"""Privilege level for the +o channel permission

.. versionadded:: 4.1
"""

ADMIN = 8
"""Privilege level for the +a channel permission

.. versionadded:: 4.1
"""

OWNER = 16
"""Privilege level for the +q channel permission

.. versionadded:: 4.1
"""


def unblockable(function):
    """Decorator to exempt ``function`` from nickname and hostname blocking.

    This can be used to ensure events such as ``JOIN`` are always recorded::

        from sopel import module

        @module.event('JOIN')
        @module.unblockable
        def on_join_callable(bot, trigger):
            # do something when a user JOIN a channel
            # a blocked nickname or hostname *will* trigger this
            pass

    .. seealso::

        Sopel's :meth:`~sopel.bot.Sopel.dispatch` and
        :meth:`~sopel.bot.Sopel.get_triggered_callables` methods.

    """
    function.unblockable = True
    return function


def interval(*intervals):
    """Decorates a function to be called by the bot every X seconds.

    This decorator can be used multiple times for multiple intervals, or all
    intervals can be given at once as arguments. The first time the function
    will be called is X seconds after the bot was started.

    Unlike other plugin functions, ones decorated by interval must only take a
    :class:`sopel.bot.Sopel` as their argument; they do not get a trigger. The
    bot argument will not have a context, so functions like ``bot.say()`` will
    not have a default destination.

    There is no guarantee that the bot is connected to a server or joined a
    channel when the function is called, so care must be taken.

    Example::

        from sopel import module

        @module.interval(5)
        def spam_every_5s(bot):
            if "#here" in bot.channels:
                bot.say("It has been five seconds!", "#here")

    """
    def add_attribute(function):
        if not hasattr(function, "interval"):
            function.interval = []
        for arg in intervals:
            if arg not in function.interval:
                function.interval.append(arg)
        return function

    return add_attribute


def rule(*patterns):
    """Decorate a function to be called when a line matches the given pattern

    Each argument is a regular expression which will trigger the function.

    This decorator can be used multiple times to add more rules.

    If the Sopel instance is in a channel, or sent a PRIVMSG, where a string
    matching this expression is said, the function will execute. Note that
    captured groups here will be retrievable through the Trigger object later.

    Inside the regular expression, some special directives can be used. $nick
    will be replaced with the nick of the bot and , or :, and $nickname will be
    replaced with the nick of the bot.

    .. versionchanged:: 7.0

        The :func:`rule` decorator can be called with multiple positional
        arguments, each used to add a rule. This is equivalent to decorating
        the same function multiple times with this decorator.

    """
    def add_attribute(function):
        if not hasattr(function, "rule"):
            function.rule = []
        for value in patterns:
            if value not in function.rule:
                function.rule.append(value)
        return function

    return add_attribute


def thread(value):
    """Decorate a function to specify if it should be run in a separate thread.

    :param bool value: if true, the function is called in a separate thread;
                       otherwise from the bot's main thread

    Functions run in a separate thread (as is the default) will not prevent the
    bot from executing other functions at the same time. Functions not run in a
    separate thread may be started while other functions are still running, but
    additional functions will not start until it is completed.
    """
    threaded = bool(value)

    def add_attribute(function):
        function.thread = threaded
        return function

    return add_attribute


def echo(function=None):
    """Decorate a function to specify if it should receive echo messages.

    This decorator can be used to listen in on the messages that Sopel is
    sending and react accordingly.
    """
    def add_attribute(function):
        function.echo = True
        return function

    # hack to allow both @echo and @echo() to work
    if callable(function):
        return add_attribute(function)
    return add_attribute


def commands(*command_list):
    """Decorate a function to set one or more commands to trigger it.

    This decorator can be used to add multiple commands to one callable in a
    single line. The resulting match object will have the command as the first
    group, rest of the line, excluding leading whitespace, as the second group.
    Parameters 1 through 4, separated by whitespace, will be groups 3-6.

    Args:
        command: A string, which can be a regular expression.

    Returns:
        A function with a new command appended to the commands
        attribute. If there is no commands attribute, it is added.

    Example:
        @commands("hello"):
            If the command prefix is "\\.", this would trigger on lines starting
            with ".hello".

        @commands('j', 'join')
            If the command prefix is "\\.", this would trigger on lines starting
            with either ".j" or ".join".

    """
    def add_attribute(function):
        if not hasattr(function, "commands"):
            function.commands = []
        for command in command_list:
            if command not in function.commands:
                function.commands.append(command)
        return function
    return add_attribute


def nickname_commands(*command_list):
    """Decorate a function to trigger on lines starting with "$nickname: command".

    This decorator can be used multiple times to add multiple rules. The
    resulting match object will have the command as the first group, rest of
    the line, excluding leading whitespace, as the second group. Parameters 1
    through 4, separated by whitespace, will be groups 3-6.

    Args:
        command: A string, which can be a regular expression.

    Returns:
        A function with a new regular expression appended to the rule
        attribute. If there is no rule attribute, it is added.

    Example:
        @nickname_commands("hello!"):
            Would trigger on "$nickname: hello!", "$nickname,   hello!",
            "$nickname hello!", "$nickname hello! parameter1" and
            "$nickname hello! p1 p2 p3 p4 p5 p6 p7 p8 p9".
        @nickname_commands(".*"):
            Would trigger on anything starting with "$nickname[:,]? ", and
            would never have any additional parameters, as the command would
            match the rest of the line.

    """
    def add_attribute(function):
        if not hasattr(function, 'nickname_commands'):
            function.nickname_commands = []
        for cmd in command_list:
            if cmd not in function.nickname_commands:
                function.nickname_commands.append(cmd)
        return function
    return add_attribute


def action_commands(*command_list):
    """Decorate a function to trigger on CTCP ACTION lines.

    This decorator can be used multiple times to add multiple rules. The
    resulting match object will have the command as the first group, rest of
    the line, excluding leading whitespace, as the second group. Parameters 1
    through 4, separated by whitespace, will be groups 3-6.

    Args:
        command: A string, which can be a regular expression.

    Returns:
        A function with a new regular expression appended to the rule
        attribute. If there is no rule attribute, it is added.

    Example:
        @action_commands("hello!"):
            Would trigger on "/me hello!"
    """
    def add_attribute(function):
        function.intents = ['ACTION']
        if not hasattr(function, 'action_commands'):
            function.action_commands = []
        for cmd in command_list:
            if cmd not in function.action_commands:
                function.action_commands.append(cmd)
        return function
    return add_attribute


def priority(value):
    """Decorate a function to be executed with higher or lower priority.

    Args:
        value: Priority can be one of "high", "medium", "low". Defaults to
            medium.

    Priority allows you to control the order of callable execution, if your
    module needs it.

    """
    def add_attribute(function):
        function.priority = value
        return function
    return add_attribute


def event(*event_list):
    """Decorate a function to be triggered on specific IRC events.

    This is one of a number of events, such as 'JOIN', 'PART', 'QUIT', etc.
    (More details can be found in RFC 1459.) When the Sopel bot is sent one of
    these events, the function will execute. Note that the default
    :meth:`rule` (``.*``) will match *any* line of the correct event type(s).
    If any rule is explicitly specified, it overrides the default.

    :class:`sopel.tools.events` provides human-readable names for many of the
    numeric events, which may help your code be clearer.
    """
    def add_attribute(function):
        if not hasattr(function, "event"):
            function.event = []
        for name in event_list:
            if name not in function.event:
                function.event.append(name)
        return function
    return add_attribute


def intent(*intent_list):
    """Decorate a callable trigger on a message with any of the given intents.

    .. versionadded:: 5.2.0
    """
    def add_attribute(function):
        if not hasattr(function, "intents"):
            function.intents = []
        for name in intent_list:
            if name not in function.intents:
                function.intents.append(name)
        return function
    return add_attribute


def rate(user=0, channel=0, server=0):
    """Decorate a function to limit how often it can be triggered on a per-user
    basis, in a channel, or across the server (bot). A value of zero means no
    limit. If a function is given a rate of 20, that function may only be used
    once every 20 seconds in the scope corresponding to the parameter.
    Users on the admin list in Sopel’s configuration are exempted from rate
    limits.

    Rate-limited functions that use scheduled future commands should import
    threading.Timer() instead of sched, or rate limiting will not work properly.
    """
    def add_attribute(function):
        function.rate = user
        function.channel_rate = channel
        function.global_rate = server
        return function
    return add_attribute


def require_privmsg(message=None, reply=False):
    """Decorate a function to only be triggerable from a private message.

    :param str message: optional message said if triggered in a channel
    :param bool reply: use :meth:`~sopel.bot.Sopel.reply` instead of
                       :meth:`~sopel.bot.Sopel.say` when ``True``; defaults to
                       ``False``

    If it is triggered in a channel message, ``message`` will be said if
    given. By default, it uses :meth:`bot.say() <.bot.Sopel.say>`, but when
    ``reply`` is true, then it     uses :meth:`bot.reply() <.bot.Sopel.reply>`
    instead.

    .. versionchanged:: 7.0.0
        Added the ``reply`` parameter.
    """
    def actual_decorator(function):
        @functools.wraps(function)
        def guarded(bot, trigger, *args, **kwargs):
            if trigger.is_privmsg:
                return function(bot, trigger, *args, **kwargs)
            else:
                if message and not callable(message):
                    if reply:
                        bot.reply(message)
                    else:
                        bot.say(message)
        return guarded

    # Hack to allow decorator without parens
    if callable(message):
        return actual_decorator(message)
    return actual_decorator


def require_chanmsg(message=None, reply=False):
    """Decorate a function to only be triggerable from a channel message.

    :param str message: optional message said if triggered in private message
    :param bool reply: use :meth:`~.bot.Sopel.reply` instead of
                       :meth:`~.bot.Sopel.say` when ``True``; defaults to
                       ``False``

    If it is triggered in a private message, ``message`` will be said if
    given. By default, it uses :meth:`bot.say() <.bot.Sopel.say>`, but when
    ``reply`` is true, then it uses :meth:`bot.reply() <.bot.Sopel.reply>`
    instead.

    .. versionchanged:: 7.0.0
        Added the ``reply`` parameter.
    """
    def actual_decorator(function):
        @functools.wraps(function)
        def guarded(bot, trigger, *args, **kwargs):
            if not trigger.is_privmsg:
                return function(bot, trigger, *args, **kwargs)
            else:
                if message and not callable(message):
                    if reply:
                        bot.reply(message)
                    else:
                        bot.say(message)
        return guarded

    # Hack to allow decorator without parens
    if callable(message):
        return actual_decorator(message)
    return actual_decorator


def require_account(message=None, reply=False):  # lgtm [py/similar-function]
    """Decorate a function to require services/NickServ authentication.

    :param str message: optional message to say if a user without
                        authentication tries to trigger this function
    :param bool reply: use :meth:`~.bot.Sopel.reply` instead of
                       :meth:`~.bot.Sopel.say` when ``True``; defaults to
                       ``False``

    .. versionadded:: 7.0.0
    .. note::

        Only some networks support services authentication, and not all of
        those implement the standards required for clients like Sopel to
        determine authentication status. This decorator will block *all* use
        of functions it decorates on networks that lack the relevant features.

    .. seealso::

        The value of the :class:`trigger<.trigger.Trigger>`'s
        :meth:`account<.trigger.Trigger.account>` property determines whether
        this requirement is satisfied, and the property's documentation
        includes up-to-date details on what features a network must
        support to allow Sopel to fetch account information.
    """
    def actual_decorator(function):
        @functools.wraps(function)
        def guarded(bot, trigger, *args, **kwargs):
            if not trigger.account:
                if message and not callable(message):
                    if reply:
                        bot.reply(message)
                    else:
                        bot.say(message)
            else:
                return function(bot, trigger, *args, **kwargs)
        return guarded

    # Hack to allow decorator without parens
    if callable(message):
        return actual_decorator(message)

    return actual_decorator


def require_privilege(level, message=None, reply=False):
    """Decorate a function to require at least the given channel permission.

    :param int level: required privilege level to use this command
    :param str message: optional message said to insufficiently privileged user
    :param bool reply: use :meth:`~.bot.Sopel.reply` instead of
                       :meth:`~.bot.Sopel.say` when ``True``; defaults to
                       ``False``

    ``level`` can be one of the privilege level constants defined in this
    module. If the user does not have the privilege, the bot will say
    ``message`` if given. By default, it uses :meth:`bot.say()
    <.bot.Sopel.say>`, but when ``reply`` is true, then it uses
    :meth:`bot.reply() <.bot.Sopel.reply>` instead.

    Privilege requirements are ignored in private messages.

    .. versionchanged:: 7.0.0
        Added the ``reply`` parameter.
    """
    def actual_decorator(function):
        @functools.wraps(function)
        def guarded(bot, trigger, *args, **kwargs):
            # If this is a privmsg, ignore privilege requirements
            if trigger.is_privmsg:
                return function(bot, trigger, *args, **kwargs)
            channel_privs = bot.channels[trigger.sender].privileges
            allowed = channel_privs.get(trigger.nick, 0) >= level
            if not trigger.is_privmsg and not allowed:
                if message and not callable(message):
                    if reply:
                        bot.reply(message)
                    else:
                        bot.say(message)
            else:
                return function(bot, trigger, *args, **kwargs)
        return guarded
    return actual_decorator


def require_admin(message=None, reply=False):  # lgtm [py/similar-function]
    """Decorate a function to require the triggering user to be a bot admin.

    :param str message: optional message said to non-admin user
    :param bool reply: use :meth:`~.bot.Sopel.reply` instead of
                       :meth:`~.bot.Sopel.say` when ``True``; defaults to
                       ``False``

    When the triggering user is not an admin, the command is not run, and the
    bot will say the ``message`` if given. By default, it uses
    :meth:`bot.say() <.bot.Sopel.say>`, but when ``reply`` is true, then it
    uses :meth:`bot.reply() <.bot.Sopel.reply>` instead.

    .. versionchanged:: 7.0.0
        Added the ``reply`` parameter.
    """
    def actual_decorator(function):
        @functools.wraps(function)
        def guarded(bot, trigger, *args, **kwargs):
            if not trigger.admin:
                if message and not callable(message):
                    if reply:
                        bot.reply(message)
                    else:
                        bot.say(message)
            else:
                return function(bot, trigger, *args, **kwargs)
        return guarded

    # Hack to allow decorator without parens
    if callable(message):
        return actual_decorator(message)

    return actual_decorator


def require_owner(message=None, reply=False):  # lgtm [py/similar-function]
    """Decorate a function to require the triggering user to be the bot owner.

    :param str message: optional message said to non-owner user
    :param bool reply: use :meth:`~.bot.Sopel.reply` instead of
                       :meth:`~.bot.Sopel.say` when ``True``; defaults to
                       ``False``

    When the triggering user is not the bot's owner, the command is not run,
    and the bot will say ``message`` if given. By default, it uses
    :meth:`bot.say() <.bot.Sopel.say>`, but when ``reply`` is true, then it
    uses :meth:`bot.reply() <.bot.Sopel.reply>` instead.

    .. versionchanged:: 7.0.0
        Added the ``reply`` parameter.
    """
    def actual_decorator(function):
        @functools.wraps(function)
        def guarded(bot, trigger, *args, **kwargs):
            if not trigger.owner:
                if message and not callable(message):
                    if reply:
                        bot.reply(message)
                    else:
                        bot.say(message)
            else:
                return function(bot, trigger, *args, **kwargs)
        return guarded

    # Hack to allow decorator without parens
    if callable(message):
        return actual_decorator(message)
    return actual_decorator


def url(*url_rules):
    """Decorate a function to handle URLs.

    :param str url_rule: regex pattern to match URLs

    This decorator takes a regex string that will be matched against URLs in a
    message. The function it decorates, in addition to the bot and trigger,
    must take a third argument ``match``, which is the regular expression match
    of the URL::

        from sopel import module

        @module.url(r'https://example.com/bugs/([a-z0-9]+)')
        @module.url(r'https://short.com/([a-z0-9]+)')
        def handle_example_bugs(bot, trigger, match):
            bot.reply('Found bug ID #%s' % match.group(1))

    This should be used rather than the matching in trigger, in order to
    support e.g. the ``.title`` command.

    Under the hood, when Sopel collects the decorated handler it uses
    :meth:`sopel.bot.Sopel.register_url_callback` to register the handler.

    .. versionchanged:: 7.0

        The same function can be decorated multiple times with :func:`url`
        to register different URL patterns.

    .. versionchanged:: 7.0

        More than one pattern can be provided as positional argument at once.

    .. seealso::

        To detect URLs, Sopel uses a matching pattern built from a list of URL
        schemes, configured by
        :attr:`~sopel.config.core_section.CoreSection.auto_url_schemes`.

    """
    def actual_decorator(function):
        if not hasattr(function, 'url_regex'):
            function.url_regex = []
        for url_rule in url_rules:
            url_regex = re.compile(url_rule)
            if url_regex not in function.url_regex:
                function.url_regex.append(url_regex)
        return function
    return actual_decorator


class example(object):
    """Decorate a function with an example.

    Args:
        msg:
            (required) The example command as sent by a user on IRC. If it is
            a prefixed command, the command prefix used in the example must
            match the default `config.core.help_prefix` for compatibility with
            the built-in help module.
        result:
            What the example command is expected to output. If given, a test is
            generated using `msg` as input. The test behavior can be modified
            by the remaining optional arguments.
        privmsg:
            If true, the test will behave as if the input was sent to the bot
            in a private message. If false (default), the test will treat the
            input as having come from a channel.
        admin:
            Whether to treat the test message as having been sent by a bot
            admin (`trigger.admin == True`).
        owner:
            Whether to treat the test message as having been sent by the bot's
            owner (`trigger.owner == True`).
        repeat:
            Integer number of times to repeat the test. Useful for commands
            that return random results.
        re:
            If true, `result` is parsed as a regular expression. Also useful
            for commands that return random results, or that call an external
            API that doesn't always return the same value.
        ignore:
            List of outputs to ignore. Strings in this list are always
            interpreted as regular expressions.
        user_help:
            Whether this example should be displayed in user-facing help output
            such as `.help command`.
        online:
            If true, pytest will mark it as "online".
    """
    def __init__(self, msg, result=None, privmsg=False, admin=False,
                 owner=False, repeat=1, re=False, ignore=None,
                 user_help=False, online=False):
        # Wrap result into a list for get_example_test
        if isinstance(result, list):
            self.result = result
        elif result is not None:
            self.result = [result]
        else:
            self.result = None
        self.use_re = re
        self.msg = msg
        self.privmsg = privmsg
        self.admin = admin
        self.owner = owner
        self.repeat = repeat
        self.online = online

        if isinstance(ignore, list):
            self.ignore = ignore
        elif ignore is not None:
            self.ignore = [ignore]
        else:
            self.ignore = []

        self.user_help = user_help

    def __call__(self, func):
        if not hasattr(func, "example"):
            func.example = []

        import sys

        import sopel.test_tools  # TODO: fix circular import with sopel.bot and sopel.test_tools

        # only inject test-related stuff if we're running tests
        # see https://stackoverflow.com/a/44595269/5991
        if 'pytest' in sys.modules and self.result:
            # avoids doing `import pytest` and causing errors when
            # dev-dependencies aren't installed
            pytest = sys.modules['pytest']

            test = sopel.test_tools.get_example_test(
                func, self.msg, self.result, self.privmsg, self.admin,
                self.owner, self.repeat, self.use_re, self.ignore
            )

            if self.online:
                test = pytest.mark.online(test)

            sopel.test_tools.insert_into_module(
                test, func.__module__, func.__name__, 'test_example'
            )
            sopel.test_tools.insert_into_module(
                sopel.test_tools.get_disable_setup(), func.__module__, func.__name__, 'disable_setup'
            )

        record = {
            "example": self.msg,
            "result": self.result,
            "privmsg": self.privmsg,
            "admin": self.admin,
            "help": self.user_help,
        }
        func.example.append(record)
        return func


def output_prefix(prefix):
    """Decorate a function to add a prefix on its output.

    :param str prefix: the prefix to add (must include trailing whitespace if
                       desired; Sopel does not assume it should add anything)

    Prefix will be added to text sent through:

    * :meth:`bot.say <sopel.bot.SopelWrapper.say>`
    * :meth:`bot.notice <sopel.bot.SopelWrapper.notice>`

    """
    def add_attribute(function):
        function.output_prefix = prefix
        return function
    return add_attribute
