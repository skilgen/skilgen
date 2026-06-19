package com.skillayer.intellij

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.project.ProjectManager
import com.intellij.openapi.ui.ComboBox
import com.intellij.ui.components.JBCheckBox
import com.intellij.ui.components.JBLabel
import com.intellij.ui.components.JBTextField
import com.intellij.util.ui.JBUI
import java.awt.Desktop
import java.awt.GridBagConstraints
import java.awt.GridBagLayout
import java.net.URI
import javax.swing.JButton
import javax.swing.JComponent
import javax.swing.JEditorPane
import javax.swing.JPanel
import javax.swing.JPasswordField
import javax.swing.event.HyperlinkEvent

class SkillayerSettingsUI {
    private val apiKeyField = JPasswordField()
    private val repoIdField = JBTextField()
    private val apiUrlField = JBTextField()
    private val checkOnSaveBox = JBCheckBox("Check on save")
    private val violationSeverityBox = ComboBox(arrayOf("ERROR", "WARNING", "WEAK_WARNING", "INFORMATION"))
    private val warningSeverityBox = ComboBox(arrayOf("WARNING", "WEAK_WARNING", "INFORMATION"))
    private val testButton = JButton("Test connection")

    val component: JComponent = JPanel(GridBagLayout()).apply {
        border = JBUI.Borders.empty(12)
        addRow("API Key", apiKeyField, 0)
        addRow("Repo ID", repoIdField, 1)
        addRow("API URL", apiUrlField, 2)
        addRow("", checkOnSaveBox, 3)
        addRow("Violation severity", violationSeverityBox, 4)
        addRow("Warning severity", warningSeverityBox, 5)
        addRow("", testButton, 6)
        addRow("", settingsLink(), 7)
        add(JPanel(), GridBagConstraints().apply {
            gridx = 0
            gridy = 8
            weightx = 1.0
            weighty = 1.0
            fill = GridBagConstraints.BOTH
        })
    }

    init {
        testButton.addActionListener { testConnection() }
    }

    fun reset(state: SkillayerSettings.State) {
        apiKeyField.text = state.apiKey
        repoIdField.text = state.repoId
        apiUrlField.text = state.apiUrl
        checkOnSaveBox.isSelected = state.checkOnSave
        violationSeverityBox.selectedItem = state.violationSeverity
        warningSeverityBox.selectedItem = state.warningSeverity
    }

    fun applyTo(state: SkillayerSettings.State) {
        state.apiKey = String(apiKeyField.password)
        state.repoId = repoIdField.text.trim()
        state.apiUrl = apiUrlField.text.trim().ifBlank { "https://api.skillayer.com" }
        state.checkOnSave = checkOnSaveBox.isSelected
        state.violationSeverity = violationSeverityBox.selectedItem as String
        state.warningSeverity = warningSeverityBox.selectedItem as String
    }

    fun isModified(state: SkillayerSettings.State): Boolean =
        String(apiKeyField.password) != state.apiKey ||
            repoIdField.text.trim() != state.repoId ||
            apiUrlField.text.trim().ifBlank { "https://api.skillayer.com" } != state.apiUrl ||
            checkOnSaveBox.isSelected != state.checkOnSave ||
            violationSeverityBox.selectedItem != state.violationSeverity ||
            warningSeverityBox.selectedItem != state.warningSeverity

    private fun JPanel.addRow(label: String, field: JComponent, row: Int) {
        add(JBLabel(label), GridBagConstraints().apply {
            gridx = 0
            gridy = row
            anchor = GridBagConstraints.WEST
            insets = JBUI.insets(4, 0, 4, 12)
        })
        add(field, GridBagConstraints().apply {
            gridx = 1
            gridy = row
            weightx = 1.0
            fill = GridBagConstraints.HORIZONTAL
            insets = JBUI.insets(4, 0)
        })
    }

    private fun settingsLink(): JEditorPane =
        JEditorPane("text/html", """<a href="https://app.skillayer.com/dashboard/settings">Open Skillayer dashboard settings</a>""").apply {
            isEditable = false
            isOpaque = false
            addHyperlinkListener { event ->
                if (event.eventType == HyperlinkEvent.EventType.ACTIVATED) {
                    Desktop.getDesktop().browse(URI(event.url.toString()))
                }
            }
        }

    private fun testConnection() {
        val apiKey = String(apiKeyField.password)
        val repoId = repoIdField.text.trim()
        val apiUrl = apiUrlField.text.trim().ifBlank { "https://api.skillayer.com" }
        val project = ProjectManager.getInstance().openProjects.firstOrNull()
        testButton.isEnabled = false
        ApplicationManager.getApplication().executeOnPooledThread {
            try {
                val result = SkillayerApiClient(apiUrl, repoId, apiKey).checkDiff("")
                ApplicationManager.getApplication().invokeLater {
                    SkillayerNotifier.info(project, "Skillayer connection succeeded", "${result.skillsChecked} skills checked.")
                    testButton.isEnabled = true
                }
            } catch (error: Exception) {
                ApplicationManager.getApplication().invokeLater {
                    SkillayerNotifier.error(project, "Skillayer connection failed", error.message ?: "Unknown error")
                    testButton.isEnabled = true
                }
            }
        }
    }
}
