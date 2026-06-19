package com.skillayer.intellij

import com.intellij.openapi.options.Configurable
import javax.swing.JComponent

class SkillayerConfigurable : Configurable {
    private var ui: SkillayerSettingsUI? = null

    override fun getDisplayName(): String = "Skillayer"

    override fun createComponent(): JComponent {
        val next = SkillayerSettingsUI()
        ui = next
        return next.component
    }

    override fun isModified(): Boolean =
        ui?.isModified(SkillayerSettings.getInstance().state) ?: false

    override fun apply() {
        ui?.applyTo(SkillayerSettings.getInstance().state)
    }

    override fun reset() {
        ui?.reset(SkillayerSettings.getInstance().state)
    }

    override fun disposeUIResources() {
        ui = null
    }
}
