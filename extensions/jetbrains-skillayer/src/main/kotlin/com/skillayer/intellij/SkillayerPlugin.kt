package com.skillayer.intellij

import com.intellij.AppTopics
import com.intellij.codeInsight.daemon.DaemonCodeAnalyzer
import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.editor.Document
import com.intellij.openapi.fileEditor.FileDocumentManagerListener
import com.intellij.openapi.project.Project
import com.intellij.openapi.startup.StartupActivity

class SkillayerPlugin : StartupActivity.DumbAware {
    override fun runActivity(project: Project) {
        project.messageBus.connect().subscribe(
            AppTopics.FILE_DOCUMENT_SYNC,
            object : FileDocumentManagerListener {
                override fun beforeDocumentSaving(document: Document) {
                    if (!SkillayerSettings.getInstance().state.checkOnSave) return
                    ApplicationManager.getApplication().invokeLater {
                        if (!project.isDisposed) DaemonCodeAnalyzer.getInstance(project).restart()
                    }
                }
            },
        )
    }
}
