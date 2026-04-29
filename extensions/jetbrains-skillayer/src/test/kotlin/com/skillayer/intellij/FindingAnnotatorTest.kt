package com.skillayer.intellij

import com.intellij.lang.annotation.HighlightSeverity
import kotlin.test.Test
import kotlin.test.assertEquals

class FindingAnnotatorTest {
    @Test
    fun `filters findings by current file path`() {
        val findings = listOf(
            Finding("src/main/kotlin/App.kt", 3, "violation", "style", "Bad pattern"),
            Finding("src/main/kotlin/Other.kt", 4, "warning", "test", "Missing test"),
        )

        val filtered = FindingAnnotator.filterFindingsForPath(
            findings,
            "/repo/src/main/kotlin/App.kt",
            "/repo",
        )

        assertEquals(1, filtered.size)
        assertEquals("style", filtered.first().skillName)
    }

    @Test
    fun `maps configured severities`() {
        val state = SkillayerSettings.State(
            violationSeverity = "ERROR",
            warningSeverity = "WEAK_WARNING",
        )

        assertEquals(
            HighlightSeverity.ERROR,
            FindingAnnotator.severityForFinding(Finding("App.kt", 1, "violation", "skill", "message"), state),
        )
        assertEquals(
            HighlightSeverity.WEAK_WARNING,
            FindingAnnotator.severityForFinding(Finding("App.kt", 1, "warning", "skill", "message"), state),
        )
    }

    @Test
    fun `formats finding message with suggestion`() {
        val message = FindingAnnotator.messageForFinding(
            Finding("App.kt", 1, "warning", "testing", "Missing test", "Add a focused unit test"),
        )

        assertEquals("[testing] Missing test - Add a focused unit test", message)
    }
}
