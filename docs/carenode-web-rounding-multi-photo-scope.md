# Carenode: Web Rounding Multi-Photo Support

Backend scope for [CIP-9660](https://cipherhealth.atlassian.net/browse/CIP-9660). Web rounding only — no mobile API, no migration.

## Data model

- Add `max_attachments` (default `10`) to script answer options (`Rounding::Answer`)
- Add `orchid_image_ids` (array) to in-progress draft answers (`Rounding::InteractionAttempt::Answer`) and completed interaction answers (`Answer`)
- Keep existing `orchid_image_id` during rollout for backward compatibility

## Web API — load round

- Update `Rounding::InteractionAttemptSerializer` to return per answer:
  - `orchid_image_ids` (array)
  - `orchid_image_urls` (array, for thumbnails)
- Update `Rounding::AnswerSerializer` to return `max_attachments` on script answer options

## Web API — save answer

- Update `Angular::Rounding::AttemptsController` to accept `orchid_image_ids: []` in `answer_question`
- Validate max photos per answer (use script’s `max_attachments`, default 10)
- Reject photos on answers where `allow_attachments` is false

## Web API — upload

- No new upload endpoint — keep `POST /rounding/images/upload_image` (one file per request)
- Web app uploads sequentially and appends each returned id to `orchid_image_ids`

## Answer save logic

- Change photo handling from **replace** to **append**
- When `orchid_image_ids` shrinks (user removes a photo), delete the orphaned `OrchidImage` records
- Update `clear_questions!`, `persist_images` (on submit), and expired draft cleanup to handle arrays

## Submit round

- Update `CopyQuestionnaireOperation` to copy `orchid_image_ids` from draft to completed interaction

## Post-submit display & integrations

- Update interaction/issue views and `AnswerDecorator` to show multiple photos (not just one)
- Update ServiceNow, Infor, and TMA integrations to attach all photos, not just the first

## Script builder (Evolve admin)

- When `allow_attachments` is enabled on an answer, persist `max_attachments: 10`
- Include `max_attachments` in script copy/duplicate operations

## Tests

- Append photo, remove photo, enforce max limit
- Serializer returns arrays + URLs
- Submit round preserves all photos
- Integrations receive all photos

## Out of scope

- Mobile Orchid API changes
- Data migration/backfill
- DBT/reporting updates
