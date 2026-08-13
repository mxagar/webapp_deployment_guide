---
name: summarize-for-learning
description: Summarize and replace a named section from a file or file link for learning. Use when the user invokes /summarize-for-learning or asks to summarize a specific section of a Markdown, notebook, script, or documentation file in place into concise hierarchical bullets, reproduce or summarize explained code, and update linked notebooks/scripts or generic code comments using current Context7 documentation.
---

# Summarize For Learning

## Inputs

Expect:

- `file`: Path or link to the source file. Accept Markdown links such as `[lesson](03_Topic/README.md)`, relative paths, absolute paths, and workspace-local file references.
- `section`: Exact or approximate section title/name inside the file.
- Optional additional parameters or natural-language instructions: scope, audience, desired depth, concision, output location, or technology/library constraints.

If `file` or `section` is missing and cannot be inferred, ask one concise question before proceeding.

This skill modifies the source file by default. Do not only return the summary in chat unless the user explicitly asks not to edit files or the file cannot be modified.

## Usage Example

Use the skill with a Markdown file link and a named section:

```text
/summarize-for-learning file: [README.md](03_Topic/README.md) section: "What is X?"
```

Equivalent natural-language request:

```text
Use /summarize-for-learning on file [README.md](03_Topic/README.md), section "What is X?".
```

## Workflow

1. Resolve `file` to a workspace file:
   - For Markdown links, use the link target path.
   - For relative paths, resolve from the workspace root unless the user clearly anchors the path elsewhere.
   - For local file links or absolute paths, use the referenced path directly when accessible.
2. Find the requested section by heading, notebook cell heading, comment marker, function/class name, or nearby text match.
3. Determine the section boundary:
   - For Markdown/reStructuredText, include content until the next heading at the same or higher level.
   - For notebooks, include the matching markdown/code cell and related following cells until the next peer heading.
   - For scripts, include the matching function/class/block and its immediately relevant comments/docstrings.
4. Preserve all relevant information while removing repetition.
   - Use one idea per sentence.
   - Allow two closely related ideas in one sentence when that is more compact and avoids needless hierarchy.
   - Prefer shorter sentences over long compound sentences.
   - Break bullets into deeper nested levels when a bullet would otherwise contain several loosely related ideas.
   - Group repeated sentence stems into one parent bullet with nested child items.
   - Do not repeat the same subject, verb, or phrase across sibling bullets when one parent bullet can introduce the shared concept.
   - Expand acronyms on first use with parentheses, such as `OTT (over-the-top)`.
5. If the section discusses libraries, frameworks, APIs, CLIs, or cloud services, use MCP Context7 before writing or editing code comments/code examples. Prefer official/current docs from Context7 over memory.
6. Detect links in the section that point to notebooks or scripts. Treat relative links as relative to the source file.
7. Detect image links in the section and keep them after the generated bullet summary, before any notebook/script link summaries or code blocks.
8. For each linked notebook or script:
   - Open and inspect the linked file.
   - Use Context7 for any library/API usage that may be stale.
   - Modify the linked file to use current APIs and style when updates are needed.
   - Avoid unrelated refactors and preserve the instructional intent.
   - Remove or avoid superfluous debug/demo prints in summary code, but do not delete useful explanatory output from the real file unless it is clearly stale or noisy.
9. Replace the original requested section in the source file with the generated summary, including bullet points, retained image links, notebook/script links and summaries, and code blocks when present. Preserve the original section heading and neighboring sections.
10. In the final response, report which file and section were updated. Keep the actual summary brief or omit it unless the user asks to see it in chat.

## Summary Format

Use this structure for the requested section:

````markdown
- Use concise bullet points with full but short sentences.
  - Use nested bullets for hierarchy when it improves learning.
  - Use deeper nesting when several ideas belong under one parent point.
  - Use parent bullets to introduce shared phrasing.
    - Put repeated items as child bullets.
    - Write child bullets as concise fragments when the parent supplies the grammar.
  - Keep each sentence focused on one idea.
  - Allow two tightly connected ideas in one sentence if it keeps the summary compact.
  - Do not omit relevant details.
  - Do not repeat the same detail in multiple places.
  - Do not repeat concepts, sentence stems, or shared phrases across sibling bullets.
  - Expand acronyms on first use with the full phrase in parentheses.
- Do not insert blank lines between higher-level bullet points.

```language
# Reproduce code explained by the section here.
# Put minor explanatory details that can be represented in code as comments.
```
````

When there is no code explained in the section, omit the code block.

If the original section includes image links, keep them after the bullet summary and before any notebook/script link or code block:

```markdown
![Alt text](relative/image.png)
```

For every linked notebook or script found in the section, add the notebook/script summary directly below its link:

````markdown
[Linked notebook or script](relative/path)

- Summarize the linked file in concise hierarchical bullets.
- Include purpose, major steps, important inputs/outputs, assumptions, and relevant API choices.
- Note any modernization performed, but keep this brief.

```language
# Summarize the linked code here.
# Include the meaningful structure and core operations.
# Omit superfluous debug or demonstration prints.
```
````

## Editing Rules

- Use structured parsers when practical:
  - Read `.ipynb` as JSON and preserve notebook metadata.
  - Treat Markdown links and headings structurally when reasonable.
- Keep summaries faithful to the source material, but update generic comments and code snippets to modern APIs/style when Context7 shows a newer recommended approach.
- Do not invent details that are absent from the section or linked files.
- Do not expand lists by repeating the same phrase. Prefer `Common features include:` with nested items over repeated `Common features include ...` bullets.
- Do not over-nest lists when a compact sentence with two related ideas is clearer.
- Explain acronyms on first use, then use the acronym afterward.
- Replace only the requested section text in the source file. Preserve the section heading and neighboring sections.
- Do not add blank lines between top-level bullets in generated summaries.
- If Context7 documentation conflicts with the source text, preserve the source's learning point and update only the API/style details needed to keep examples current.
- If a link is broken, mention it and continue summarizing the available section.
- If an API cannot be verified through Context7, state that verification was not available and avoid unnecessary changes.
