{{- define "skillayer.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{- define "skillayer.fullname" -}}
{{- printf "%s-%s" .Release.Name (include "skillayer.name" .) | trunc 63 | trimSuffix "-" -}}
{{- end -}}
