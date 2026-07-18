# Fact-Checking Protocol

## Agent-generated quotes are NOT primary-sourced

When an agent extracts quotes from browser-based news coverage, those extractions are one layer removed from the primary source. The agent is reading a journalist's paraphrase of a court transcript, official report, or press release.

## Known failure modes

| Written | Correct | Root cause |
|---|---|---|
| Judge: "heedless of the **severe** consequences **to** others" | "heedless of the consequences **on** others" | Agent used Guardian paraphrase, not ITV transcript |
| TfL cost: **£39 million** | **£29m** remediation + **£10m** lost income | Agent used 2024 estimate, not today's NCA figure |
| Goldring report: "wholly fictitious account" | Actually BBC coverage of Goldring, not Goldring itself | Press paraphrase presented as primary quote |

## Verification gate

Before publication: every load-bearing quote checked against primary source. Every key figure checked against today's coverage. If a quote can only be confirmed via press coverage, attribute it to that press coverage explicitly.
