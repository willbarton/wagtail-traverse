from django.test import TestCase

from wagtail.blocks import (
    BoundBlock,
    CharBlock,
    FloatBlock,
    ListBlock,
    StructBlock,
)
from wagtail.contrib.typed_table_block.blocks import TypedTableBlock

from wagtailtraverse import traverse_block, traverse_value
from wagtailtraverse.tests.testapp.models import SearchTestPage


class TraverseBlockTest(TestCase):
    def test_block(self):
        streamfield = SearchTestPage._meta.get_field("streamfield_with_block")
        child = streamfield.stream_block.child_blocks["block"]
        results = list(traverse_block(child))
        self.assertEqual(len(results), 1)
        path, block = results[0]
        self.assertEqual(path, "block")
        self.assertIsInstance(block, CharBlock)

    def test_listblock(self):
        streamfield = SearchTestPage._meta.get_field("streamfield_with_list")
        child = streamfield.stream_block.child_blocks["list"]
        results = list(traverse_block(child))
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0][0], "list")
        self.assertIsInstance(results[0][1], ListBlock)
        self.assertEqual(results[1][0], "list.item")
        self.assertIsInstance(results[1][1], CharBlock)

    def test_structblock(self):
        streamfield = SearchTestPage._meta.get_field("streamfield_with_struct")
        child = streamfield.stream_block.child_blocks["struct"]
        results = list(traverse_block(child))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "struct")
        self.assertIsInstance(results[0][1], StructBlock)
        self.assertEqual(results[1][0], "struct.givenname")
        self.assertEqual(results[2][0], "struct.surname")

    def test_typedtableblock(self):
        streamfield = SearchTestPage._meta.get_field("streamfield_with_table")
        child = streamfield.stream_block.child_blocks["table"]
        results = list(traverse_block(child))
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0][0], "table")
        self.assertIsInstance(results[0][1], TypedTableBlock)
        self.assertEqual(results[1][0], "table.text")
        self.assertIsInstance(results[1][1], CharBlock)
        self.assertEqual(results[2][0], "table.numeric")
        self.assertIsInstance(results[2][1], FloatBlock)

    def test_parent_path(self):
        streamfield = SearchTestPage._meta.get_field("streamfield_with_list")
        child = streamfield.stream_block.child_blocks["list"]
        results = list(traverse_block(child, parent="body"))
        self.assertEqual(results[0][0], "body.list")
        self.assertEqual(results[1][0], "body.list.item")


class TraverseValueTest(TestCase):
    """Tests for traverse_value, which walks hydrated page data."""

    fixtures = ["wagtail_content_audit_testapp_fixture.json"]

    def setUp(self):
        self.page = SearchTestPage.objects.get(pk=3)

    def test_block_value(self):
        results = list(traverse_value(self.page.streamfield_with_block))
        self.assertEqual(len(results), 1)
        path, bound_block = results[0]
        self.assertEqual(path, "block")
        self.assertIsInstance(bound_block, BoundBlock)
        self.assertEqual(bound_block.value, "Test heading")

    def test_structvalue(self):
        results = list(traverse_value(self.page.streamfield_with_struct))
        paths = [path for path, _ in results]
        self.assertEqual(
            paths, ["struct", "struct.givenname", "struct.surname"]
        )
        # Check the leaf values
        self.assertEqual(results[1][1].value, "Testname")
        self.assertEqual(results[2][1].value, "Surtestname")

    def test_listvalue(self):
        results = list(traverse_value(self.page.streamfield_with_list))
        paths = [path for path, _ in results]
        self.assertEqual(paths, ["list", "list.item", "list.item"])
        self.assertEqual(results[1][1].value["value"], "Test one")
        self.assertEqual(results[2][1].value["value"], "Test two")

    def test_typedtableblock_value(self):
        results = list(traverse_value(self.page.streamfield_with_table))
        paths = [path for path, _ in results]
        self.assertEqual(
            paths,
            [
                "table",
                "table.text",
                "table.numeric",
                "table.text",
                "table.numeric",
            ],
        )

    def test_all_results_are_bound_blocks(self):
        """Every yielded value should be a BoundBlock."""
        for field_name in [
            "streamfield_with_block",
            "streamfield_with_list",
            "streamfield_with_struct",
            "streamfield_with_table",
        ]:
            field_value = getattr(self.page, field_name)
            for path, bound_block in traverse_value(field_value):
                self.assertIsInstance(
                    bound_block,
                    BoundBlock,
                    msg=f"Non-BoundBlock yielded at {path} in {field_name}",
                )

    def test_second_page_has_different_values(self):
        """Sanity check that traversal works across pages."""
        page_two = SearchTestPage.objects.get(pk=4)
        results = list(traverse_value(page_two.streamfield_with_block))
        self.assertEqual(results[0][1].value, "Heading")
