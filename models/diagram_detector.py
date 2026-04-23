import cv2
import numpy as np
import os
from PIL import Image
import pytesseract

class DiagramDetector:
    def __init__(self):
        # Configure Tesseract path if needed
        # pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
        pass
    
    def extract_diagrams(self, video_path, max_frames=50):
        """Extract diagrams from video frames"""
        diagrams = []
        
        # Open video
        cap = cv2.VideoCapture(video_path)
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        # Sample frames
        frame_indices = np.linspace(0, total_frames-1, min(max_frames, total_frames), dtype=int)
        
        for idx, frame_num in enumerate(frame_indices):
            cap.set(cv2.CAP_PROP_POS_FRAMES, frame_num)
            ret, frame = cap.read()
            
            if ret and self._is_diagram(frame):
                # Save diagram
                diagram_path = f"static/uploads/diagram_{idx}_{frame_num}.png"
                cv2.imwrite(diagram_path, frame)
                
                # Extract any text from diagram
                diagram_text = self._extract_text_from_image(frame)
                
                diagrams.append({
                    'path': diagram_path,
                    'caption': self._generate_caption(frame, diagram_text),
                    'text': diagram_text[:100] if diagram_text else '',
                    'frame': int(frame_num)
                })
        
        cap.release()
        return diagrams
    
    def _is_diagram(self, frame):
        """Detect if frame contains a diagram (not just talking head)"""
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Calculate edge density
        edges = cv2.Canny(gray, 50, 150)
        edge_density = np.sum(edges > 0) / edges.size
        
        # Calculate color variance
        color_variance = np.var(frame)
        
        # Diagrams typically have high edge density and moderate color variance
        if edge_density > 0.1 and color_variance > 1000:
            return True
        
        return False
    
    def _extract_text_from_image(self, image):
        """Extract text from diagram using OCR"""
        try:
            # Convert to PIL Image
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            pil_image = Image.fromarray(image)
            
            # Extract text
            text = pytesseract.image_to_string(pil_image)
            return text.strip()
        except:
            return ""
    
    def _generate_caption(self, frame, extracted_text):
        """Generate caption for diagram"""
        if extracted_text:
            # Use first line of extracted text
            first_line = extracted_text.split('\n')[0]
            if len(first_line) > 50:
                first_line = first_line[:50] + '...'
            return f"Diagram: {first_line}"
        
        return "Extracted Diagram"
    
    def detect_objects(self, image_path):
        """Detect objects in diagram (future enhancement)"""
        # Could implement YOLO or other object detection
        pass