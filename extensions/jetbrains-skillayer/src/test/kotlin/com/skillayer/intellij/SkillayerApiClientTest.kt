package com.skillayer.intellij

import com.sun.net.httpserver.HttpServer
import java.net.InetSocketAddress
import kotlin.test.Test
import kotlin.test.assertEquals
import kotlin.test.assertTrue

class SkillayerApiClientTest {
    @Test
    fun `parse check result JSON`() {
        val json = """
            {
              "violations": [
                {
                  "file_path": "src/Main.kt",
                  "line_number": 12,
                  "severity": "violation",
                  "skill_name": "kotlin-style",
                  "message": "Use the local service helper.",
                  "suggestion": "Call SkillayerSettings.getInstance()."
                }
              ],
              "warnings": [
                {
                  "file_path": "src/App.kt",
                  "line_number": null,
                  "severity": "warning",
                  "skill_name": "testing",
                  "message": "Add coverage."
                }
              ],
              "skills_checked": 7,
              "risk_tier": "yellow"
            }
        """.trimIndent()

        val result = SkillayerApiClient.parseCheckResult(json)

        assertEquals(1, result.violations.size)
        assertEquals("src/Main.kt", result.violations.first().filePath)
        assertEquals(12, result.violations.first().lineNumber)
        assertEquals("kotlin-style", result.violations.first().skillName)
        assertEquals(1, result.warnings.size)
        assertEquals(null, result.warnings.first().lineNumber)
        assertEquals(7, result.skillsChecked)
        assertEquals("yellow", result.riskTier)
    }

    @Test
    fun `mock HTTP check accepts empty diff`() {
        val server = HttpServer.create(InetSocketAddress("127.0.0.1", 0), 0)
        var receivedBody = ""
        var receivedKey = ""
        server.createContext("/repos/repo-1/check") { exchange ->
            receivedKey = exchange.requestHeaders.getFirst("X-API-Key").orEmpty()
            receivedBody = exchange.requestBody.bufferedReader(Charsets.UTF_8).readText()
            val response = """{"violations":[],"warnings":[],"skills_checked":3,"risk_tier":"green"}"""
            exchange.sendResponseHeaders(200, response.toByteArray().size.toLong())
            exchange.responseBody.use { it.write(response.toByteArray()) }
        }
        server.start()
        try {
            val client = SkillayerApiClient("http://127.0.0.1:${server.address.port}", "repo-1", "sk-test")
            val result = client.checkDiff("")

            assertEquals("sk-test", receivedKey)
            assertEquals("""{"diff":""}""", receivedBody)
            assertEquals(3, result.skillsChecked)
            assertTrue(result.violations.isEmpty())
        } finally {
            server.stop(0)
        }
    }
}
