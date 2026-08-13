---
name: format-for-learning
description: Reformat a named tutorial section from a file or file link into structured Markdown for learning. Use when the user invokes /format-for-learning or asks to clean up a tutorial section while preserving the original order of text, images, links, code blocks, commands, and examples.
---

# Format For Learning

## Inputs

Expect:

- `file`: Path or link to the source file. Accept Markdown links such as `[README.md](03_Topic/README.md)`, relative paths, absolute paths, and workspace-local file references.
- `section`: Exact or approximate section title/name inside the file.
- Optional additional instructions: desired depth, audience, whether to add code fences, acronym style, or technology/library constraints.

If `file` or `section` is missing and cannot be inferred, ask one concise question before proceeding.

## Workflow

1. Resolve `file` to a workspace file.
   - For Markdown links, use the link target path.
   - For relative paths, resolve from the workspace root unless the user clearly anchors the path elsewhere.
   - For absolute paths or local file links, use the referenced path directly when accessible.
2. Find the requested section by heading, nearby text match, notebook cell heading, comment marker, function name, or class name.
3. Determine the section boundary.
   - For Markdown/reStructuredText, include content until the next heading at the same or higher level.
   - For notebooks, include the matching cell group until the next peer heading.
   - For scripts, include the matching function/class/block and directly related comments.
4. Preserve the original sequence of ideas and artifacts.
   - Do not move images, links, command blocks, code blocks, examples, or explanatory text out of their original relative order.
   - Reformat each segment in place.
   - Add subsections where they clarify the existing flow.
5. Convert tutorial prose into learning-friendly Markdown.
   - Keep the text as tutorial content, not a compressed transcript summary.
   - Break long paragraphs into concise paragraphs or bullet lists.
   - Use nested bullets to group repeated stems or related items.
   - Do not repeat concepts, sentence stems, or shared phrases across sibling bullets.
   - Allow two closely related ideas in one sentence when it avoids unnecessary hierarchy.
   - Do not omit relevant details.
6. Preserve and improve technical artifacts.
   - Fence commands, file trees, source code, settings snippets, terminal output, and configuration examples with appropriate languages.
   - Keep image links and ordinary links in their original position relative to the surrounding explanation.
   - Expand acronyms on first use with parentheses, then use the acronym afterward.
7. Use MCP Context7 when the section discusses libraries, frameworks, APIs, CLIs, commands, or configuration.
   - Prefer current official docs from Context7 over memory.
   - Update stale command names, settings examples, comments, and generic API style when needed.
   - Preserve the tutorial's learning goal when updating details.
8. Replace only the requested section body with the formatted Markdown.
   - Preserve the requested section heading.
   - Preserve neighboring sections.
   - Do not add blank lines between top-level bullets inside a single bullet-list block.

## Format Guidelines

Use this pattern when helpful:

````markdown
#### Existing Section Heading

##### Clear Subsection

Short tutorial paragraph.

- Grouped learning point.
  - Related detail.
  - Related detail.

```bash
command --example
```

![Existing image](relative/path.png)

##### Next Subsection

Continue in the same order as the source section.
````

Use code fences for:

- commands and terminal steps,
- file trees,
- source code,
- settings,
- URLs or output blocks when they are shown as examples.

## Editing Rules

- Preserve content order over topical regrouping.
- Preserve all existing image links and file links unless they are broken.
- Keep tutorial explanations readable and instructional.
- Do not invent details that are absent from the source section or verified current docs.
- If placeholders or broken transcript artifacts appear, replace them with the intended command/code only when the surrounding text makes the intended content clear.
- If an API cannot be verified through Context7, say so in the final response and avoid unnecessary changes.
