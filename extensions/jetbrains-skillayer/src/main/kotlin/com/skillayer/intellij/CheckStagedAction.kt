package com.skillayer.intellij

import com.intellij.openapi.actionSystem.AnAction
import com.intellij.openapi.actionSystem.AnActionEvent
import com.intellij.openapi.application.ApplicationManager

class CheckStagedAction : AnAction() {
    override fun actionPerformed(event: AnActionEvent) {
        val project = event.project
        if (project == null) {
            SkillayerNotifier.warning(null, "Skillayer", "Open a project before checking staged changes.")
            return
        }

        val settings = SkillayerSettings.getInstance().state
        ApplicationManager.getApplication().executeOnPooledThread {
            try {
                val client = SkillayerApiClient(settings.apiUrl, settings.repoId, settings.apiKey)
                val diff = client.stagedDiff(project.basePath)
                if (diff.isBlank()) {
                    ApplicationManager.getApplication().invokeLater {
                        SkillayerNotifier.info(project, "Skillayer", "No staged changes to check.")
                    }
                    return@executeOnPooledThread
                }
                val result = client.checkDiff(diff)
                ApplicationManager.getApplication().invokeLater { SkillayerNotifier.result(project, result) }
            } catch (error: Exception) {
                ApplicationManager.getApplication().invokeLater {
                    SkillayerNotifier.error(project, "Skillayer staged check failed", error.message ?: "Unknown error")
                }
            }
        }
    }

    override fun update(event: AnActionEvent) {
        event.presentation.isEnabled = event.project != null
    }
}
