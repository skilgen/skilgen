package com.skillayer.intellij

import com.intellij.lang.annotation.AnnotationHolder
import com.intellij.lang.annotation.ExternalAnnotator
import com.intellij.lang.annotation.HighlightSeverity
import com.intellij.openapi.editor.Document
import com.intellij.openapi.util.TextRange
import com.intellij.psi.PsiDocumentManager
import com.intellij.psi.PsiFile

class FindingAnnotator : ExternalAnnotator<List<Finding>, List<Finding>>() {
    override fun collectInformation(file: PsiFile): List<Finding>? {
        val settings = SkillayerSettings.getInstance().state
        if (!settings.checkOnSave || settings.apiKey.isBlank() || settings.repoId.isBlank()) return emptyList()
        val virtualFile = file.virtualFile ?: return emptyList()
        val document = PsiDocumentManager.getInstance(file.project).getDocument(file) ?: return emptyList()
        val diff = SkillayerApiClient.currentFileDiff(virtualFile.path, document.text, file.project.basePath)
        return try {
            val result = SkillayerApiClient(settings.apiUrl, settings.repoId, settings.apiKey).checkDiff(diff)
            filterFindingsForPath(result.violations + result.warnings, virtualFile.path, file.project.basePath)
        } catch (_: Exception) {
            emptyList()
        }
    }

    override fun doAnnotate(collectedInfo: List<Finding>?): List<Finding> = collectedInfo.orEmpty()

    override fun apply(file: PsiFile, annotationResult: List<Finding>?, holder: AnnotationHolder) {
        val findings = annotationResult.orEmpty()
        if (findings.isEmpty()) return
        val document = PsiDocumentManager.getInstance(file.project).getDocument(file) ?: return
        val settings = SkillayerSettings.getInstance().state
        findings.forEach { finding ->
            val severity = severityForFinding(finding, settings)
            val message = messageForFinding(finding)
            holder
                .newAnnotation(severity, message)
                .range(rangeForFinding(document, finding))
                .create()
        }
    }

    companion object {
        fun filterFindingsForPath(findings: List<Finding>, filePath: String, projectBasePath: String?): List<Finding> {
            val relative = SkillayerApiClient.relativePath(filePath, projectBasePath)
            val normalizedFile = filePath.replace('\\', '/')
            return findings.filter { finding ->
                val findingPath = finding.filePath.replace('\\', '/')
                findingPath.isNotBlank() && (normalizedFile.endsWith(findingPath) || relative.endsWith(findingPath))
            }
        }

        fun severityForFinding(finding: Finding, settings: SkillayerSettings.State): HighlightSeverity {
            val configured = if (finding.severity.equals("violation", ignoreCase = true) || finding.severity.equals("error", ignoreCase = true)) {
                settings.violationSeverity
            } else {
                settings.warningSeverity
            }
            return when (configured.uppercase()) {
                "ERROR" -> HighlightSeverity.ERROR
                "WEAK_WARNING" -> HighlightSeverity.WEAK_WARNING
                "INFORMATION", "INFO" -> HighlightSeverity.INFORMATION
                else -> HighlightSeverity.WARNING
            }
        }

        fun messageForFinding(finding: Finding): String =
            buildString {
                append("[")
                append(finding.skillName.ifBlank { "Skillayer" })
                append("] ")
                append(finding.message)
                if (!finding.suggestion.isNullOrBlank()) {
                    append(" - ")
                    append(finding.suggestion)
                }
            }

        fun rangeForFinding(document: Document, finding: Finding): TextRange {
            val line = ((finding.lineNumber ?: 1) - 1).coerceIn(0, (document.lineCount - 1).coerceAtLeast(0))
            return TextRange(document.getLineStartOffset(line), document.getLineEndOffset(line))
        }
    }
}
