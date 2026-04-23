from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
import os
from datetime import datetime

class PDFGenerator:
    def __init__(self):
        self.styles = getSampleStyleSheet()
        
        # Custom styles
        self.styles.add(ParagraphStyle(
            name='CustomTitle',
            parent=self.styles['Heading1'],
            fontSize=24,
            alignment=TA_CENTER,
            spaceAfter=30,
            textColor=colors.HexColor('#2c3e50')
        ))
        
        self.styles.add(ParagraphStyle(
            name='SectionHeading',
            parent=self.styles['Heading2'],
            fontSize=16,
            spaceAfter=12,
            spaceBefore=20,
            textColor=colors.HexColor('#34495e')
        ))
        
        self.styles.add(ParagraphStyle(
            name='KeyPoint',
            parent=self.styles['Normal'],
            fontSize=11,
            leftIndent=20,
            spaceAfter=6,
            textColor=colors.HexColor('#27ae60'),
            bulletIndent=10
        ))
    
    def generate_pdf(self, notes, diagrams, quiz, level, filename="Lecture_Notes"):
        """Generate PDF from notes, diagrams, and quiz"""
        
        # Create PDF path
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        pdf_path = f"outputs/{filename}_{timestamp}.pdf"
        
        # Create document
        doc = SimpleDocTemplate(
            pdf_path,
            pagesize=A4,
            rightMargin=72,
            leftMargin=72,
            topMargin=72,
            bottomMargin=72
        )
        
        # Build content
        story = []
        
        # Title
        title_text = notes.get('title', 'Lecture Notes')
        story.append(Paragraph(title_text, self.styles['CustomTitle']))
        story.append(Spacer(1, 0.2*inch))
        
        # Level and date info
        info_text = f"<i>Learning Level: {level.capitalize()} | Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}</i>"
        story.append(Paragraph(info_text, self.styles['Italic']))
        story.append(Spacer(1, 0.3*inch))
        
        # Summary
        if notes.get('summary'):
            story.append(Paragraph("Summary", self.styles['Heading2']))
            story.append(Paragraph(notes['summary'], self.styles['Normal']))
            story.append(Spacer(1, 0.2*inch))
        
        # Key Points
        if notes.get('key_points'):
            story.append(Paragraph("Key Highlights", self.styles['Heading2']))
            for point in notes['key_points']:
                story.append(Paragraph(f"• {point}", self.styles['KeyPoint']))
            story.append(Spacer(1, 0.2*inch))
        
        # Sections
        for section in notes.get('sections', []):
            story.append(Paragraph(section.get('heading', 'Section'), self.styles['SectionHeading']))
            
            # Content
            content = section.get('content', '')
            if content:
                story.append(Paragraph(content, self.styles['Normal']))
            
            # Bullets
            for bullet in section.get('bullets', []):
                story.append(Paragraph(bullet, self.styles['KeyPoint']))
            
            # Simplified version (if exists)
            if section.get('simplified'):
                story.append(Spacer(1, 0.1*inch))
                story.append(Paragraph("<i>Simplified Explanation:</i>", self.styles['Italic']))
                story.append(Paragraph(section['simplified'], self.styles['Normal']))
            
            story.append(Spacer(1, 0.15*inch))
        
        # Diagrams
        if diagrams:
            story.append(Paragraph("Diagrams", self.styles['Heading2']))
            
            for diagram in diagrams[:3]:  # Limit to 3 diagrams
                if os.path.exists(diagram.get('path', '')):
                    try:
                        img = Image(diagram['path'])
                        img.drawHeight = 2.5*inch
                        img.drawWidth = 4*inch
                        story.append(img)
                        
                        if diagram.get('caption'):
                            story.append(Paragraph(f"<i>{diagram['caption']}</i>", self.styles['Italic']))
                        
                        story.append(Spacer(1, 0.1*inch))
                    except:
                        pass
        
        # Quiz
        if quiz:
            story.append(Paragraph("Practice Quiz", self.styles['Heading2']))
            
            for i, q in enumerate(quiz[:5]):  # Limit to 5 questions
                question_text = f"<b>Q{i+1}:</b> {q.get('question', '')}"
                story.append(Paragraph(question_text, self.styles['Normal']))
                
                # Options
                options = q.get('options', [])
                for j, opt in enumerate(options):
                    opt_text = f"&nbsp;&nbsp;&nbsp;{chr(65+j)}. {opt}"
                    story.append(Paragraph(opt_text, self.styles['Normal']))
                
                # Correct answer (hidden in actual quiz)
                # story.append(Paragraph(f"<i>Correct: {q.get('correct', '')}</i>", self.styles['Italic']))
                
                story.append(Spacer(1, 0.1*inch))
        
        # Footer
        story.append(Spacer(1, 0.3*inch))
        footer_text = "<i>Generated by AI-Based Adaptive Notes Generator</i>"
        story.append(Paragraph(footer_text, self.styles['Italic']))
        
        # Build PDF
        doc.build(story)
        
        return pdf_path