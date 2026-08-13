---
name: process-course-summary
description: Process an existing, poorly formatted course README.md section by section into a structured learning summary that teaches how to do what the source explains, using the README's text, images, links, transcripts, code, and exercises. Complete incomplete examples and narrated exercises into modern fenced code blocks, preserve available artifacts, and remove references to missing artifacts. Use when the user invokes /process-course-summary, asks to clean up or summarize an already populated course README, or wants an imported course dump converted into a coherent offline course guide without fetching content from URLs.
---

# Process Course Summary

## Invocation

Expect this form:

```text
/process-course-summary folder <course-folder> [config <config-file>]
```

Examples:

```text
/process-course-summary folder @06_SQL_DataModeling
/process-course-summary folder @06_SQL_DataModeling config config.json
```

Treat a leading `@` as a workspace-reference marker, not part of the folder name. Resolve the course folder from the workspace root unless the user clearly supplies another base path. Require an existing `README.md` inside the course folder. Resolve a relative config path from the course folder and reject paths that escape it.

If the folder cannot be inferred, ask one concise question. Otherwise, begin immediately.

## Optional Configuration

The config file is optional. Do not require `config.json` or any other config file. When no config argument is supplied, process the course using the existing folder structure and discovered files.

When a config file is supplied:

1. Read it as JSON if it exists and is valid.
2. Treat every parameter as optional.
3. Use a provided non-empty parameter as a hint or override.
4. Infer missing or empty parameters from the course folder, README, and existing artifacts.
5. Ignore unknown parameters.
6. If the supplied config file is missing or invalid, mention it and continue using inferred defaults unless doing so would risk modifying the wrong course folder.

Recognize these optional parameters when present:

```json
{
  "course-name": "Course title",
  "course-url": "https://public-course-page.example",
  "course-learning-link": "https://learning-platform.example/course",
  "assets-folder": "assets",
  "exercises-folder": "lab"
}
```

Default behavior:

- Infer `course-name` from the README title or course-folder name.
- Treat `course-url` and `course-learning-link` as optional labels only. Never visit them or use them to fetch course content.
- Discover asset and exercise folders from existing references and directory contents.
- Use `assets` and `exercises` only as fallback folder-name hints; do not create them unless processing requires them.
- Resolve configured asset and exercise folders inside the course folder and ignore values that escape it.

## Output Contract

Process the existing course content in place:

- Reformat and summarize `<course-folder>/README.md`.
- Preserve useful local assets, exercises, code, and environment files.
- Preserve working links and image references in their relevant course sections.
- Remove links and image references whose targets are not provided or available.
- Use the content already present in `README.md` as the course-content source.
- Never visit URLs or fetch remote content while processing the course.
- Do not invent replacement content for unavailable references.
- Do not delete unreferenced files or unrelated user-authored content.

Use relative Markdown links for local artifacts. Preserve the original course order unless the existing order is clearly malformed and the intended hierarchy can be determined confidently.

Treat the processed README as a learning-ready guide: the reader should be able to understand and apply the technique, workflow, or exercise explained by each section without needing to decode raw transcripts or incomplete snippets.

## Workflow

### 1. Inspect Existing Course State

1. Read the optional config when supplied and infer all unspecified settings.
2. Read the complete course `README.md`.
3. Inspect the course folder, likely asset and exercise folders, and environment files.
4. Identify headings, prose, lists, images, links, code blocks, exercises, setup instructions, duplicated fragments, and malformed transcript artifacts.
5. Check the git worktree before editing and preserve unrelated user changes.
6. Determine the intended course hierarchy from the strongest available signals:
   - existing headings,
   - numbering and titles,
   - table of contents,
   - repeated structural patterns,
   - artifact names and locations.

Treat the README and available local files as the complete source set. Do not browse, open, request, or download content from any URL, including configured course URLs and links found in the README.

### 2. Validate References

Inspect every Markdown image, ordinary link, HTML image, and clearly referenced local artifact.

For local references:

1. Resolve relative paths from the `README.md` location.
2. Decode URL-escaped path segments when checking the target.
3. Preserve the reference when the target exists.
4. Remove the Markdown or HTML reference when the target does not exist.
5. Preserve meaningful visible link text as plain text when removing an ordinary link.
6. Remove a missing image reference entirely, including an empty caption or wrapper created only for that image.

For external references:

1. Never visit the external URL to verify or fetch content.
2. Preserve the link when it is syntactically valid and appears intentionally provided.
3. Remove the link destination when it is empty, malformed, an unresolved placeholder, or explicitly marked as missing or unavailable in the README.
4. Preserve meaningful visible link text as plain text when removing the destination.
5. Remove an external image reference entirely unless its image content is already provided locally.

For reference-style Markdown, remove or update both the usage and its definition as needed. Do not leave empty bullets, empty headings, dangling punctuation, or sentences that only announce a removed artifact.

### 3. Establish Structure

1. Build a coherent heading hierarchy for the course, modules, sections, and lectures.
2. Repair malformed Markdown and inconsistent heading levels.
3. Keep each surviving image, link, exercise, and code block near the content it supports.
4. Remove duplicated content only when it is clearly redundant.
5. Preserve relevant details even when the source formatting is poor.

Do not add a `Missing Items` section for removed references unless the user explicitly requests an audit. The default result should contain only available course content.

### 4. Summarize Section by Section

Process one top-level README content section at a time in source order, where a section is each `##` heading and all of its nested `###` or deeper subsections. Do not process `###` sections as independent units outside their parent `##`. Complete and verify the current `##` section before moving to the next `##` section so changes remain easy to review and correct.

