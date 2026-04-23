# 🚀 QUICK START GUIDE

## 5-Minute Setup

### Option 1: Windows (Easiest)
1. **Double-click** `START.bat`
2. Wait for server to start
3. Open browser to: **http://127.0.0.1:5000**
4. Done! ✅

### Option 2: Manual Setup (Any OS)

#### Step 1: Install Python (if not already installed)
- Download from: https://www.python.org/
- Make sure to check "Add Python to PATH" during installation

#### Step 2: Navigate to Project Directory
```bash
cd "path/to/Sanchula Siva Jyothi"
```

#### Step 3: Install Dependencies
```bash
pip install Flask Flask-CORS python-docx reportlab
```

#### Step 4: Create Required Folders
```bash
mkdir -p uploads outputs/pdf outputs/docx static/temp
```

#### Step 5: Start Server
```bash
python app.py
```

#### Step 6: Open in Browser
```
http://127.0.0.1:5000
```

---

## 🎬 First Use - Step by Step

### 1️⃣ Select Difficulty Level
- Choose from: **Beginner**, **Intermediate**, or **Advanced**
- This affects the complexity of generated notes

### 2️⃣ Record Audio
- Click **"Start Recording"** button 🎤
- Speak clearly about any topic (10-60 seconds recommended)
- Click **"Stop Recording"** when done

### 3️⃣ Transcribe
- Click **"Transcribe Audio"** button
- Wait for AI to process (shows "Transcribing Audio with AI..." overlay)
- See transcribed text appear

### 4️⃣ View Generated Notes
- Notes automatically appear with:
  - 📖 Introduction
  - ⭐ Key Highlights
  - 📚 Learning Structure
  - 📝 Summary

### 5️⃣ Export Notes
Choose your format:
- **Preview** (HTML) - View in browser
- **PDF** - Download professional PDF
- **DOCX** - Download for Microsoft Word

### 6️⃣ Access History
- View all previously generated notes
- Download older files anytime

---

## 📱 Trying Different Topics

### Technology Topics (auto-detected)
- Python programming
- Java development
- Web development (HTML, CSS, JavaScript)
- Databases & SQL
- Machine Learning
- Cloud computing

### General Topics
Record anything! System adapts:
- History & Geography
- Science & Physics
- Languages & Literature
- Business & Economics

---

## ⚙️ Customization

### Change Difficulty Level Mid-Session
1. Click a different difficulty card at the top
2. Record new audio or upload a file
3. New notes generate with selected level

### Without Whisper AI (Demo Mode)
If Whisper isn't installed, app still works:
- Uses mock transcription for demo
- All export features work normally
- To enable real transcription: `pip install openai-whisper`

---

## 🆘 Common Issues

### Issue: Microphone not working
**Solution:**
- Check browser permissions
- Try uploading an audio file instead
- Use Chrome/Edge/Firefox (Firefox may require HTTPS)

### Issue: "Port 5000 already in use"
**Solution:**
```bash
# Change port in app.py (line with app.run)
app.run(debug=True, host='127.0.0.1', port=5001)  # Change 5000 to 5001
```

### Issue: Slow PDF/DOCX generation
**Solution:**
- This is normal on first run
- Subsequent generations are faster
- Closing browser tabs frees memory

### Issue: "Module not found" error
**Solution:**
```bash
pip install -r requirements.txt
```

---

## 📚 Understanding Note Levels

### When to use BEGINNER? 
- Learning something completely new
- Simplifying complex topics
- Teaching others

### When to use INTERMEDIATE?
- Most common choice
- Building on existing knowledge
- Professional reference

### When to use ADVANCED?
- Deep learning sessions
- Research purposes
- Academic study

---

## 💡 Tips & Tricks

1. **Use Complete Sentences**
   - Better results when you speak clearly and complete thoughts

2. **Test Topics**
   - Try: "Today I want to learn about Python programming"
   - Try: "Explain machine learning and neural networks"

3. **Download All Formats**
   - PDF for reading
   - DOCX for editing
   - HTML for sharing

4. **Save Important Notes**
   - Access History section always shows past files
   - Files persist even after closing app

5. **Check Generated Files**
   - PDFs are in: `outputs/pdf/`
   - DOCX files are in: `outputs/docx/`
   - Download directly from History tab

---

## 🎯 Feature Highlights

✅ **Audio Recording** - Built-in microphone support
✅ **AI Transcription** - OpenAI Whisper (optional)
✅ **Smart Generation** - Level-aware content
✅ **Multiple Export** - PDF, DOCX, HTML
✅ **File History** - Track all generated notes
✅ **Responsive UI** - Works on desktop & mobile
✅ **User Accounts** - Sign up + login (MongoDB)
✅ **Open Source** - Fully customizable

---

## 🔗 Keyboard Shortcuts

| Action | Shortcut |
|--------|----------|
| Start/Stop Recording | Spacebar (when focused) |
| Jump to PDF Export | Alt+P |
| Jump to DOCX Export | Alt+D |
| Jump to History | Alt+H |

---

## 🆕 What's New

### Version 1.0 Features:
- 3-Level difficulty system
- Audio recording & transcription
- PDF & DOCX generation
- HTML preview
- File history tracking
- Timestamp-based file naming
- Browser-based microphone support

---

## 📞 Support

If you encounter issues:

1. **Check README.md** for detailed documentation
2. **Review Troubleshooting section** in README
3. **Check Browser Console** (F12) for errors
4. **Look at Terminal Output** for Flask errors

---

## 🎓 Learning Resources

### AI & Machine Learning
- OpenAI Whisper: https://github.com/openai/whisper
- ReportLab: https://www.reportlab.com/

### Flask Framework
- Official Docs: https://flask.palletsprojects.com/
- Tutorials: https://realpython.com/flask-by-example/

### Web Development
- Bootstrap 5: https://getbootstrap.com/
- Font Awesome Icons: https://fontawesome.com/

---

## ✨ Examples

### Example 1: Learn Python
```
Record: "Python is a programming language. Let me explain..."
Level: Beginner
Result: Beginner-friendly Python notes with simple examples
```

### Example 2: Professional Reference
```
Record: "Advanced database optimization techniques..."
Level: Advanced
Result: Technical notes with performance considerations
```

### Example 3: Export for Review
```
Generate notes → Download PDF
Share with colleagues → Get feedback
Edit in Word → Update locally
```

---

## 💬 Feedback

This application is built to help you learn better. Let me know what features would be most helpful!

---

**Ready to start? Open http://127.0.0.1:5000 now!** 🚀
