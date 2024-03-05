from typing import TypeVar, Awaitable, Any

import strawberry
from typing_extensions import ParamSpec

from obugs.graphql.types.generated import Entry, EntryMessagePatch

_AwaitableT = TypeVar("_AwaitableT", bound=Awaitable[Any])
_AwaitableT_co = TypeVar("_AwaitableT_co", bound=Awaitable[Any], covariant=True)
_P = ParamSpec("_P")


@strawberry.type
class ApiSuccess:
    """The Query/Mutation was process successfully, but has no result to return

    Attributes:
        message: Information message for the frontend
    """
    message: str = ""


@strawberry.type
class ProcessPatchSuccess:
    entry: Entry
    entry_message: EntryMessagePatch


@strawberry.type
class ApiError:
    """An error occurred while resolving the Query/Mutation

    Attributes:
        message: information message for the frontend
    """
    message: str
