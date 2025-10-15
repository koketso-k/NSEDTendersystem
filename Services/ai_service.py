from transformers import pipeline

class AIService:
    """Handles AI/ML processing for document summarization."""

    def __init__(self, model_name="facebook/bart-large-cnn"):
        self.summarizer = pipeline("summarization", model=model_name)

    def summarize_document(self, text: str, max_length=120):
        """Summarize a given document."""
        summary = self.summarizer(text, max_length=max_length, min_length=30, do_sample=False)
        return summary[0]['summary_text']
