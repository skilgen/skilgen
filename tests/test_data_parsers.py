from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.parsers.dbt import DbtProjectParseError, parse_dbt_project
from skilgen.parsers.kafka import KafkaParseError, parse_kafka_artifact
from skilgen.parsers.sql_schema import SqlSchemaParseError, parse_sql_schema


FIXTURES = Path(__file__).parent / "fixtures"


class DbtParserTests(unittest.TestCase):
    def test_parse_dbt_project_extracts_lineage_docs_tests_and_findings(self) -> None:
        analysis = parse_dbt_project(FIXTURES)

        self.assertEqual(analysis.project_name, "analytics")
        self.assertEqual(len(analysis.models), 1)
        model = analysis.models[0]
        self.assertEqual(model.name, "orders")
        self.assertEqual(model.refs, ["stg_customers"])
        self.assertEqual(model.sources, ["raw.orders"])
        self.assertIn("source_orders", model.ctes)
        self.assertIn("cents_to_dollars", model.macros)
        self.assertIn("analytics.stripe.payments", model.hardcoded_relations)
        self.assertTrue(analysis.test_coverage["orders"])
        self.assertEqual(analysis.sources[0].source_name, "raw")
        self.assertEqual(analysis.macros[0].name, "cents_to_dollars")
        self.assertIn("missing-description", {issue.category for issue in analysis.issues})
        self.assertIn("hardcoded-schema", {issue.category for issue in analysis.issues})

    def test_dbt_parser_reports_malformed_yaml(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "dbt_project.yml").write_text("name: [", encoding="utf-8")

            with self.assertRaisesRegex(DbtProjectParseError, "Could not parse"):
                parse_dbt_project(root)

    def test_dbt_parser_reports_empty_project_file(self) -> None:
        with TemporaryDirectory() as tmp:
            root = Path(tmp)
            (root / "dbt_project.yml").write_text("", encoding="utf-8")

            with self.assertRaisesRegex(DbtProjectParseError, "empty"):
                parse_dbt_project(root)


class SqlSchemaParserTests(unittest.TestCase):
    def test_parse_create_table_schema_extracts_constraints_indexes_and_audits(self) -> None:
        analysis = parse_sql_schema(FIXTURES / "schema_create.sql")

        self.assertEqual({table.name for table in analysis.tables}, {"public.customers", "public.orders"})
        orders = next(table for table in analysis.tables if table.name == "public.orders")
        self.assertEqual(orders.primary_key, ["order_id"])
        self.assertEqual(orders.foreign_keys[0].target_table, "public.customers")
        self.assertEqual(orders.comment, "Customer order facts")
        self.assertIn("idx_orders_customer_id", {index.name for index in orders.indexes})
        self.assertIn("indexed-large-text", {issue.category for issue in analysis.issues})

    def test_parse_json_schema_export_extracts_table_columns(self) -> None:
        analysis = parse_sql_schema(FIXTURES / "order_json_schema.json")

        self.assertEqual(len(analysis.tables), 1)
        table = analysis.tables[0]
        self.assertEqual(table.name, "orders")
        self.assertIn("id", table.primary_key)
        self.assertEqual({column.name for column in table.columns}, {"id", "customer_id", "status", "updated_at"})
        self.assertIn("foreign-key-coverage", {issue.category for issue in analysis.issues})

    def test_sql_schema_parser_reports_malformed_sql(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "schema.sql"
            path.write_text("CREATE TABLE broken (id BIGINT", encoding="utf-8")

            with self.assertRaisesRegex(SqlSchemaParseError, "Unbalanced"):
                parse_sql_schema(path)

    def test_sql_schema_parser_reports_empty_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "schema.sql"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(SqlSchemaParseError, "empty"):
                parse_sql_schema(path)


class KafkaParserTests(unittest.TestCase):
    def test_parse_kafka_topic_extracts_config_schema_patterns_and_audits(self) -> None:
        analysis = parse_kafka_artifact(FIXTURES / "kafka_topic.yaml")

        self.assertEqual(len(analysis.topics), 1)
        topic = analysis.topics[0]
        self.assertEqual(topic.name, "orders.events.v1")
        self.assertEqual(topic.partitions, 1)
        self.assertEqual(topic.retention_ms, 604800000)
        self.assertEqual(topic.cleanup_policy, "delete")
        self.assertEqual(analysis.schemas[0].name, "OrderEvent")
        self.assertIn("retention-configured", analysis.patterns)
        self.assertIn("schema-compatibility-configured", analysis.patterns)
        self.assertIn("delete-policy-audit", {issue.category for issue in analysis.issues})
        self.assertIn("single-partition-high-throughput", {issue.category for issue in analysis.issues})

    def test_parse_kafka_avro_schema_extracts_fields(self) -> None:
        analysis = parse_kafka_artifact(FIXTURES / "order_event.avsc")

        self.assertEqual(analysis.schemas[0].schema_type, "avro")
        self.assertEqual([field.name for field in analysis.schemas[0].fields], ["order_id", "user_id"])
        self.assertIn("schema-defined", analysis.patterns)

    def test_parse_kafka_directory_skips_unrelated_yaml(self) -> None:
        analysis = parse_kafka_artifact(FIXTURES)

        self.assertIn("orders.events.v1", {topic.name for topic in analysis.topics})
        self.assertIn("OrderEvent", {schema.name for schema in analysis.schemas})

    def test_kafka_parser_reports_malformed_yaml(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "topic.yaml"
            path.write_text("topic: [", encoding="utf-8")

            with self.assertRaisesRegex(KafkaParseError, "Could not parse"):
                parse_kafka_artifact(path)

    def test_kafka_parser_reports_empty_file(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "topic.yaml"
            path.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(KafkaParseError, "empty"):
                parse_kafka_artifact(path)


if __name__ == "__main__":
    unittest.main()
