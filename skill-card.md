## Description:

Creates sourced daily industry briefings with structured analysis and optional delivery to configured channels.

This skill is ready for commercial/non-commercial use.

## Publisher:

[haiyangchenbj](https://clawhub.ai/user/haiyangchenbj)

### License/Terms of Use:

MIT-0

## Use Case:

Industry analysts and teams use this skill to collect recent first-hand news, produce a reviewed daily intelligence brief, and optionally share it through configured channels. The default profile covers Data and AI infrastructure and can be adapted to other industries.

### Deployment Geography for Use:

Global

## Known Risks and Mitigations:

Risk: Configured delivery channels can share briefing content outside the workspace.

Mitigation: Review the brief and enabled recipients before publishing or sending.

Risk: Webhook URLs, email credentials, or GitHub tokens may be exposed if stored in committed configuration.

Mitigation: Keep credentials out of committed files and use least-privilege GitHub tokens.

## Reference(s):

- [Industry Daily Brief on ClawHub](https://clawhub.ai/haiyangchenbj/skills/data-ai-daily-brief)
- [Skill documentation](artifact/README.md)

## Skill Output:

**Output Type(s):** [Markdown, HTML, Text]

**Output Format:** [Sourced Markdown daily brief; optional HTML page and channel-specific message summaries]

**Output Parameters:** [1D]

**Other Properties Related to Output:** [Includes dated sections, source links, impact analysis, and a review gate before delivery.]

## Skill Version(s):

5.0.5 (source: server-resolved release metadata and skill frontmatter)

## Ethical Considerations:

Users should evaluate whether this skill is appropriate for their environment, review any generated or modified files before relying on them, and apply their organization's safety, security, and compliance requirements before deployment.
