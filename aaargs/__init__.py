"""The aaargs library to help with autocompletion and argparse library"""

import argparse
import typing

import zninit


class ArgumentParser(zninit.ZnInit):
    """Define a dataclass like container for the argparse library"""

    prog = None
    usage = None
    description = None
    epilog = None
    parents = None
    formatter_class = argparse.HelpFormatter
    prefix_chars = "-"
    fromfile_prefix_chars = None
    argument_default = None
    conflict_handler = "error"
    add_help = True
    allow_abbrev = True

    def __init_subclass__(cls, **kwargs):
        """Allow adding arguments through subclass creation"""
        super().__init_subclass__()
        for key in kwargs:
            if key in dir(cls):
                setattr(cls, key, kwargs[key])
            else:
                raise AttributeError(f"Class {cls} has no attribute '{key}'.")
        return cls

    @classmethod
    def get_parser(cls) -> argparse.ArgumentParser:
        """Get the ArgumentParser object based on class attributes."""
        if cls.parents is None:
            cls.parents = []
        parser = argparse.ArgumentParser(
            prog=cls.prog,
            usage=cls.usage,
            description=cls.description,
            epilog=cls.epilog,
            parents=cls.parents,
            formatter_class=cls.formatter_class,
            prefix_chars=cls.prefix_chars,
            fromfile_prefix_chars=cls.fromfile_prefix_chars,
            argument_default=cls.argument_default,
            conflict_handler=cls.conflict_handler,
            add_help=cls.add_help,
            allow_abbrev=cls.allow_abbrev,
        )
        arguments: typing.List[Argument] = cls._get_descriptors()

        for argument in arguments:
            parser.add_argument(*argument.name_or_flags, **argument.kwargs)

        return parser

    @classmethod
    def parse_args(cls, args=None, namespace=None):
        """Run parse_args from the argparse.ArgumentParser

        Parameters
        ----------
        args: List of strings to parse. The default is taken from sys.argv
        namespace: An object to take the attributes.

        Returns
        -------
        an instance of 'self' with all attributes set.

        """
        parser = cls.get_parser()
        args = parser.parse_args(args, namespace)
        try:
            return cls(**args.__dict__)
        except TypeError as err:
            arguments: typing.List[Argument] = cls._get_descriptors()
            argument_names = [
                argument.name
                for argument in arguments
                if argument.name not in args.__dict__
            ]
            raise AttributeError(
                f"Arguments '{argument_names}' not in '{args}'. Check that the"
                f" attribute names '{argument_names}' matche the argparse names. E.g."
                " 'filename = Argument(--filename)'."
            ) from err


class Argument(zninit.Descriptor):
    """An argparse argument."""

    def __init__(
        self,
        *name_or_flags: str,
        action=None,
        choices=None,
        const=None,
        default=None,
        dest=None,
        help=None,
        metavar=None,
        nargs=None,
        required=None,
        type=None,
        positional=True,
    ):
        """Replace the argparse.ArgumentParser.add_argument method.

        All arguments are passed to argparse.ArgumentParser.add_argument

        Parameters
        ----------
        positional: bool, default = True. Make the argument positional or keyword
            argument, if no name_or_flags are provided.

        """
        if default is not None:
            super().__init__(default=default)
        else:
            super().__init__()
        self.name_or_flags = name_or_flags
        self.positional = positional

        self.kwargs = {}

        if action is not None:
            self.kwargs["action"] = action
        if choices is not None:
            self.kwargs["choices"] = choices
        if const is not None:
            self.kwargs["const"] = const
        if default is not None:
            self.kwargs["default"] = default
        if dest is not None:
            self.kwargs["dest"] = dest
        if help is not None:
            self.kwargs["help"] = help
        if metavar is not None:
            self.kwargs["metavar"] = metavar
        if nargs is not None:
            self.kwargs["nargs"] = nargs
        if required is not None:
            self.kwargs["required"] = required
        if type is not None:
            self.kwargs["type"] = type

    def __get__(self, instance, owner=None):
        """Get method of the descriptor

        This class is used to set the name and allows for the special case:

        >>> class MyArgs(ArgumentParser):
        >>>     filename = Argument()

        which will define a positional argument without defining 'name_or_flags'.
        When using 'positional=False' it will be converted to a keyword only argument.

        """
        if len(self.name_or_flags) == 0:
            self.name_or_flags = (self.name if self.positional else f"--{self.name}",)
        return super().__get__(instance, owner)
