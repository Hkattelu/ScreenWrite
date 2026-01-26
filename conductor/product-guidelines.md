# Product Guidelines: screenwrite

## Tone and Voice
- **Professional & Technical:** All user-facing communication, including CLI messages, documentation, and error reports, should be precise, technically accurate, and clear.
- **Action-Oriented:** Instructions should focus on what the user needs to do next, providing specific commands or configuration steps.
- **Clarifying Errors:** Error messages must provide actionable context or codes to help users troubleshoot issues with dependencies (ffmpeg, yt-dlp) or API keys.

## CLI Interaction & Experience
- **Rich & Interactive:** Prioritize a high-quality standalone experience for humans. Use progress bars for long-running downloads and spinners for background processing tasks.
- **Tactile Feedback:** Use clear status indicators (e.g., color-coded icons) to show the progress of script parsing, asset fetching, and timeline generation.
- **Interactive Wizards:** Where appropriate (e.g., first-time setup or reviewing beats), employ interactive prompts to guide the user through decisions rather than relying solely on complex flags.

## Error Handling & Reliability
- **Graceful Degradation:** The automation pipeline must be resilient. If a specific B-roll asset cannot be fetched, the tool should provide a placeholder or skip the item with a clear warning, allowing the rest of the timeline to be generated successfully.
- **Comprehensive Debugging:** Maintain a detailed log file for every run to assist with advanced troubleshooting, while keeping the main CLI output focused on high-level progress.

## Visual Aesthetic (UI/Preview)
- **Modern & Minimalist:** Any graphical interfaces (like the planned beat preview) should feature clean layouts, high contrast, and a "content-first" design.
- **Utility over Decoration:** Avoid unnecessary animations or decorative elements that do not serve a functional purpose.
- **Dark-Mode Optimized:** Given the developer and editor target audience, interfaces should be optimized for dark environments with clear, legible typography.

