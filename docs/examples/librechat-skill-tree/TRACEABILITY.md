# Traceability

This file maps requirements and detected code evidence to the generated Skilgen outputs.

## Requirements Source
- Source file: `codebase-only input`
- Source hash: `dc7b33e727a0`

## Intent To Output Mapping
### Endpoints
- Intent: Detected route: api/app/clients/BaseClient.js
  Domain: `backend`
  Evidence: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/server/services/ActionService.js`, `api/server/services/ActionService.spec.js`, `api/models/index.js`, `client/src/components/Chat/Menus/Models/fakeData.ts`, `api/server/controllers/AuthController.js`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/app/clients/OllamaClient.js
  Domain: `backend`
  Evidence: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/server/services/ActionService.js`, `api/server/services/ActionService.spec.js`, `api/models/index.js`, `client/src/components/Chat/Menus/Models/fakeData.ts`, `api/server/controllers/AuthController.js`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/app/clients/TextStream.js
  Domain: `backend`
  Evidence: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/server/services/ActionService.js`, `api/server/services/ActionService.spec.js`, `api/models/index.js`, `client/src/components/Chat/Menus/Models/fakeData.ts`, `api/server/controllers/AuthController.js`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/app/clients/index.js
  Domain: `backend`
  Evidence: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/server/services/ActionService.js`, `api/server/services/ActionService.spec.js`, `api/models/index.js`, `client/src/components/Chat/Menus/Models/fakeData.ts`, `api/server/controllers/AuthController.js`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/app/clients/prompts/artifacts.js
  Domain: `backend`
  Evidence: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/server/services/ActionService.js`, `api/server/services/ActionService.spec.js`, `api/models/index.js`, `client/src/components/Chat/Menus/Models/fakeData.ts`, `api/server/controllers/AuthController.js`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/app/clients/prompts/createContextHandlers.js
  Domain: `backend`
  Evidence: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/server/services/ActionService.js`, `api/server/services/ActionService.spec.js`, `api/models/index.js`, `client/src/components/Chat/Menus/Models/fakeData.ts`, `api/server/controllers/AuthController.js`
  Generated output: `skills/backend/SKILL.md`, `skills/backend/api/SKILL.md`, `FEATURES.md`

