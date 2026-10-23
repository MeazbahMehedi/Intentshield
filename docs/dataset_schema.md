# PromptGuard Evaluation Dataset

## Purpose

This dataset contains labeled prompts for evaluating PromptGuard's
ability to identify potentially malicious prompt-injection attempts
while distinguishing them from ordinary safe requests.

## Dataset size

- Total prompts: 48
- Attack prompts: 24
- Safe prompts: 24

## Fields

| Field | Type | Description |
|---|---|---|
| `id` | String | Unique identifier for each test case |
| `prompt` | String | Text submitted to the detector |
| `expected_label` | String | Expected classification: `attack` or `safe` |
| `category` | String | Main category of the prompt |
| `reason` | String | Explanation for the assigned label |

## Labels

- `attack`: The prompt contains an instruction override, jailbreak,
  request for confidential information, or another potentially
  malicious instruction.
- `safe`: The prompt is an ordinary request that should not be
  classified as a prompt-injection attack.

## Important notes

These labels are expected outcomes for evaluation. They do not
guarantee that the detector will classify every prompt correctly.
Detector performance must be measured against this dataset.