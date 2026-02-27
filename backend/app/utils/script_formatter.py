def format_youtube_script(script_json: str) -> str:
    """
    Converts your LLM JSON string into a clean, readable,
    YouTube-ready script with emojis & section headers.
    """

    import json

    try:
        data = json.loads(script_json)
    except Exception:
        # If script is plain-text, return as-is
        return script_json

    title = data.get("title", "").strip()
    sections = data.get("sections", [])

    output_lines = []

    # Title block
    if title:
        output_lines.append(f"🎬 TITLE: {title}\n")

    for sec in sections:
        heading = sec.get("heading", "").strip()
        content = sec.get("content", "").strip()

        if heading:
            # Make headings pretty
            if "hook" in heading.lower():
                output_lines.append(f"🔥 {heading.upper()}")
            elif "intro" in heading.lower():
                output_lines.append(f"🎯 {heading.upper()}")
            elif "conclusion" in heading.lower():
                output_lines.append(f"🏁 {heading.upper()}")
            else:
                output_lines.append(f"🟦 {heading}")

        if content:
            output_lines.append(content)
            output_lines.append("")  # blank line for spacing

    return "\n".join(output_lines).strip()
