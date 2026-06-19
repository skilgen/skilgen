package com.skillayer.intellij

import java.io.BufferedReader
import java.io.File
import java.io.InputStreamReader
import java.io.OutputStreamWriter
import java.net.HttpURLConnection
import java.net.URL

data class Finding(
    val filePath: String,
    val lineNumber: Int?,
    val severity: String,
    val skillName: String,
    val message: String,
    val suggestion: String? = null,
)

data class CheckResult(
    val violations: List<Finding>,
    val warnings: List<Finding>,
    val skillsChecked: Int,
    val riskTier: String,
)

class SkillayerApiClient(
    private val apiUrl: String,
    private val repoId: String,
    private val apiKey: String,
) {
    fun checkDiff(diff: String): CheckResult {
        require(repoId.isNotBlank()) { "Skillayer repo ID is not configured" }
        require(apiKey.isNotBlank()) { "Skillayer API key is not configured" }

        val endpoint = URL("${apiUrl.trimEnd('/')}/repos/${encodePath(repoId)}/check")
        val connection = endpoint.openConnection() as HttpURLConnection
        connection.requestMethod = "POST"
        connection.connectTimeout = 15_000
        connection.readTimeout = 30_000
        connection.doOutput = true
        connection.setRequestProperty("Content-Type", "application/json")
        connection.setRequestProperty("X-API-Key", apiKey)

        OutputStreamWriter(connection.outputStream, Charsets.UTF_8).use { writer ->
            writer.write("""{"diff":${quote(diff)}}""")
        }

        val stream = if (connection.responseCode in 200..299) connection.inputStream else connection.errorStream
        val body = stream?.bufferedReader(Charsets.UTF_8)?.use(BufferedReader::readText).orEmpty()
        if (connection.responseCode !in 200..299) {
            throw IllegalStateException("Skillayer API error ${connection.responseCode}: $body")
        }
        return parseCheckResult(body)
    }

    fun stagedDiff(projectBasePath: String?): String {
        val cwd = projectBasePath?.let(::File)?.takeIf { it.isDirectory } ?: File(".")
        val process = ProcessBuilder("git", "diff", "--cached")
            .directory(cwd)
            .redirectErrorStream(true)
            .start()
        val output = process.inputStream.bufferedReader(Charsets.UTF_8).readText()
        val exit = process.waitFor()
        if (exit != 0) throw IllegalStateException("git diff --cached failed: $output")
        return output
    }

    companion object {
        fun parseCheckResult(json: String): CheckResult {
            val parser = JsonParser(json)
            val root = parser.parseObject()
            return CheckResult(
                violations = parseFindings(root["violations"]),
                warnings = parseFindings(root["warnings"]),
                skillsChecked = numberValue(root["skills_checked"]) ?: numberValue(root["skillsChecked"]) ?: 0,
                riskTier = stringValue(root["risk_tier"]) ?: stringValue(root["riskTier"]) ?: "unknown",
            )
        }

        fun currentFileDiff(filePath: String, content: String, projectBasePath: String?): String {
            val displayPath = relativePath(filePath, projectBasePath)
            val lines = content.split("\n")
            val header = "--- a/$displayPath\n+++ b/$displayPath\n@@ -0,0 +1,${lines.size} @@\n"
            return header + lines.joinToString("\n") { "+$it" }
        }

        fun relativePath(filePath: String, projectBasePath: String?): String {
            val normalized = filePath.replace(File.separatorChar, '/')
            val base = projectBasePath?.replace(File.separatorChar, '/')?.trimEnd('/')
            return if (!base.isNullOrBlank() && normalized.startsWith("$base/")) {
                normalized.removePrefix("$base/")
            } else {
                normalized
            }
        }

        private fun parseFindings(value: Any?): List<Finding> {
            val rows = value as? List<*> ?: return emptyList()
            return rows.mapNotNull { row ->
                val map = row as? Map<*, *> ?: return@mapNotNull null
                Finding(
                    filePath = stringValue(map["file_path"]) ?: stringValue(map["filePath"]) ?: "",
                    lineNumber = numberValue(map["line_number"]) ?: numberValue(map["lineNumber"]),
                    severity = stringValue(map["severity"]) ?: "warning",
                    skillName = stringValue(map["skill_name"]) ?: stringValue(map["skillName"]) ?: "Skillayer",
                    message = stringValue(map["message"]) ?: "",
                    suggestion = stringValue(map["suggestion"]),
                )
            }
        }

        private fun stringValue(value: Any?): String? = value as? String

        private fun numberValue(value: Any?): Int? = when (value) {
            is Number -> value.toInt()
            is String -> value.toIntOrNull()
            else -> null
        }

        private fun encodePath(value: String): String =
            java.net.URLEncoder.encode(value, Charsets.UTF_8).replace("+", "%20")

        private fun quote(value: String): String = buildString {
            append('"')
            value.forEach { char ->
                when (char) {
                    '\\' -> append("\\\\")
                    '"' -> append("\\\"")
                    '\n' -> append("\\n")
                    '\r' -> append("\\r")
                    '\t' -> append("\\t")
                    else -> if (char.code < 0x20) append("\\u%04x".format(char.code)) else append(char)
                }
            }
            append('"')
        }
    }
}

