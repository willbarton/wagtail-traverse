from collections.abc import Generator

from wagtail.blocks import (
    Block,
    BoundBlock,
    ListBlock,
    StreamBlock,
    StreamValue,
    StructBlock,
    StructValue,
)
from wagtail.blocks.list_block import ListValue
from wagtail.contrib.typed_table_block.blocks import (
    TypedTable,
    TypedTableBlock,
)


def traverse_block(
    block: Block, parent: str | None = None
) -> Generator[tuple[str, Block]]:
    """Walk a StreamBlock, yielding all possible (path, block) tuples"""
    block_name = block.name if block.name != "" else "item"
    path = f"{parent}.{block_name}" if parent is not None else block_name
    yield path, block

    if isinstance(block, StreamBlock | StructBlock | TypedTableBlock):
        for child_block_name in block.child_blocks:
            yield from traverse_block(
                block.child_blocks[child_block_name],
                parent=path,
            )
    elif isinstance(block, ListBlock):
        yield from traverse_block(
            block.child_block,
            parent=path,
        )


def traverse_value(
    value: StreamValue | BoundBlock | StructValue | ListValue | TypedTable,
    parent: str | None = None,
) -> Generator[tuple[str, BoundBlock]]:
    """Walk a StreamValue, yielding all (path, bound_block) tuples."""

    if isinstance(value, BoundBlock):
        block_name = value.block.name if value.block.name != "" else "item"
        path = f"{parent}.{block_name}" if parent is not None else block_name
        yield path, value
        yield from traverse_value(value.value, parent=path)

    elif isinstance(value, StructValue):
        for child in value.bound_blocks.values():
            yield from traverse_value(child, parent=parent)

    elif isinstance(value, ListValue):
        for child in value.bound_blocks:
            yield from traverse_value(child, parent=parent)

    elif isinstance(value, TypedTable):
        for row in value.rows:
            for child in row:
                yield from traverse_value(child, parent=parent)

    elif isinstance(value, StreamValue):
        for child in value:
            yield from traverse_value(child, parent=parent)
