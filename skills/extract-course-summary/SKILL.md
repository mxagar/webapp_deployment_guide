---
name: extract-course-summary
description: Extract an online course from a learning page where the user has manually authenticated in their web browser, then create a course-folder README, local assets, and numbered exercise files and summarize them for learning. Use when the user invokes /extract-course-summary with folder and config arguments, asks to capture a course table of contents and lecture material, or asks to resume course summarization after supplying previously missing media or exercises.
---

# Extract Course Summary

## Invocation

Expect this form:

```text
/extract-course-summary folder <course-folder> config <config-file>
```

Example:

```text
/extract-course-summary folder @06_Data_Modeling config course_config.json
```

Treat a leading `@` on the folder value as a workspace-reference marker, not part of the folder name. Resolve `<course-folder>` from the workspace root unless the user clearly supplies another base path. Resolve `<config-file>` inside the course folder; reject paths that escape that folder.

If either argument is missing and cannot be inferred, ask one concise question. Otherwise, begin work immediately.

## Configuration

Read the JSON config before accessing the course. Require these string keys:

```json
{
  "course-name": "Course title",
  "course-url": "https://public-course-page.example",
  "course-learning-link": "https://learning-platform.example/course",
  "assets-folder": "assets",
  "exercises-folder": "lab"
}
```

Validate before extraction:

- Confirm the course folder and config file exist.
- Confirm all required config keys are present and non-empty.
- Resolve the configured asset and exercise folders inside the course folder; reject paths that escape it.
- Use `course-learning-link` as the required source for course content and use `course-url` only for public metadata or fallback context.

## Output Contract

Write all course output beneath `<course-folder>`:

- `README.md`: Course structure, extracted learning summary, links to local artifacts, setup instructions, and missing-item status.
- `{assets-folder}/`: Downloaded images and related media with descriptive, stable filenames.
- `{exercises-folder}/`: Exercises and labs numbered by first appearance, such as `01_query_basics/` or `02_build_an_api/`.

Create missing output paths without deleting existing content. Preserve user-authored material and previously downloaded artifacts. Reuse an existing artifact when it clearly represents the same source item.

Use relative Markdown links from `README.md`. Give files descriptive lowercase snake-case or kebab-case names; never retain opaque random filenames unless the source format requires them.

## Workflow

### 1. Inspect Existing State

1. Read the config.
2. Inspect the existing course `README.md`, assets folder, exercises folder, and environment files.
3. Determine whether this is:
   - a fresh extraction,
   - a continuation with missing artifacts now supplied, or
   - a refresh of an existing course summary.
4. Preserve completed work and continue from the first incomplete item.

### 2. Access the Course

1. Open or inspect `course-learning-link` in a browser session controlled or shared by the user.
2. If the learning page is not authenticated, ask the user to log in manually in that browser and tell you when the course page is ready.
3. Never request, read, handle, enter, store, or transmit login secrets.
4. After the user confirms login, analyze the already-authenticated learning page.
5. Prefer read-only page inspection or content APIs exposed by the page.
6. Avoid changing account settings, enrollment state, course progress, submissions, quiz answers, or other remote data unless the user explicitly requests it.
7. If browser inspection is unavailable or blocked, record the authenticated course content as missing instead of replacing it with public or speculative material.

### 3. Build the Course Outline

1. Extract the table of contents in course order:
   - course,
   - modules or sections,
   - subsections,
   - lectures or learning units.
2. Create corresponding headings in `README.md`.
3. Create the configured assets and exercises folders if absent.
4. Under each lecture heading, add an extraction-status marker while working:

```markdown
<!-- extraction-status: complete|partial|blocked -->
```

5. Keep the heading structure stable so the extraction can resume without duplicating content.

### 4. Extract Each Learning Unit

Process units in appearance order:

1. Capture the learning points from text, code, and available video transcripts.
2. Paraphrase source material; do not reproduce long transcripts or substantial copyrighted course text verbatim.
3. Download useful instructional images when permitted:
   - use a descriptive filename based on module and concept,
   - save it under `{assets-folder}`,
   - add its Markdown link after the relevant text summary.
