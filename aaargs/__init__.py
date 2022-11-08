"""The aaargs library to help with attribute autocompletion and argparse library"""
import argparse
import dataclasses
import importlib.metadata
import typing

import zninit

__version__ = importlib.metadata.version("aaargs")


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
        for key, value in kwargs.items():
            if key in dir(cls):
                setattr(cls, key, value)
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
            parser.add_argument(*argument.name_or_flags, **argument.options.get_dict())

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
                f" attribute names {argument_names} match the argparse names. E.g."
                " 'filename = Argument(--filename)'."
            ) from err


@dataclasses.dataclass
class _ArgumentOptions:
    action: typing.Any
    choices: typing.Any
    const: typing.Any
    default: typing.Any
    dest: typing.Any
    help: typing.Any
    metavar: typing.Any
    nargs: typing.Any
    required: bool
    type: typing.Any

    def get_dict(self) -> dict:
        """Get a dict of all value pairs that are not None"""
        return {
            key.name: getattr(self, key.name)
            for key in dataclasses.fields(self)
            if getattr(self, key.name) is not None
        }


class Argument(zninit.Descriptor):
    """An argparse argument."""

    def __init__(
        self,
        *name_or_flags: str,
        action=None,
        choices=None,
        const=None,
        default=zninit.Empty,
        dest=None,
        help=None,
        metavar=None,
        nargs=None,
        required=None,
        type=None,
        positional=False,
    ):
        """Replace the argparse.ArgumentParser.add_argument method.

        All arguments are passed to argparse.ArgumentParser.add_argument

        Parameters
        ----------
        positional: bool, default = True. Make the argument positional or keyword
            argument, if no name_or_flags are provided.

        """
        if required:
            if default in (zninit.Empty, None):
                default = zninit.Empty
            else:
                raise TypeError(
                    "When using 'required=True' the argument 'default' must be None"
                )
        elif default is zninit.Empty:
            default = None
        super().__init__(default=default)
        self.name_or_flags = name_or_flags
        self.positional = positional

        self.options = _ArgumentOptions(
            action=action,
            choices=choices,
            const=const,
            default=default,
            dest=dest,
            help=help,
            metavar=metavar,
            nargs=nargs,
            required=required,
            type=type,
        )

        self._check_input()

    def _check_input(self):
        if self.options.required and self.positional:
            raise TypeError("'required' is an invalid argument for positionals`")

    @property
    def _is_boolean(self) -> bool:
        """Check type annotations if Argument is defined as boolean"""
        return self.owner.__annotations__.get(self.name) in ["bool", bool]

    def _handle_boolean_annotation(self):
        if self._is_boolean and self.options.action is None:
            self.options.action = "store_true"
            if len(self.name_or_flags) == 0:
                if self.positional:
                    raise TypeError(
                        "Can not use boolean annotation with positional only Argument"
                        f" '{self.name}'"
                    )
                if self.default not in (True, False, None, zninit.Empty):
                    raise ValueError(
                        f"Default value for boolean argument '{self.name}' can only be"
                        f" boolean, not '{self.default}'"
                    )
                self.name_or_flags = (f"--{self.name}",)

    def __get__(self, instance, owner=None):
        """Get method of the descriptor

        This class is used to set the name and allows for the special case:

        >>> class MyArgs(ArgumentParser):
        >>>     filename = Argument()
        >>>     verbose: bool = Argument()

        which will define a positional argument without defining 'name_or_flags'.
        When using 'positional=False' it will be converted to a keyword only argument.
        Futhermore, it allows for boolean arguments without defining 'positional=False'
        or 'action=store_true' explicitly.

        """
        self._handle_boolean_annotation()

        if len(self.name_or_flags) == 0:
            self.name_or_flags = (self.name if self.positional else f"--{self.name}",)

        if self._is_boolean and self.default in (None, zninit.Empty):
            self._default = False

        return super().__get__(instance, owner)