### UI Flows
- Intent: Detected route: api/server/routes/__test-utils__/convos-route-mocks.js
  Domain: `frontend`
  Evidence: `api/server/routes/__test-utils__/convos-route-mocks.js`, `api/server/routes/__tests__/config.spec.js`, `api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js`, `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/cache/getLogStores.js`, `api/server/services/GraphTokenService.js`
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/server/routes/__tests__/config.spec.js
  Domain: `frontend`
  Evidence: `api/server/routes/__test-utils__/convos-route-mocks.js`, `api/server/routes/__tests__/config.spec.js`, `api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js`, `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/cache/getLogStores.js`, `api/server/services/GraphTokenService.js`
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js
  Domain: `frontend`
  Evidence: `api/server/routes/__test-utils__/convos-route-mocks.js`, `api/server/routes/__tests__/config.spec.js`, `api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js`, `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/cache/getLogStores.js`, `api/server/services/GraphTokenService.js`
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/server/routes/__tests__/convos-import.spec.js
  Domain: `frontend`
  Evidence: `api/server/routes/__test-utils__/convos-route-mocks.js`, `api/server/routes/__tests__/config.spec.js`, `api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js`, `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/cache/getLogStores.js`, `api/server/services/GraphTokenService.js`
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/server/routes/__tests__/convos.spec.js
  Domain: `frontend`
  Evidence: `api/server/routes/__test-utils__/convos-route-mocks.js`, `api/server/routes/__tests__/config.spec.js`, `api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js`, `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/cache/getLogStores.js`, `api/server/services/GraphTokenService.js`
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`
- Intent: Detected route: api/server/routes/__tests__/grants.spec.js
  Domain: `frontend`
  Evidence: `api/server/routes/__test-utils__/convos-route-mocks.js`, `api/server/routes/__tests__/config.spec.js`, `api/server/routes/__tests__/convos-duplicate-ratelimit.spec.js`, `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/cache/getLogStores.js`, `api/server/services/GraphTokenService.js`
  Generated output: `skills/frontend/SKILL.md`, `skills/frontend/components/SKILL.md`, `FEATURES.md`

### Feature Planning
- Intent: Codebase-only scan
  Domain: `operations`
  Evidence: `api/server/controllers/agents/__tests__/jobReplacement.spec.js`, `api/server/utils/import/importBatchBuilder.js`, `api/server/utils/queue.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Generate skills from the current repository structure
  Domain: `operations`
  Evidence: `api/server/controllers/agents/__tests__/jobReplacement.spec.js`, `api/server/utils/import/importBatchBuilder.js`, `api/server/utils/queue.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: api/app/clients/BaseClient.js
  Domain: `operations`
  Evidence: `api/server/controllers/agents/__tests__/jobReplacement.spec.js`, `api/server/utils/import/importBatchBuilder.js`, `api/server/utils/queue.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: api/app/clients/OllamaClient.js
  Domain: `operations`
  Evidence: `api/server/controllers/agents/__tests__/jobReplacement.spec.js`, `api/server/utils/import/importBatchBuilder.js`, `api/server/utils/queue.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: api/app/clients/TextStream.js
  Domain: `operations`
  Evidence: `api/server/controllers/agents/__tests__/jobReplacement.spec.js`, `api/server/utils/import/importBatchBuilder.js`, `api/server/utils/queue.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`
- Intent: Backend route: api/app/clients/index.js
  Domain: `operations`
  Evidence: `api/server/controllers/agents/__tests__/jobReplacement.spec.js`, `api/server/utils/import/importBatchBuilder.js`, `api/server/utils/queue.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`
  Generated output: `skills/roadmap/SKILL.md`, `skills/GRAPH.md`, `REPORT.md`

## Domain Evidence

### api
- Key files: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/app/clients/index.js`, `api/app/clients/prompts/artifacts.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/app/clients/prompts/createVisionPrompt.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`, `api/app/clients/prompts/formatMessages.js`, `api/app/clients/prompts/formatMessages.spec.js`, `api/app/clients/prompts/index.js`, `api/app/clients/prompts/shadcn-docs/components.js`, `api/app/clients/prompts/shadcn-docs/generate.js`, `api/app/clients/prompts/summaryPrompts.js`, `api/app/clients/prompts/truncate.js`, `api/app/clients/specs/BaseClient.test.js`, `api/app/clients/specs/FakeClient.js`, `api/app/clients/tools/index.js`, `api/app/clients/tools/manifest.js`, `api/app/clients/tools/structured/AzureAISearch.js`, `api/app/clients/tools/structured/DALLE3.js`, `api/app/clients/tools/structured/FluxAPI.js`
- Key patterns: repo-native app surface, top-level implementation boundary, folder-driven capability map
- Sub-domains: none

