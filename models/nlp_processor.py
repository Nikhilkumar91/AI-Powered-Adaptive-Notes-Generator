from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import spacy
from collections import Counter
import re

class NLPProcessor:
    def __init__(self):
        print("Loading NLP models...")
        # Load summarization pipeline
        self.summarizer = pipeline("summarization", model="facebook/bart-large-cnn")
        
        # Load spaCy for keyword extraction
        self.nlp = spacy.load("en_core_web_sm")
        
        # Load question generation model (optional)
        try:
            self.qg_tokenizer = AutoTokenizer.from_pretrained("valhalla/t5-small-qg-hl")
            self.qg_model = AutoModelForSeq2SeqLM.from_pretrained("valhalla/t5-small-qg-hl")
        except:
            print("Question generation model not available")
            self.qg_model = None
    
    def generate_notes(self, text, level='beginner'):
        """Generate structured notes from transcribed text"""
        
        # Split into sections
        sections = self._split_into_sections(text)
        
        notes = {
            'title': self._extract_title(text),
            'sections': [],
            'key_points': [],
            'summary': '',
            'level': level
        }
        
        # Process each section
        for i, section in enumerate(sections[:5]):  # Limit to 5 sections
            section_notes = {
                'heading': f"Section {i+1}: {self._generate_heading(section)}",
                'content': self._simplify_text(section, level),
                'bullets': self._extract_bullet_points(section)
            }
            notes['sections'].append(section_notes)
        
        # Extract key points
        notes['key_points'] = self._extract_key_points(text, level)
        
        # Generate summary
        notes['summary'] = self._generate_summary(text)
        
        return notes
    
    def _split_into_sections(self, text):
        """Split text into logical sections"""
        # Simple split by sentences and group
        sentences = text.split('. ')
        sections = []
        current_section = []
        
        for sentence in sentences:
            current_section.append(sentence)
            if len(current_section) >= 5:  # 5 sentences per section
                sections.append('. '.join(current_section))
                current_section = []
        
        if current_section:
            sections.append('. '.join(current_section))
        
        return sections
    
    def _extract_title(self, text):
        """Extract main title from text"""
        # Take first sentence or generate title
        first_sentence = text.split('.')[0]
        if len(first_sentence) < 60:
            return first_sentence
        return "Lecture Notes"
    
    def _generate_heading(self, text):
        """Generate heading for a section"""
        # Take first 8-10 words
        words = text.split()[:8]
        return ' '.join(words) + '...'
    
    def _simplify_text(self, text, level):
        """Simplify text based on learning level"""
        if level == 'beginner':
            # Very simple explanation
            doc = self.nlp(text)
            simple_sentences = []
            for sent in doc.sents:
                # Keep only main clauses
                words = [token.text for token in sent if not token.is_stop or token.pos_ in ['NOUN', 'VERB']]
                simple_sentences.append(' '.join(words))
            return ' '.join(simple_sentences[:3])
        
        elif level == 'intermediate':
            # Moderate detail
            return text[:300] + '...' if len(text) > 300 else text
        
        else:  # advanced
            # Full detail
            return text
    
    def _extract_bullet_points(self, text):
        """Extract bullet points from text"""
        doc = self.nlp(text)
        bullets = []
        
        # Extract noun phrases as potential bullet points
        for chunk in doc.noun_chunks:
            if len(chunk.text.split()) <= 5:  # Keep short phrases
                bullets.append(f"• {chunk.text}")
        
        return bullets[:5]  # Limit to 5 bullets
    
    def _extract_key_points(self, text, level):
        """Extract key points based on frequency and importance"""
        doc = self.nlp(text)
        
        # Extract important phrases
        key_phrases = []
        for sent in list(doc.sents)[:10]:  # First 10 sentences
            # Find sentences with important keywords
            if any(word in sent.text.lower() for word in ['important', 'key', 'main', 'essential', 'crucial']):
                key_phrases.append(sent.text)
        
        # If no explicit key points, take first few sentences
        if not key_phrases:
            key_phrases = [sent.text for sent in list(doc.sents)[:5]]
        
        # Adjust for level
        if level == 'beginner':
            key_phrases = [p[:100] for p in key_phrases[:3]]
        elif level == 'intermediate':
            key_phrases = key_phrases[:5]
        
        return key_phrases
    
    def _generate_summary(self, text):
        """Generate summary using Hugging Face"""
        try:
            # Limit text length for summarizer
            if len(text) > 1000:
                text = text[:1000]
            
            summary = self.summarizer(text, max_length=150, min_length=50, do_sample=False)
            return summary[0]['summary_text']
        except:
            # Fallback: take first few sentences
            sentences = text.split('.')
            return '. '.join(sentences[:3]) + '.'
    
    def generate_adaptive_explanations(self, notes, weak_topics):
        """Generate simplified explanations for weak topics"""
        adaptive_notes = notes.copy()
        
        for topic in weak_topics:
            # Find relevant section
            for section in adaptive_notes.get('sections', []):
                if topic.lower() in section.get('heading', '').lower():
                    # Create simplified version
                    section['simplified'] = self._simplify_text(
                        section.get('content', ''), 
                        'beginner'
                    )
                    section['has_simplified'] = True
        
        return adaptive_notes