private class JsonParser(private val input: String) {
    private var index = 0

    fun parseObject(): Map<String, Any?> {
        skipWhitespace()
        expect('{')
        val result = linkedMapOf<String, Any?>()
        skipWhitespace()
        if (peek() == '}') {
            index++
            return result
        }
        while (true) {
            val key = parseString()
            skipWhitespace()
            expect(':')
            result[key] = parseValue()
            skipWhitespace()
            when (peek()) {
                ',' -> {
                    index++
                    skipWhitespace()
                }
                '}' -> {
                    index++
                    return result
                }
                else -> error("Expected ',' or '}' at $index")
            }
        }
    }

    private fun parseArray(): List<Any?> {
        expect('[')
        val result = mutableListOf<Any?>()
        skipWhitespace()
        if (peek() == ']') {
            index++
            return result
        }
        while (true) {
            result.add(parseValue())
            skipWhitespace()
            when (peek()) {
                ',' -> {
                    index++
                    skipWhitespace()
                }
                ']' -> {
                    index++
                    return result
                }
                else -> error("Expected ',' or ']' at $index")
            }
        }
    }

    private fun parseValue(): Any? {
        skipWhitespace()
        return when (peek()) {
            '"' -> parseString()
            '{' -> parseObject()
            '[' -> parseArray()
            't' -> {
                expectLiteral("true")
                true
            }
            'f' -> {
                expectLiteral("false")
                false
            }
            'n' -> {
                expectLiteral("null")
                null
            }
            else -> parseNumber()
        }
    }

    private fun parseString(): String {
        expect('"')
        val builder = StringBuilder()
        while (index < input.length) {
            val char = input[index++]
            when (char) {
                '"' -> return builder.toString()
                '\\' -> {
                    val escaped = input[index++]
                    builder.append(
                        when (escaped) {
                            '"', '\\', '/' -> escaped
                            'b' -> '\b'
                            'f' -> '\u000c'
                            'n' -> '\n'
                            'r' -> '\r'
                            't' -> '\t'
                            'u' -> input.substring(index, index + 4).toInt(16).toChar().also { index += 4 }
                            else -> escaped
                        },
                    )
                }
                else -> builder.append(char)
            }
        }
        error("Unterminated string")
    }

    private fun parseNumber(): Number {
        val start = index
        while (index < input.length && input[index] in "-0123456789.eE+") index++
        val raw = input.substring(start, index)
        return if (raw.contains('.') || raw.contains('e', ignoreCase = true)) raw.toDouble() else raw.toLong()
    }

    private fun skipWhitespace() {
        while (index < input.length && input[index].isWhitespace()) index++
    }

    private fun expect(char: Char) {
        skipWhitespace()
        if (peek() != char) error("Expected '$char' at $index")
        index++
    }

    private fun expectLiteral(literal: String) {
        if (!input.startsWith(literal, index)) error("Expected '$literal' at $index")
        index += literal.length
    }

    private fun peek(): Char = input.getOrNull(index) ?: error("Unexpected end of JSON")
}
