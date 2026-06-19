package com.skillayer.intellij

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.actionSystem.CommonDataKeys
import com.intellij.openapi.application.ApplicationManager

class CheckAction : AnAction() {
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project
        val editor = event.getData(CommonDataKeys.EDITOR)
        val file = event.getData(CommonDataKeys.VIRTUAL_FILE)
        if (project == null || editor == null || file == null) {
            SkillayerNotifier.warning(project, "Skillayer", "Open a file before running Check Current File.")
            return
        }

        val settings = SkillayerSettings.getInstance().state
        val diff = SkillayerApiClient.currentFileDiff(file.path, editor.document.text, project.basePath)
        ApplicationManager.getApplication().executeOnPooledThread {
            try {
                val result = SkillayerApiClient(settings.apiUrl, settings.repoId, settings.apiKey).checkDiff(diff)
                ApplicationManager.getApplication().invokeLater { SkillayerNotifier.result(project, result) }
            } catch (error: Exception) {
                ApplicationManager.getApplication().invokeLater {
                    SkillayerNotifier.error(project, "Skillayer check failed", error.message ?: "Unknown error")
                }
            }
        }
    }

    override fun update(event: AnActionEvent) {
        event.presentation.isEnabled = event.project != null && event.getData(CommonDataKeys.EDITOR) != null
    }
}
