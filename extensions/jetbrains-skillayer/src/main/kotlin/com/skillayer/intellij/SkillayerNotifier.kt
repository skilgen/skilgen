package com.skillayer.intellij

import com.intellij.notification.Notification
import com.intellij.notification.NotificationType
import com.intellij.notification.Notifications
import com.intellij.openapi.project.Project

object SkillayerNotifier {
    private const val GROUP_ID = "Skillayer"

    fun info(project: Project?, title: String, content: String) {
        notify(project, title, content, NotificationType.INFORMATION)
    }

    fun warning(project: Project?, title: String, content: String) {
        notify(project, title, content, NotificationType.WARNING)
    }

    fun error(project: Project?, title: String, content: String) {
        notify(project, title, content, NotificationType.ERROR)
    }

    fun result(project: Project?, result: CheckResult) {
        val violationCount = result.violations.size
        val warningCount = result.warnings.size
        if (violationCount == 0 && warningCount == 0) {
            info(project, "Skillayer check passed", "No findings. ${result.skillsChecked} skills checked, risk ${result.riskTier}.")
        } else {
            warning(
                project,
                "Skillayer findings",
                "$violationCount violations, $warningCount warnings. ${result.skillsChecked} skills checked, risk ${result.riskTier}.",
            )
        }
    }

    private fun notify(project: Project?, title: String, content: String, type: NotificationType) {
        Notifications.Bus.notify(Notification(GROUP_ID, title, content, type), project)
    }
}
