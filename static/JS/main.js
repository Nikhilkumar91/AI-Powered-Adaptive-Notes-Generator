// Global variables
let selectedFile = null;
let processingInterval = null;

// DOM Elements
const uploadArea = document.getElementById('uploadArea');
const fileInput = document.getElementById('fileInput');
const fileInfo = document.getElementById('fileInfo');
const levelSelection = document.getElementById('levelSelection');
const loadingSection = document.getElementById('loadingSection');
const resultsPreview = document.getElementById('resultsPreview');
const processBtn = document.getElementById('processBtn');
const downloadBtn = document.getElementById('downloadPdfBtn');

// Event Listeners
uploadArea.addEventListener('click', () => fileInput.click());
uploadArea.addEventListener('dragover', handleDragOver);
uploadArea.addEventListener('drop', handleDrop);
fileInput.addEventListener('change', handleFileSelect);
processBtn.addEventListener('click', processLecture);
downloadBtn.addEventListener('click', downloadPDF);

// Handle drag over
function handleDragOver(e) {
    e.preventDefault();
    uploadArea.style.background = '#f0f3ff';
}

// Handle file drop
function handleDrop(e) {
    e.preventDefault();
    uploadArea.style.background = '';
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file selection
function handleFileSelect(e) {
    const files = e.target.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

// Handle file processing
function handleFile(file) {
    selectedFile = file;
    
    // Show file info
    fileInfo.innerHTML = `
        <i class="fas fa-check-circle"></i>
        Selected: ${file.name} (${(file.size / (1024*1024)).toFixed(2)} MB)
    `;
    fileInfo.style.display = 'block';
    
    // Show level selection
    levelSelection.style.display = 'block';
}

// Upload and process lecture
async function processLecture() {
    if (!selectedFile) {
        alert('Please select a file first');
        return;
    }
    
    const level = document.querySelector('input[name="level"]:checked').value;
    
    // Show loading
    levelSelection.style.display = 'none';
    loadingSection.style.display = 'block';
    
    // Create form data
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
        // Upload file
        const uploadResponse = await fetch('/upload', {
            method: 'POST',
            body: formData
        });
        
        const uploadResult = await uploadResponse.json();
        
        if (!uploadResult.success) {
            throw new Error(uploadResult.error);
        }
        
        // Process lecture
        const processResponse = await fetch('/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ level: level })
        });
        
        const processResult = await processResponse.json();
        
        if (!processResult.success) {
            throw new Error(processResult.error);
        }
        
        // Display preview
        displayPreview(processResult);
        
        // Hide loading, show results
        loadingSection.style.display = 'none';
        resultsPreview.style.display = 'block';
        
    } catch (error) {
        alert('Error: ' + error.message);
        loadingSection.style.display = 'none';
        levelSelection.style.display = 'block';
    }
}

// Display preview results
function displayPreview(data) {
    // Notes preview
    const notesPreview = document.getElementById('notesPreview');
    if (data.notes) {
        let notesHtml = '';
        
        if (data.notes.title) {
            notesHtml += `<h4>${data.notes.title}</h4>`;
        }
        
        if (data.notes.sections) {
            data.notes.sections.slice(0, 2).forEach(section => {
                notesHtml += `
                    <div class="preview-section">
                        <h5>${section.heading}</h5>
                        <p>${section.content}</p>
                    </div>
                `;
            });
        }
        
        notesPreview.innerHTML = notesHtml;
    }
    
    // Diagrams preview
    const diagramsPreview = document.getElementById('diagramsPreview');
    if (data.diagrams && data.diagrams.length > 0) {
        let diagramsHtml = '';
        data.diagrams.forEach(diagram => {
            diagramsHtml += `
                <div class="diagram-thumb">
                    <img src="/${diagram.path}" alt="Diagram">
                    <p>${diagram.caption}</p>
                </div>
            `;
        });
        diagramsPreview.innerHTML = diagramsHtml;
    } else {
        diagramsPreview.innerHTML = '<p>No diagrams detected in this lecture.</p>';
    }
    
    // Quiz preview
    const quizPreview = document.getElementById('quizPreview');
    if (data.quiz && data.quiz.length > 0) {
        let quizHtml = '';
        data.quiz.forEach((q, index) => {
            quizHtml += `
                <div class="quiz-question-preview">
                    <p><strong>Q${index + 1}:</strong> ${q.question}</p>
                    <ul>
                        ${q.options.map(opt => `<li>${opt}</li>`).join('')}
                    </ul>
                </div>
            `;
        });
        quizPreview.innerHTML = quizHtml;
    }
}

// Download PDF
async function downloadPDF() {
    try {
        const response = await fetch('/download_pdf');
        const blob = await response.blob();
        
        // Create download link
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'lecture_notes.pdf';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        window.URL.revokeObjectURL(url);
    } catch (error) {
        alert('Error downloading PDF: ' + error.message);
    }
}

// Reset session
async function resetSession() {
    await fetch('/reset');
    location.reload();
}