# Agent Rules

## startup/state-file-fresh
- category: startup
- check: state_file_fresh
Agent herhangi bir tool çağrısından önce agent_state.json'u okumalıdır.

## forbidden/no-out-of-scope-writes
- category: forbidden
- check: no_out_of_scope_writes
Aktif task'ın scope kontratının dışındaki bir dosyayı asla düzenleme.

## done/tests-pass
- category: definition_of_done
- check: tests_pass
Bir task ancak her acceptance command sıfır exit ettiğinde done'dur.

## uncertainty/open-question-note
- category: uncertainty
- check: opened_question_when_unsure
Confidence eşiğin altında olduğunda, tahmin etmek yerine bir soru notu aç.

## approval/new-dependency
- category: approval
- check: new_dependency_approved
Bir runtime dependency eklemek açık insan onayı gerektirir.