1. Preserve the section heading and convert its body into concise, learning-focused Markdown.
2. Treat video transcripts, transcript fragments, slide narration, and lecture notes as ordinary source text to summarize.
3. Paraphrase verbose or transcript-like prose; do not reproduce substantial source text verbatim.
4. Use bullet-pointed summaries as the default format in every substantive section.
5. Use full but short sentences with one focused idea per bullet.
6. Use hierarchical bullets when they improve comprehension.
7. State concepts directly. Remove source-narration phrases such as "the video mentions," "the instructor explains," "this section discusses," or "the course shows."
8. Treat each bullet as additive: include it only when it introduces a new idea, detail, consequence, example, or relationship.
9. Do not repeat concepts already established earlier in the section or course unless a brief reference is essential to explain a genuinely new idea.
10. Consolidate overlapping source fragments into one complete bullet instead of restating them.
11. Avoid repeating details, sentence stems, shared phrases, or equivalent wording.
12. Expand acronyms on first use with the full phrase in parentheses.
13. Preserve useful examples, commands, and code in appropriately labeled fences.
14. Convert narrated exercises, inline code, pseudo-code, shell commands, configuration fragments, and malformed snippets into complete fenced code blocks when they are meant to be used as examples.
15. Complete incomplete code blocks or embedded code fragments when the README and local artifacts provide enough intent to do so confidently.
16. Follow current library, framework, language, and command-line standards for completed examples, using local dependency files and available official documentation context when needed; do not modernize in ways that change the exercise's learning goal.
17. Add concise code examples when they would clarify an important concept and the README does not already provide one.
18. Derive added examples from the section's existing concepts and keep them focused, runnable, and clearly illustrative.
19. Do not add speculative APIs, behavior, or course facts merely to create an example.
20. Keep surviving image references after the related explanation and before exercise links or code blocks when practical.
21. Preserve useful external links as learning references when valid, but summarize the surrounding idea so the README remains useful offline.
22. Do not invent factual details absent from the README, available local files, or documentation consulted only to verify technical standards.

Do not put blank lines between top-level bullets in a single summary list.

Use this default section shape when applicable:

````markdown
## Existing Section Heading

- Concise summary point.
- Related concept.
  - Supporting detail.

```python
# Focused example that clarifies the section.
```

![Available local image](assets/example.png)

```python
# Completed exercise or example solution.
```
````

### 5. Process Linked Exercises and Code

For each surviving local notebook, script, exercise file, or exercise folder:

1. Inspect the artifact using a structured parser where practical.
2. Read `.ipynb` files as JSON and preserve notebook metadata.
3. Add a concise hierarchical summary directly below its README link, covering:
   - purpose,
   - major steps,
   - important inputs and outputs,
   - assumptions,
   - relevant API choices.
4. Preserve the artifact's learning goal.
5. Modify linked code only when required to fix stale generic APIs, formatting, or comments needed for a runnable modern example.
6. Avoid unrelated refactors.

When exercises, labs, quizzes, or examples are narrated in the README instead of supplied as files:

1. Treat them as examples to explain, not as challenges for the reader to solve later.
2. Convert the exercise prompt and any provided solution fragments into one complete solution code block when practical.
3. If an exercise already includes a solution, present the complete solution directly and explain the important choices after it.
4. Do not write teaser language such as "try this first" or "we will build this and reveal the solution later."
5. Preserve setup commands, expected inputs, and expected outputs near the completed solution.

### 6. Verify Technical Content

When the README or linked artifacts discuss libraries, frameworks, APIs, CLIs, commands, or configuration:

1. Do not visit course URLs or use links from the README to fetch additional course content.
2. Preserve the README's learning goal and avoid changing APIs based only on uncertain memory.
3. When completing or modernizing code requires current syntax or behavior, consult local dependency files first and then approved official documentation sources if available.
4. Add or improve code examples when the available local content provides enough context to do so confidently.
5. Run the most relevant lightweight local validation for modified code or notebooks.

### 7. Update the Learning Environment

When linked exercises require dependencies:

1. Detect the existing environment or dependency-management convention (for example a language-specific manifest or lockfile, a package list, or an environment definition file).
2. Add only required dependencies that are not already declared.
3. Follow the repository's existing dependency-management style and avoid unrelated upgrades.
4. Ensure the course README has concise setup instructions when exercises require an environment.

### 8. Final Review

Before finishing:

1. Re-scan the processed README for broken local references.
2. Confirm no URL was visited or used to fetch course content.
3. Confirm no unavailable image or link references remain.
4. Confirm every substantive section uses a clear bullet-pointed summary and helpful code blocks where appropriate.
5. Confirm each `##` section was processed as a unit, with nested `###` content kept under its parent context.
6. Confirm transcripts and narrated material were summarized as learning content.
7. Confirm incomplete or narrated code examples and exercises were converted into complete fenced code blocks where practical.
8. Confirm solved exercises are presented directly as complete examples with explanation, not as delayed reveals.
9. Confirm the summary states ideas directly without referring to videos, instructors, courses, transcripts, or source sections.
10. Confirm every bullet adds a new idea and repeated concepts have been consolidated or removed.
11. Confirm surviving artifacts remain in their relevant sections.
12. Confirm heading hierarchy, Markdown fences, and lists render coherently.
13. Confirm neighboring files and unrelated user changes were preserved.

In the final response, report:

- the course folder and README processed,
- the sections processed,
- the available images, links, and exercises preserved,
- the unavailable references removed,
- environment files changed,
- validation performed,
- anything that could not be verified.
