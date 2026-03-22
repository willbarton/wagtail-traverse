# wagtail-traverse

Utilities for traversing Wagtail `StreamField` and `StreamValue` objects.

## Installation

```
pip install wagtail-traverse
```

## Usage

This is a set of two functions:

- `traverse_block(block, parent=None)` walks a StreamField's block definition tree (the schema, not page data). 

  Given a root block, it yields back `(path, block)` tuples for every block reachable from that root, including the root itself. This is intended to be used to discover what block types and paths can exist in a StreamField.

  ```python
  from wagtailtraverse import traverse_block
  
  streamfield = MyPage._meta.get_field("body")
  for child_name in streamfield.stream_block.child_blocks:
      for path, block in traverse_block(
          streamfield.stream_block.child_blocks[child_name]
      ):
          print(f"{path}: {block.__class__.__name__}")
  ```

  For a page with a `body` field containing `heading`, `paragraph`, and a `hero` StructBlock that has an `image` and `caption`, this would print:

  ```
  heading: CharBlock
  paragraph: RichTextBlock
  hero: StructBlock
  hero.image: ImageChooserBlock
  hero.caption: CharBlock
  ```
  
- `traverse_value(value, parent=None)` walks the value of a StreamField on a page. 

  It yields `(path, bound_block)` tuples for every block in the stream value, recursing into `StreamValue`s, `StructValue`s, `ListValue`s, and `TypedTable`s. This is intended to be used for deeply inspecting or migrating the content stored in a StreamField.

  ```python
  from wagtail_traverse import traverse_value
  
  page = MyPage.objects.get(slug="example")
  for path, bound_block in traverse_value(page.body):
      print(f"{path}: {bound_block.block.__class__.__name__} = {bound_block.value}")
  ```

### Paths

Both functions produce dotted path strings like `hero.image` or `section.list.item` that describe where a block sits in the tree.

### License

This project is licensed under the MIT License. See [LICENSE](./LICENSE) for details.

These functions originate in the [wagtail-content-audit](https://github.com/cfpb/wagtail-content-audit) library as part of a block usage auditing. I have broken them out in this small utility library for convenience, since the ability to traverse `StreamField`s and their values is something I occasionally have found need to do.
