class MarkdownUtils:
    @staticmethod
    def clean_code_blocks(text):
        """Clean markdown text by removing code block markers"""
        if text.startswith("```markdown\n"):
            text = text[len("```markdown\n"):]
        if text.startswith("```"):
            text = text[3:]
        if text.endswith("\n```"):
            text = text[:-len("\n```")]
        elif text.endswith("```"):
            text = text[:-3]
        return text