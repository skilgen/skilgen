package com.skillayer.intellij

import com.intellij.openapi.application.ApplicationManager
import com.intellij.openapi.components.PersistentStateComponent
import com.intellij.openapi.components.Service
import com.intellij.openapi.components.State
import com.intellij.openapi.components.Storage

@Service(Service.Level.APP)
@State(name = "SkillayerSettings", storages = [Storage("skillayer.xml")])
class SkillayerSettings : PersistentStateComponent<SkillayerSettings.State> {
    data class State(
        var apiKey: String = "",
        var repoId: String = "",
        var apiUrl: String = "https://api.skillayer.com",
        var checkOnSave: Boolean = false,
        var violationSeverity: String = "ERROR",
        var warningSeverity: String = "WARNING",
    )

    private var state = State()

    override fun getState(): State = state

    override fun loadState(state: State) {
        this.state = state
    }

    companion object {
        fun getInstance(): SkillayerSettings =
            ApplicationManager.getApplication().getService(SkillayerSettings::class.java)
    }
}
