from uuid import UUID

from beartype import beartype
from temporalio import activity

from agents_api.autogen.openapi_model import Entry
from agents_api.models.entry.delete_entries import delete_entries
from agents_api.models.entry.entries_summarization import get_toplevel_entries_query


def get_extra_entries(messages: list[Entry], token_count_threshold: int) -> list[UUID]:
    result: list[UUID] = []

    if not len(messages):
        return messages

    token_cnt, offset = 0, 0
    if messages[0].role == "system":
        token_cnt, offset = messages[0].token_count, 1

    for m in reversed(messages[offset:]):
        token_cnt += m.token_count
        if token_cnt >= token_count_threshold:
            result.append(m.id)

    return result


@activity.defn
@beartype
async def truncation(
    developer_id: str, session_id: str, token_count_threshold: int
) -> None:
    session_id = UUID(session_id)
    developer_id = UUID(developer_id)

    delete_entries(
        developer_id=developer_id,
        session_id=session_id,
        entry_ids=get_extra_entries(
            [
                Entry(
                    entry_id=row["entry_id"],
                    session_id=session_id,
                    source=row["source"],
                    role=row["role"],
                    name=row["name"],
                    content=row["content"],
                    created_at=row["created_at"],
                    timestamp=row["timestamp"],
                    tokenizer=row["tokenizer"],
                )
                for _, row in get_toplevel_entries_query(
                    session_id=session_id
                ).iterrows()
            ],
            token_count_threshold,
        ),
    )
