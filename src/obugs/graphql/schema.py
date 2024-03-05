import strawberry

from obugs.graphql.mutations.entry import entry_create
from obugs.graphql.mutations.entry_message import entry_comment, entry_message_delete, entry_patch_process, \
    entry_patch_submit
from obugs.graphql.mutations.software import software_suggest, software_suggestion_delete, software_upsert
from obugs.graphql.mutations.tag import tag_upsert
from obugs.graphql.mutations.user import user_ban, user_change_role
from obugs.graphql.mutations.vote import vote
from obugs.graphql.queries.entry import entries, entry
from obugs.graphql.queries.entry_message import entry_messages, entry_messages_open_patches
from obugs.graphql.queries.software import software, software_suggestions, softwares
from obugs.graphql.queries.tag import tags
from obugs.graphql.queries.user import user_current, user, users
from obugs.graphql.queries.vote import vote_my
from obugs.graphql.types.generated import strawberry_sqlalchemy_mapper


@strawberry.type
class Mutation:
    entry_create = strawberry.mutation(resolver=entry_create)
    entry_comment = strawberry.mutation(resolver=entry_comment)
    entry_message_delete = strawberry.mutation(resolver=entry_message_delete)
    entry_patch_process = strawberry.mutation(resolver=entry_patch_process)
    entry_patch_submit = strawberry.mutation(resolver=entry_patch_submit)
    software_suggest = strawberry.mutation(resolver=software_suggest)
    software_suggestion_delete = strawberry.mutation(resolver=software_suggestion_delete)
    software_upsert = strawberry.mutation(resolver=software_upsert)
    tag_upsert = strawberry.mutation(resolver=tag_upsert)
    user_ban = strawberry.mutation(resolver=user_ban)
    user_change_role = strawberry.mutation(resolver=user_change_role)
    vote = strawberry.mutation(resolver=vote)


@strawberry.type
class Query:
    entries = strawberry.field(resolver=entries)
    entry = strawberry.field(resolver=entry)
    entry_messages = strawberry.field(resolver=entry_messages)
    entry_messages_open_patches = strawberry.field(resolver=entry_messages_open_patches)
    software = strawberry.field(resolver=software)
    software_suggestions = strawberry.field(resolver=software_suggestions)
    softwares = strawberry.field(resolver=softwares)
    tags = strawberry.field(resolver=tags)
    user = strawberry.field(resolver=user)
    user_current = strawberry.field(resolver=user_current)
    users = strawberry.field(resolver=users)
    vote_my = strawberry.field(resolver=vote_my)


strawberry_sqlalchemy_mapper.finalize()
additional_types = list(strawberry_sqlalchemy_mapper.mapped_types.values())
schema = strawberry.Schema(query=Query, mutation=Mutation, types=additional_types)