4. For public embedded videos, include the public YouTube, Vimeo, or equivalent URL. Do not download videos.
5. For exercises and labs:
   - download or reconstruct accessible files while preserving their structure,
   - prefix each exercise file or folder with its two-digit appearance order,
   - add a relative link under the relevant lecture,
   - preserve notebook metadata when handling `.ipynb` files.
6. Record anything inaccessible, broken, or impossible to download in the missing-items section.

### 5. Maintain Missing Items

Keep one `## Missing Items` section near the end of `README.md`. Use a checklist with enough context for the user to fetch each item:

```markdown
## Missing Items
- [ ] Module 2 > Lecture 3: Lab download was blocked. Expected destination: `lab/04_lab_name/`. Source: <URL>
- [ ] Module 4 > Lecture 1: Diagram could not be downloaded. Expected destination: `assets/module-04_concept-diagram.png`. Source: <URL>
```

When extraction is complete but items remain missing:

1. Leave affected lecture statuses as `partial` or `blocked`.
2. Clearly report the missing items and their expected destinations.
3. Ask the user to download or provide them.
4. Stop before final section-by-section summarization so the final summary can include those artifacts.

When the user supplies missing pieces, verify them, mark checklist items complete or remove them, and resume at the affected lectures.

### 6. Summarize Section by Section

After all obtainable content and user-supplied missing pieces are present, summarize each lecture section in place. Preserve its heading, neighboring sections, artifact links, and source order where it affects understanding.

Use concise hierarchical bullets:

- Write full but short sentences, with one focused idea per sentence.
- Use parent bullets for shared phrasing and child fragments where the parent supplies the grammar.
- Nest only when hierarchy improves learning.
- Do not omit relevant details or repeat details, concepts, sentence stems, or shared phrases.
- Expand acronyms on first use with the full phrase in parentheses.
- Do not put blank lines between top-level bullets in a single summary list.
- Put image links after the lecture bullet summary and before exercise links or code blocks.
- Omit a code block when the lecture explains no code.
- Put minor details that code can express clearly into succinct code comments.

For each linked notebook or script, inspect the file and add a concise hierarchical summary directly below its link. Include:

- purpose,
- major steps,
- important inputs and outputs,
- assumptions,
- relevant API choices,
- a brief note about any modernization performed.

### 7. Verify and Modernize Code

For every code snippet, notebook, script, dependency, or API usage:

1. Use Context7 MCP to check current official documentation when available.
2. Preserve the source learning point while updating only stale generic API usage, formatting, or comments needed for a runnable modern example.
3. Do not invent behavior or make unrelated refactors.
4. If Context7 conflicts with the lesson, preserve the lesson's concept and make the smallest current-style adjustment.
5. If Context7 cannot verify an API, state that verification was unavailable and avoid unnecessary changes.
6. If a link is broken, mention it and continue with available material.

Use structured parsers where practical. Read `.ipynb` as JSON and preserve notebook metadata. Treat Markdown headings and links structurally when editing sections.

### 8. Update the Learning Environment

After processing exercises:

1. Detect the course's existing environment or dependency-management convention (for example a language-specific manifest or lockfile, a package list, or an environment definition file).
2. Add only dependencies required by the extracted exercises and not already declared.
3. Follow the repository's existing dependency-management style and avoid unrelated upgrades.
4. Ensure the course `README.md` has a concise `Setup` or equivalent section explaining how to create the environment and run the exercises.
5. Run the most relevant lightweight validation available for modified exercise files and report anything that could not be tested.

### 9. Finish

Remove temporary extraction-status comments after every lecture is complete. Keep the `Missing Items` section only when unresolved items remain.

In the final response, report:

- the course folder and README updated,
- the number of modules or sections processed,
- the assets and exercises saved,
- environment files changed,
- validation performed,
- unresolved or manually required items.