### api-app
- Key files: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/app/clients/index.js`, `api/app/clients/prompts/artifacts.js`, `api/app/clients/prompts/createContextHandlers.js`, `api/app/clients/prompts/createVisionPrompt.js`, `api/app/clients/prompts/formatAgentMessages.spec.js`, `api/app/clients/prompts/formatGoogleInputs.js`, `api/app/clients/prompts/formatGoogleInputs.spec.js`, `api/app/clients/prompts/formatMessages.js`, `api/app/clients/prompts/formatMessages.spec.js`
- Key patterns: api surface: app, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-cache
- Key files: `api/cache/banViolation.js`, `api/cache/banViolation.spec.js`, `api/cache/clearPendingReq.js`, `api/cache/getLogStores.js`, `api/cache/index.js`, `api/cache/logViolation.js`
- Key patterns: api surface: cache, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-config
- Key files: `api/config/index.js`, `api/config/meiliLogger.js`, `api/config/parsers.js`, `api/config/paths.js`, `api/config/winston.js`
- Key patterns: api surface: config, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-db
- Key files: `api/db/connect.js`, `api/db/index.js`, `api/db/index.spec.js`, `api/db/indexSync.js`, `api/db/indexSync.spec.js`, `api/db/models.js`, `api/db/utils.js`, `api/db/utils.spec.js`
- Key patterns: api surface: db, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-server
- Key files: `api/server/cleanup.js`, `api/server/controllers/AuthController.js`, `api/server/controllers/AuthController.spec.js`, `api/server/controllers/Balance.js`, `api/server/controllers/EndpointController.js`, `api/server/controllers/FavoritesController.js`, `api/server/controllers/FavoritesController.spec.js`, `api/server/controllers/ModelController.js`, `api/server/controllers/PermissionsController.js`, `api/server/controllers/PluginController.js`, `api/server/controllers/PluginController.spec.js`, `api/server/controllers/TwoFactorController.js`
- Key patterns: api surface: server, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-strategies
- Key files: `api/strategies/appleStrategy.js`, `api/strategies/appleStrategy.test.js`, `api/strategies/discordStrategy.js`, `api/strategies/facebookStrategy.js`, `api/strategies/githubStrategy.js`, `api/strategies/googleStrategy.js`, `api/strategies/index.js`, `api/strategies/jwtStrategy.js`, `api/strategies/ldapStrategy.js`, `api/strategies/ldapStrategy.spec.js`, `api/strategies/localStrategy.js`, `api/strategies/openIdJwtStrategy.js`
- Key patterns: api surface: strategies, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-test
- Key files: `api/test/__mocks__/logger.js`, `api/test/__mocks__/openid-client-passport.js`, `api/test/__mocks__/openid-client.js`, `api/test/app/clients/tools/structured/OpenAIImageTools.test.js`, `api/test/app/clients/tools/util/fileSearch.test.js`, `api/test/jestSetup.js`, `api/test/server/middleware/checkBan.test.js`, `api/test/services/Files/processFileCitations.test.js`
- Key patterns: api surface: test, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### api-utils
- Key files: `api/utils/LoggingSystem.js`, `api/utils/logger.js`, `api/utils/tokens.spec.js`
- Key patterns: api surface: utils, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### client
- Key files: `client/src/@types/i18next.d.ts`, `client/src/@types/react.d.ts`, `client/src/App.jsx`, `client/src/Providers/ActivePanelContext.tsx`, `client/src/Providers/AddedChatContext.tsx`, `client/src/Providers/AgentPanelContext.tsx`, `client/src/Providers/AgentsContext.tsx`, `client/src/Providers/AgentsMapContext.tsx`, `client/src/Providers/AnnouncerContext.tsx`, `client/src/Providers/ArtifactContext.tsx`, `client/src/Providers/ArtifactsContext.tsx`, `client/src/Providers/AssistantsContext.tsx`, `client/src/Providers/AssistantsMapContext.tsx`, `client/src/Providers/BadgeRowContext.tsx`, `client/src/Providers/BookmarkContext.tsx`, `client/src/Providers/ChatContext.tsx`, `client/src/Providers/ChatFormContext.tsx`, `client/src/Providers/CodeBlockContext.tsx`, `client/src/Providers/CustomFormContext.tsx`, `client/src/Providers/DragDropContext.tsx`, `client/src/Providers/EditorContext.tsx`, `client/src/Providers/FileMapContext.tsx`, `client/src/Providers/MessageContext.tsx`, `client/src/Providers/MessagesViewContext.tsx`
- Key patterns: repo-native app surface, top-level implementation boundary, folder-driven capability map
- Sub-domains: none

### client-src
- Key files: `client/src/@types/i18next.d.ts`, `client/src/@types/react.d.ts`, `client/src/App.jsx`, `client/src/Providers/ActivePanelContext.tsx`, `client/src/Providers/AddedChatContext.tsx`, `client/src/Providers/AgentPanelContext.tsx`, `client/src/Providers/AgentsContext.tsx`, `client/src/Providers/AgentsMapContext.tsx`, `client/src/Providers/AnnouncerContext.tsx`, `client/src/Providers/ArtifactContext.tsx`, `client/src/Providers/ArtifactsContext.tsx`, `client/src/Providers/AssistantsContext.tsx`
- Key patterns: client surface: src, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### config
- Key files: `config/__tests__/migrate-prompt-permissions.spec.js`, `config/add-balance.js`, `config/ban-user.js`, `config/connect.js`, `config/create-user.js`, `config/delete-banner.js`, `config/delete-user.js`, `config/deployed-update.js`, `config/flush-cache.js`, `config/helpers.js`, `config/invite-user.js`, `config/list-balances.js`, `config/list-users.js`, `config/migrate-agent-permissions.js`, `config/migrate-prompt-permissions.js`, `config/packages.js`, `config/prepare.js`, `config/reset-meili-sync.js`, `config/reset-password.js`, `config/reset-terms.js`, `config/set-balance.js`, `config/smart-reinstall.js`, `config/stop-backend.js`, `config/translations/anthropic.ts`
- Key patterns: repo-native app surface, top-level implementation boundary, folder-driven capability map
- Sub-domains: none

### config-translations
- Key files: `config/translations/anthropic.ts`, `config/translations/comparisons.ts`, `config/translations/embeddings.ts`, `config/translations/file.ts`, `config/translations/instructions.ts`, `config/translations/keys.ts`, `config/translations/main.ts`, `config/translations/process.ts`, `config/translations/scan.ts`
- Key patterns: config surface: translations, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### e2e
- Key files: `e2e/config.local.example.ts`, `e2e/jestSetup.js`, `e2e/playwright.config.a11y.ts`, `e2e/playwright.config.local.ts`, `e2e/playwright.config.ts`, `e2e/setup/authenticate.ts`, `e2e/setup/cleanupUser.ts`, `e2e/setup/global-setup.local.ts`, `e2e/setup/global-setup.ts`, `e2e/setup/global-teardown.local.ts`, `e2e/setup/global-teardown.ts`, `e2e/specs/a11y.spec.ts`, `e2e/specs/keys.spec.ts`, `e2e/specs/landing.spec.ts`, `e2e/specs/messages.spec.ts`, `e2e/specs/nav.spec.ts`, `e2e/specs/popup.spec.ts`, `e2e/specs/settings.spec.ts`, `e2e/types.ts`
- Key patterns: repo-native app surface, top-level implementation boundary, folder-driven capability map
- Sub-domains: none

### e2e-setup
- Key files: `e2e/setup/authenticate.ts`, `e2e/setup/cleanupUser.ts`, `e2e/setup/global-setup.local.ts`, `e2e/setup/global-setup.ts`, `e2e/setup/global-teardown.local.ts`, `e2e/setup/global-teardown.ts`
- Key patterns: e2e surface: setup, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### e2e-specs
- Key files: `e2e/specs/a11y.spec.ts`, `e2e/specs/keys.spec.ts`, `e2e/specs/landing.spec.ts`, `e2e/specs/messages.spec.ts`, `e2e/specs/nav.spec.ts`, `e2e/specs/popup.spec.ts`, `e2e/specs/settings.spec.ts`
- Key patterns: e2e surface: specs, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### packages
- Key files: `packages/api/rollup.config.js`, `packages/api/src/acl/accessControlService.spec.ts`, `packages/api/src/acl/accessControlService.ts`, `packages/api/src/admin/config.handler.spec.ts`, `packages/api/src/admin/config.spec.ts`, `packages/api/src/admin/config.ts`, `packages/api/src/admin/grants.spec.ts`, `packages/api/src/admin/grants.ts`, `packages/api/src/admin/groups.spec.ts`, `packages/api/src/admin/groups.ts`, `packages/api/src/admin/index.ts`, `packages/api/src/admin/pagination.ts`, `packages/api/src/admin/roles.spec.ts`, `packages/api/src/admin/roles.ts`, `packages/api/src/admin/users.spec.ts`, `packages/api/src/admin/users.ts`, `packages/api/src/agents/__tests__/estimateMediaTokensForMessage.spec.ts`, `packages/api/src/agents/__tests__/initialize.test.ts`, `packages/api/src/agents/__tests__/load.spec.ts`, `packages/api/src/agents/__tests__/memory.test.ts`, `packages/api/src/agents/__tests__/run-summarization.test.ts`, `packages/api/src/agents/__tests__/summarization.e2e.test.ts`, `packages/api/src/agents/added.ts`, `packages/api/src/agents/auth.ts`
- Key patterns: repo-native app surface, top-level implementation boundary, folder-driven capability map
- Sub-domains: none

### packages-api
- Key files: `packages/api/rollup.config.js`, `packages/api/src/acl/accessControlService.spec.ts`, `packages/api/src/acl/accessControlService.ts`, `packages/api/src/admin/config.handler.spec.ts`, `packages/api/src/admin/config.spec.ts`, `packages/api/src/admin/config.ts`, `packages/api/src/admin/grants.spec.ts`, `packages/api/src/admin/grants.ts`, `packages/api/src/admin/groups.spec.ts`, `packages/api/src/admin/groups.ts`, `packages/api/src/admin/index.ts`, `packages/api/src/admin/pagination.ts`
- Key patterns: packages surface: api, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### packages-client
- Key files: `packages/client/babel.config.js`, `packages/client/jest.config.js`, `packages/client/jest.setup.ts`, `packages/client/rollup.config.js`, `packages/client/src/Providers/ToastContext.tsx`, `packages/client/src/Providers/index.ts`, `packages/client/src/common/enum.ts`, `packages/client/src/common/index.ts`, `packages/client/src/common/menus.ts`, `packages/client/src/common/types.ts`, `packages/client/src/components/Accordion.tsx`, `packages/client/src/components/AlertDialog.tsx`
- Key patterns: packages surface: client, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### packages-data-provider
- Key files: `packages/data-provider/babel.config.js`, `packages/data-provider/jest.config.js`, `packages/data-provider/rollup.config.js`, `packages/data-provider/server-rollup.config.js`, `packages/data-provider/specs/actions.spec.ts`, `packages/data-provider/specs/api-endpoints-subdir.spec.ts`, `packages/data-provider/specs/api-endpoints.spec.ts`, `packages/data-provider/specs/azure.spec.ts`, `packages/data-provider/specs/bedrock.spec.ts`, `packages/data-provider/specs/config-schemas.spec.ts`, `packages/data-provider/specs/filetypes.spec.ts`, `packages/data-provider/specs/generate.spec.ts`
- Key patterns: packages surface: data-provider, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### packages-data-schemas
- Key files: `packages/data-schemas/misc/ferretdb/aclBitops.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/migrationAntiJoin.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/multiTenancy.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/orgOperations.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/promptLookup.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/pullAll.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/pullSubdocument.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/randomPrompts.ferretdb.spec.ts`, `packages/data-schemas/misc/ferretdb/sharding.ferretdb.spec.ts`, `packages/data-schemas/rollup.config.js`, `packages/data-schemas/src/admin/capabilities.spec.ts`, `packages/data-schemas/src/admin/capabilities.ts`
- Key patterns: packages surface: data-schemas, Stay close to the repo-native folder seam before widening scope.
- Sub-domains: none

### roadmap
- Key files: `skills/roadmap/SKILL.md`, `REPORT.md`
- Key patterns: phase-based delivery, sequenced implementation planning, traceable next steps
- Sub-domains: roadmap-phase-0, roadmap-phase-1, roadmap-phase-2, roadmap-phase-3

### roadmap-phase-0
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

### roadmap-phase-1
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

### roadmap-phase-2
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

### roadmap-phase-3
- Key files: `skills/roadmap/SKILL.md`
- Key patterns: phase sequencing, delivery planning
- Sub-domains: none

## Architecture Traceability

### api
- Summary: Backend application guidance for API routes, services, persistence, auth, and runtime orchestration under the repo's `api/` surface.
- Evidence paths: `api/app/clients/BaseClient.js`, `api/app/clients/OllamaClient.js`, `api/app/clients/TextStream.js`, `api/app/clients/index.js`, `api/app/clients/prompts/artifacts.js`, `api/app/clients/prompts/createContextHandlers.js`
- Recommended skill path: `skills/api/SKILL.md`

### client
- Summary: Frontend application guidance for the user-facing client, routes, UI composition, and client-side runtime behavior.
- Evidence paths: `client/src/@types/i18next.d.ts`, `client/src/@types/react.d.ts`, `client/src/App.jsx`, `client/src/Providers/ActivePanelContext.tsx`, `client/src/Providers/AddedChatContext.tsx`, `client/src/Providers/AgentPanelContext.tsx`
- Recommended skill path: `skills/client/SKILL.md`

### config
- Summary: Configuration guidance for runtime configuration, feature flags, translation setup, and environment-driven behavior.
- Evidence paths: `config/__tests__/migrate-prompt-permissions.spec.js`, `config/add-balance.js`, `config/ban-user.js`, `config/connect.js`, `config/create-user.js`, `config/delete-banner.js`
- Recommended skill path: `skills/config/SKILL.md`

### e2e
- Summary: End-to-end testing guidance for browser workflows, setup, and cross-surface regression coverage.
- Evidence paths: `e2e/config.local.example.ts`, `e2e/jestSetup.js`, `e2e/playwright.config.a11y.ts`, `e2e/playwright.config.local.ts`, `e2e/playwright.config.ts`, `e2e/setup/authenticate.ts`
- Recommended skill path: `skills/e2e/SKILL.md`

### packages
- Summary: Shared package guidance for reusable internal packages that support the app runtime and product surfaces.
- Evidence paths: `packages/api/rollup.config.js`, `packages/api/src/acl/accessControlService.spec.ts`, `packages/api/src/acl/accessControlService.ts`, `packages/api/src/admin/config.handler.spec.ts`, `packages/api/src/admin/config.spec.ts`, `packages/api/src/admin/config.ts`
- Recommended skill path: `skills/packages/SKILL.md`

### roadmap
- Summary: Delivery sequencing domain that keeps phases, next steps, and implementation order explicit for agents.
- Evidence paths: `skills/roadmap/SKILL.md`, `REPORT.md`
- Recommended skill path: `skills/roadmap/SKILL.md`

## Generated Outputs
- `ANALYSIS.md` for full machine-readable project analysis
- `ARCHITECTURE.md` for evidence-backed domain architecture
- `FEATURES.md` for detected and planned feature inventory
- `REPORT.md` for human-readable summary
- `skills/MANIFEST.md` and `skills/GRAPH.md` for skill discovery
- `skills/<domain>/SKILL.md` for domain-specific execution guidance

## External Skill Traceability
- Policy mode: `permissive`
- No external skill packs were installed for this run.

## Enterprise Skill Traceability
- No active enterprise skills were installed for this run.

## MCP Connector Traceability
- No MCP connectors are currently active.

### Recommended MCP Connectors
- `github-enterprise` (`official`, oauth `True`): Detected connector keywords: github.
- `azure` (`official`, oauth `True`): Detected connector keywords: azure.
- `azure-kubernetes` (`official`, oauth `True`): Detected connector keywords: aks.
- `figma` (`official`, oauth `True`): Detected connector keywords: figma.

## Gaps And Next Actions
- This run was codebase-only, so roadmap and intent guidance came from implementation signals rather than a product spec.
