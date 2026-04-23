from __future__ import annotations

from pathlib import Path
from tempfile import TemporaryDirectory
import unittest

from skilgen.parsers import ApiSpecParserError
from skilgen.parsers.graphql import parse_graphql_schema
from skilgen.parsers.openapi import parse_openapi_spec
from skilgen.parsers.postman import parse_postman_collection


FIXTURES = Path(__file__).parent / "fixtures"


class ApiSpecParserTests(unittest.TestCase):
    def test_openapi_parser_extracts_enterprise_signals(self) -> None:
        result = parse_openapi_spec(FIXTURES / "openapi_petstore.yaml")

        self.assertEqual(result.source_type, "openapi")
        self.assertEqual(result.title, "Enterprise Petstore")
        self.assertIn("pets", result.groups)
        self.assertIn("users", result.groups)
        self.assertIn("bearerAuth:http", result.auth_schemes)
        self.assertTrue(any("listPets" in evidence for evidence in result.evidence))
        self.assertTrue(any("Pet" in evidence for evidence in result.evidence))
        self.assertTrue(any("429" in item for item in result.rate_limits))
        self.assertTrue(any("404" in item for item in result.error_responses))
        self.assertTrue(any(item.category == "deprecated-endpoint" for item in result.anti_patterns))
        self.assertTrue(any(item.category == "no-auth" for item in result.anti_patterns))
        self.assertTrue(any(item.category == "raw-pii-example" for item in result.anti_patterns))

    def test_openapi_parser_supports_swagger_2_json(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "swagger.json"
            path.write_text(
                """
                {
                  "swagger": "2.0",
                  "info": {"title": "Legacy API", "version": "1.0"},
                  "securityDefinitions": {"apiKey": {"type": "apiKey", "in": "header", "name": "X-API-Key"}},
                  "security": [{"apiKey": []}],
                  "paths": {
                    "/orders": {
                      "get": {
                        "operationId": "listOrders",
                        "responses": {"200": {"description": "OK"}, "500": {"description": "Error"}}
                      }
                    }
                  },
                  "definitions": {"Order": {"type": "object"}}
                }
                """,
                encoding="utf-8",
            )

            result = parse_openapi_spec(path)

        self.assertEqual(result.version, "2.0")
        self.assertIn("orders", result.groups)
        self.assertIn("apiKey:apiKey", result.auth_schemes)
        self.assertTrue(any("Order" in evidence for evidence in result.evidence))

    def test_openapi_parser_rejects_malformed_and_empty_input(self) -> None:
        with TemporaryDirectory() as tmp:
            malformed = Path(tmp) / "bad.yaml"
            malformed.write_text("openapi: [", encoding="utf-8")
            empty = Path(tmp) / "empty.yaml"
            empty.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ApiSpecParserError, "could not decode"):
                parse_openapi_spec(malformed)
            with self.assertRaisesRegex(ApiSpecParserError, "empty input"):
                parse_openapi_spec(empty)

    def test_graphql_parser_extracts_schema_signals(self) -> None:
        result = parse_graphql_schema(FIXTURES / "graphql_schema.graphql")

        self.assertEqual(result.source_type, "graphql")
        self.assertIn("Query", result.groups)
        self.assertIn("Mutation", result.groups)
        self.assertIn("types", result.groups)
        self.assertTrue(any(item.category == "pagination" for item in result.patterns))
        self.assertTrue(any(item.category == "nullability" for item in result.patterns))
        self.assertTrue(any(item.category == "n-plus-one-risk" for item in result.anti_patterns))
        self.assertTrue(any(item.category == "deprecated-field" for item in result.anti_patterns))
        self.assertTrue(any("directive:key" in evidence for evidence in result.evidence))

    def test_graphql_parser_supports_introspection_json(self) -> None:
        with TemporaryDirectory() as tmp:
            path = Path(tmp) / "schema.json"
            path.write_text(
                """
                {
                  "data": {
                    "__schema": {
                      "queryType": {"name": "Query"},
                      "mutationType": {"name": "Mutation"},
                      "directives": [{"name": "deprecated"}],
                      "types": [
                        {
                          "kind": "OBJECT",
                          "name": "Query",
                          "fields": [
                            {
                              "name": "pets",
                              "args": [{"name": "first"}, {"name": "after"}],
                              "type": {"kind": "NON_NULL", "ofType": {"kind": "LIST", "ofType": {"kind": "OBJECT", "name": "Pet"}}},
                              "isDeprecated": false
                            }
                          ]
                        },
                        {
                          "kind": "OBJECT",
                          "name": "Pet",
                          "fields": [
                            {"name": "id", "args": [], "type": {"kind": "NON_NULL", "ofType": {"kind": "SCALAR", "name": "ID"}}, "isDeprecated": false}
                          ]
                        }
                      ]
                    }
                  }
                }
                """,
                encoding="utf-8",
            )

            result = parse_graphql_schema(path)

        self.assertIn("Query", result.groups)
        self.assertTrue(any(item.category == "pagination" for item in result.patterns))
        self.assertTrue(any("field:Query.pets" in evidence for evidence in result.evidence))

    def test_graphql_parser_rejects_malformed_and_empty_input(self) -> None:
        with TemporaryDirectory() as tmp:
            malformed = Path(tmp) / "bad.graphql"
            malformed.write_text("type Query {", encoding="utf-8")
            empty = Path(tmp) / "empty.graphql"
            empty.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ApiSpecParserError, "found no object fields"):
                parse_graphql_schema(malformed)
            with self.assertRaisesRegex(ApiSpecParserError, "empty input"):
                parse_graphql_schema(empty)

    def test_postman_parser_extracts_collection_signals(self) -> None:
        result = parse_postman_collection(FIXTURES / "postman_collection.json")

        self.assertEqual(result.source_type, "postman")
        self.assertEqual(result.title, "Enterprise Petstore Collection")
        self.assertIn("Pets", result.groups)
        self.assertIn("Admin", result.groups)
        self.assertIn("bearer", result.auth_schemes)
        self.assertIn("apikey", result.auth_schemes)
        self.assertTrue(any(item.category == "environment-variables" for item in result.patterns))
        self.assertTrue(any(item.category == "hardcoded-url" for item in result.anti_patterns))
        self.assertTrue(any(item.category == "hardcoded-token" for item in result.anti_patterns))
        self.assertTrue(any("request:List pets" in evidence for evidence in result.evidence))

    def test_postman_parser_rejects_malformed_and_empty_input(self) -> None:
        with TemporaryDirectory() as tmp:
            malformed = Path(tmp) / "bad.json"
            malformed.write_text("{", encoding="utf-8")
            empty = Path(tmp) / "empty.json"
            empty.write_text("", encoding="utf-8")

            with self.assertRaisesRegex(ApiSpecParserError, "could not decode"):
                parse_postman_collection(malformed)
            with self.assertRaisesRegex(ApiSpecParserError, "empty input"):
                parse_postman_collection(empty)


if __name__ == "__main__":
    unittest.main()
