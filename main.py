from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse, JSONResponse
from groq import Groq
import uvicorn
import re
from datetime import datetime

app = FastAPI()
client = Groq(api_key="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")

# -----------------------------
# Helper: Improve and structure the input prompt
# -----------------------------
def clean_prompt(raw_prompt: str, tone: str, use_case: str) -> str:
    """
    Cleans and structures the user input for detailed AI prompt generation.
    """
    cleaned = re.sub(r"[\n\r\t]+", " ", raw_prompt.strip())
    cleaned = re.sub(r"\s{2,}", " ", cleaned)

    tone_instructions = {
        "expert": "Use professional, technical language with deep expertise and industry-specific terminology.",
        "casual": "Use friendly, conversational language that's easy to understand and approachable.",
        "formal": "Use professional, polished language suitable for business or academic contexts.",
        "creative": "Use imaginative, engaging language with vivid descriptions and creative flair.",
        "marketing": "Use persuasive, action-oriented language focused on benefits and conversions."
    }

    use_case_instructions = {
        "general": "",
        "content_writing": "Focus on SEO optimization, readability, and engaging storytelling.",
        "email": "Include subject line suggestions, clear call-to-action, and professional email structure.",
        "code": "Specify programming language, best practices, error handling, and code documentation.",
        "social_media": "Include hashtag suggestions, character limits, and platform-specific formatting.",
        "business": "Focus on ROI, stakeholder communication, and professional business language."
    }

    formatted_prompt = (
        f"You are an expert AI prompt engineer. "
        f"Convert the user's request into a detailed, structured, and clear AI prompt. "
        f"The prompt should be in a {tone} tone. {tone_instructions.get(tone, '')}\n\n"
        f"Use Case: {use_case}. {use_case_instructions.get(use_case, '')}\n\n"
        f"Structure the output with clear sections using these exact formats:\n"
        f"- Use **bold text** for all section headings and key terms\n"
        f"- Use bullet points for lists\n"
        f"- Include: **Prompt Goal**, **Specific Requirements**, **Expected Output Format**, **Constraints**\n\n"
        f"User request: {cleaned}\n\n"
        f"Now create a professional, well-structured prompt:"
    )
    return formatted_prompt


# -----------------------------
# API Endpoint for AJAX requests
# -----------------------------
@app.post("/api/generate")
async def generate_prompt_api(request: Request):
    try:
        data = await request.json()
        raw_prompt = data.get("raw_prompt", "")
        tone = data.get("tone", "expert")
        use_case = data.get("use_case", "general")
        
        if not raw_prompt.strip():
            return JSONResponse({"error": "Please enter a prompt"}, status_code=400)
        
        structured_prompt = clean_prompt(raw_prompt, tone, use_case)

        completion = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": (
                    "You are a professional AI prompt engineer. "
                    "Generate optimized, detailed prompts with clear structure. "
                    "ALWAYS use **bold text** for headings and important terms. "
                    "Format your response with clear sections and bullet points."
                )},
                {"role": "user", "content": structured_prompt}
            ],
            temperature=0.8,
            max_tokens=1024,
            top_p=1,
            stream=False
        )

        generated_text = completion.choices[0].message.content.strip()
        
        return JSONResponse({
            "success": True,
            "generated_prompt": generated_text,
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        })

    except Exception as e:
        return JSONResponse({"error": str(e)}, status_code=500)


# -----------------------------
# Landing Page with Modern UI
# -----------------------------
@app.get("/", response_class=HTMLResponse)
async def home():
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>AI Prompt Generator Pro</title>
        <style>
            * {
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }

            body {
                font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
                background: linear-gradient(135deg, #1e3c72 0%, #2a5298 50%, #7e22ce 100%);
                min-height: 100vh;
                padding: 20px;
                color: #333;
            }

            .container {
                max-width: 1400px;
                margin: 0 auto;
            }

            header {
                text-align: center;
                color: white;
                margin-bottom: 50px;
                animation: fadeInDown 0.8s ease;
            }

            header h1 {
                font-size: 3.5em;
                font-weight: 800;
                margin-bottom: 15px;
                text-shadow: 3px 3px 6px rgba(0,0,0,0.3);
                background: linear-gradient(45deg, #fff, #a78bfa);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
            }

            header p {
                font-size: 1.3em;
                opacity: 0.95;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            }

            .main-grid {
                display: grid;
                grid-template-columns: 400px 1fr;
                gap: 30px;
                animation: fadeInUp 0.8s ease;
            }

            .sidebar {
                display: flex;
                flex-direction: column;
                gap: 20px;
            }

            .card {
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(10px);
                border-radius: 24px;
                padding: 30px;
                box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                transition: transform 0.3s ease, box-shadow 0.3s ease;
            }

            .card:hover {
                transform: translateY(-5px);
                box-shadow: 0 25px 70px rgba(0,0,0,0.4);
            }

            .card h2 {
                color: #1e3c72;
                margin-bottom: 20px;
                font-size: 1.4em;
                display: flex;
                align-items: center;
                gap: 10px;
                font-weight: 700;
            }

            .icon {
                font-size: 1.5em;
            }

            .form-group {
                margin-bottom: 20px;
            }

            .form-group label {
                display: block;
                margin-bottom: 8px;
                color: #1e3c72;
                font-weight: 600;
                font-size: 14px;
            }

            textarea {
                width: 100%;
                min-height: 180px;
                padding: 15px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 15px;
                font-family: inherit;
                resize: vertical;
                transition: all 0.3s ease;
            }

            textarea:focus {
                outline: none;
                border-color: #7e22ce;
                box-shadow: 0 0 0 3px rgba(126, 34, 206, 0.1);
            }

            select {
                width: 100%;
                padding: 12px 15px;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                font-size: 15px;
                font-family: inherit;
                background: white;
                cursor: pointer;
                transition: all 0.3s ease;
                appearance: none;
                background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='12' height='12' viewBox='0 0 12 12'%3E%3Cpath fill='%231e3c72' d='M6 9L1 4h10z'/%3E%3C/svg%3E");
                background-repeat: no-repeat;
                background-position: right 15px center;
                padding-right: 40px;
            }

            select:focus {
                outline: none;
                border-color: #7e22ce;
                box-shadow: 0 0 0 3px rgba(126, 34, 206, 0.1);
            }

            button {
                width: 100%;
                padding: 16px 30px;
                border: none;
                border-radius: 12px;
                font-size: 16px;
                font-weight: 700;
                cursor: pointer;
                transition: all 0.3s ease;
                display: flex;
                align-items: center;
                justify-content: center;
                gap: 10px;
                text-transform: uppercase;
                letter-spacing: 0.5px;
            }

            .btn-primary {
                background: linear-gradient(135deg, #7e22ce 0%, #1e3c72 100%);
                color: white;
                box-shadow: 0 4px 15px rgba(126, 34, 206, 0.4);
            }

            .btn-primary:hover:not(:disabled) {
                transform: translateY(-2px);
                box-shadow: 0 8px 25px rgba(126, 34, 206, 0.5);
            }

            .btn-primary:disabled {
                opacity: 0.6;
                cursor: not-allowed;
                transform: none;
            }

            .btn-secondary {
                background: #f3f4f6;
                color: #1e3c72;
                margin-top: 10px;
            }

            .btn-secondary:hover {
                background: #e5e7eb;
            }

            .output-card {
                position: relative;
                min-height: 600px;
            }

            .output-header {
                display: flex;
                justify-content: space-between;
                align-items: center;
                margin-bottom: 20px;
            }

            .output-content {
                background: #f9fafb;
                border-radius: 16px;
                padding: 25px;
                min-height: 500px;
                line-height: 1.8;
                border: 2px dashed #e5e7eb;
                color: #9ca3af;
                font-size: 15px;
            }

            .output-content.has-content {
                border: 2px solid #7e22ce;
                color: #1f2937;
                background: white;
            }

            /* Markdown-style formatting for output */
            .output-content.has-content {
                white-space: pre-wrap;
            }

            .copy-btn {
                padding: 10px 20px;
                background: #7e22ce;
                color: white;
                border: none;
                border-radius: 10px;
                cursor: pointer;
                font-size: 14px;
                font-weight: 600;
                display: none;
                align-items: center;
                gap: 8px;
                transition: all 0.3s ease;
            }

            .copy-btn:hover {
                background: #6b21a8;
                transform: translateY(-2px);
            }

            .copy-btn.show {
                display: flex;
            }

            .copy-btn.copied {
                background: #10b981;
            }

            .loader {
                border: 3px solid #f3f3f3;
                border-top: 3px solid #7e22ce;
                border-radius: 50%;
                width: 20px;
                height: 20px;
                animation: spin 1s linear infinite;
            }

            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }

            @keyframes fadeInDown {
                from {
                    opacity: 0;
                    transform: translateY(-30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            @keyframes fadeInUp {
                from {
                    opacity: 0;
                    transform: translateY(30px);
                }
                to {
                    opacity: 1;
                    transform: translateY(0);
                }
            }

            .features {
                margin-top: 40px;
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(280px, 1fr));
                gap: 25px;
            }

            .feature-card {
                background: rgba(255, 255, 255, 0.15);
                backdrop-filter: blur(10px);
                padding: 25px;
                border-radius: 20px;
                color: white;
                text-align: center;
                border: 1px solid rgba(255, 255, 255, 0.2);
                transition: all 0.3s ease;
            }

            .feature-card:hover {
                background: rgba(255, 255, 255, 0.25);
                transform: translateY(-5px);
            }

            .feature-card .icon {
                font-size: 3em;
                margin-bottom: 15px;
            }

            .feature-card h3 {
                margin-bottom: 10px;
                font-size: 1.2em;
            }

            .alert {
                padding: 15px 20px;
                border-radius: 12px;
                margin-top: 15px;
                display: none;
                font-weight: 500;
            }

            .alert.error {
                background: #fee;
                color: #c81e1e;
                border: 2px solid #fca5a5;
            }

            .alert.success {
                background: #ecfdf5;
                color: #047857;
                border: 2px solid #6ee7b7;
            }

            .alert.show {
                display: block;
                animation: fadeInUp 0.5s ease;
            }

            .example-tags {
                display: flex;
                flex-wrap: wrap;
                gap: 8px;
                margin-top: 10px;
            }

            .tag {
                background: #e0e7ff;
                color: #4338ca;
                padding: 6px 12px;
                border-radius: 20px;
                font-size: 12px;
                font-weight: 600;
                cursor: pointer;
                transition: all 0.3s ease;
            }

            .tag:hover {
                background: #4338ca;
                color: white;
                transform: translateY(-2px);
            }

            /* Footer Styles */
            footer {
                margin-top: 60px;
                padding: 30px 20px;
                background: rgba(255, 255, 255, 0.1);
                backdrop-filter: blur(10px);
                border-radius: 24px;
                border: 1px solid rgba(255, 255, 255, 0.2);
                text-align: center;
                animation: fadeInUp 1s ease;
            }

            .footer-content {
                display: flex;
                flex-direction: column;
                align-items: center;
                gap: 15px;
                color: white;
            }

            .footer-text {
                font-size: 1.1em;
                font-weight: 500;
                display: flex;
                align-items: center;
                gap: 8px;
                text-shadow: 1px 1px 3px rgba(0,0,0,0.2);
            }

            .footer-name {
                font-size: 1.3em;
                font-weight: 700;
                background: linear-gradient(45deg, #fff, #a78bfa, #fbbf24);
                -webkit-background-clip: text;
                -webkit-text-fill-color: transparent;
                background-clip: text;
                letter-spacing: 1px;
            }

            .footer-heart {
                display: inline-block;
                color: #ef4444;
                animation: heartbeat 1.5s ease-in-out infinite;
                font-size: 1.2em;
            }

            @keyframes heartbeat {
                0%, 100% { transform: scale(1); }
                25% { transform: scale(1.1); }
                50% { transform: scale(1); }
            }

            .footer-year {
                font-size: 0.9em;
                opacity: 0.85;
            }

            @media (max-width: 1024px) {
                .main-grid {
                    grid-template-columns: 1fr;
                }

                header h1 {
                    font-size: 2.5em;
                }
            }
        </style>
    </head>
    <body>
        <div class="container">
            <header>
                <h1>🚀 AI Prompt Generator Pro</h1>
                <p>Transform simple ideas into powerful, structured AI prompts with advanced customization</p>
            </header>

            <div class="main-grid">
                <div class="sidebar">
                    <div class="card">
                        <h2><span class="icon">✍️</span> Your Input</h2>
                        <div class="form-group">
                            <label for="rawPrompt">Describe your task or idea</label>
                            <textarea 
                                id="rawPrompt" 
                                placeholder="Example: Write a blog post about sustainable living..."
                            ></textarea>
                        </div>
                        <div class="example-tags">
                            <div class="tag" onclick="fillExample('blog')">📝 Blog Post</div>
                            <div class="tag" onclick="fillExample('email')">✉️ Email</div>
                            <div class="tag" onclick="fillExample('social')">📱 Social Media</div>
                        </div>
                    </div>

                    <div class="card">
                        <h2><span class="icon">⚙️</span> Customization</h2>
                        <div class="form-group">
                            <label for="toneSelect">Tone / Expertise Level</label>
                            <select id="toneSelect">
                                <option value="expert">Expert - Technical & Professional</option>
                                <option value="casual">Casual - Friendly & Conversational</option>
                                <option value="formal">Formal - Business & Academic</option>
                                <option value="creative">Creative - Imaginative & Engaging</option>
                                <option value="marketing">Marketing - Persuasive & Action-Oriented</option>
                            </select>
                        </div>

                        <div class="form-group">
                            <label for="useCaseSelect">Use Case / Content Type</label>
                            <select id="useCaseSelect">
                                <option value="general">General Purpose</option>
                                <option value="content_writing">Content Writing / Blogging</option>
                                <option value="email">Email Communication</option>
                                <option value="code">Code / Programming</option>
                                <option value="social_media">Social Media Posts</option>
                                <option value="business">Business / Professional</option>
                            </select>
                        </div>

                        <button class="btn-primary" id="generateBtn" onclick="generatePrompt()">
                            <span id="btnText">✨ Generate Prompt</span>
                            <div id="btnLoader" class="loader" style="display: none;"></div>
                        </button>
                        <button class="btn-secondary" onclick="clearAll()">
                            🗑️ Clear All
                        </button>
                        <div id="alertBox" class="alert"></div>
                    </div>
                </div>

                <div class="card output-card">
                    <div class="output-header">
                        <h2><span class="icon">✨</span> Generated Prompt</h2>
                        <button class="copy-btn" id="copyBtn" onclick="copyToClipboard()">
                            <span id="copyIcon">📋</span>
                            <span id="copyText">Copy</span>
                        </button>
                    </div>
                    <div id="output" class="output-content">
                        Your enhanced, structured prompt will appear here...
                        
                        Tips:
                        • Select your preferred tone and use case
                        • Be specific about your requirements
                        • Try the example tags for quick start
                        • Press Ctrl+Enter to generate
                    </div>
                </div>
            </div>

            <div class="features">
                <div class="feature-card">
                    <div class="icon">🎯</div>
                    <h3>Multi-Level Expertise</h3>
                    <p>Generate prompts from casual to expert level with tailored language</p>
                </div>
                <div class="feature-card">
                    <div class="icon">🎨</div>
                    <h3>Rich Formatting</h3>
                    <p>Get well-structured outputs with bold headings and clear sections</p>
                </div>
                <div class="feature-card">
                    <div class="icon">📧</div>
                    <h3>Use Case Specific</h3>
                    <p>Optimized for emails, blogs, code, social media, and more</p>
                </div>
                <div class="feature-card">
                    <div class="icon">⚡</div>
                    <h3>Lightning Fast</h3>
                    <p>Generate professional prompts in seconds with AI power</p>
                </div>
            </div>

            <footer>
                <div class="footer-content">
                    <div class="footer-text">
                        Built with <span class="footer-heart">❤️</span> by
                    </div>
                    <div class="footer-name">Vinita Pandla</div>
                    <div class="footer-year">© 2025 AI Prompt Generator Pro</div>
                </div>
            </footer>
        </div>

        <script>
            function formatMarkdown(text) {
                // Convert **bold** to HTML bold
                text = text.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
                // Convert bullet points
                text = text.replace(/^- (.+)$/gm, '• $1');
                return text;
            }

            async function generatePrompt() {
                const rawPrompt = document.getElementById('rawPrompt').value.trim();
                const tone = document.getElementById('toneSelect').value;
                const useCase = document.getElementById('useCaseSelect').value;
                const generateBtn = document.getElementById('generateBtn');
                const btnText = document.getElementById('btnText');
                const btnLoader = document.getElementById('btnLoader');
                const output = document.getElementById('output');
                const copyBtn = document.getElementById('copyBtn');
                const alertBox = document.getElementById('alertBox');

                if (!rawPrompt) {
                    showAlert('Please enter a prompt to generate', 'error');
                    return;
                }

                generateBtn.disabled = true;
                btnText.textContent = '⏳ Generating...';
                btnLoader.style.display = 'block';
                output.innerHTML = '<div style="text-align: center; padding: 50px; color: #7e22ce;">Processing your request...</div>';
                output.classList.remove('has-content');
                copyBtn.classList.remove('show');
                hideAlert();

                try {
                    const response = await fetch('/api/generate', {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        body: JSON.stringify({ 
                            raw_prompt: rawPrompt,
                            tone: tone,
                            use_case: useCase
                        })
                    });

                    const data = await response.json();

                    if (data.success) {
                        // Format the output with proper markdown
                        const formatted = formatMarkdown(data.generated_prompt);
                        output.innerHTML = formatted;
                        output.classList.add('has-content');
                        copyBtn.classList.add('show');
                        showAlert('✅ Prompt generated successfully!', 'success');
                    } else {
                        output.innerHTML = '<div style="color: #ef4444;">Error: ' + (data.error || 'Failed to generate prompt') + '</div>';
                        showAlert(data.error || 'Failed to generate prompt', 'error');
                    }
                } catch (error) {
                    output.innerHTML = '<div style="color: #ef4444;">Error: ' + error.message + '</div>';
                    showAlert('Network error. Please try again.', 'error');
                } finally {
                    generateBtn.disabled = false;
                    btnText.textContent = '✨ Generate Prompt';
                    btnLoader.style.display = 'none';
                }
            }

            function copyToClipboard() {
                const output = document.getElementById('output');
                const copyBtn = document.getElementById('copyBtn');
                const copyIcon = document.getElementById('copyIcon');
                const copyText = document.getElementById('copyText');
                
                // Get text content without HTML
                const textContent = output.innerText || output.textContent;
                
                navigator.clipboard.writeText(textContent).then(() => {
                    copyBtn.classList.add('copied');
                    copyIcon.textContent = '✅';
                    copyText.textContent = 'Copied!';
                    
                    setTimeout(() => {
                        copyBtn.classList.remove('copied');
                        copyIcon.textContent = '📋';
                        copyText.textContent = 'Copy';
                    }, 2000);
                });
            }

            function clearAll() {
                document.getElementById('rawPrompt').value = '';
                document.getElementById('output').innerHTML = `Your enhanced, structured prompt will appear here...
                        
                        Tips:
                        • Select your preferred tone and use case
                        • Be specific about your requirements
                        • Try the example tags for quick start
                        • Press Ctrl+Enter to generate`;
                document.getElementById('output').classList.remove('has-content');
                document.getElementById('copyBtn').classList.remove('show');
                document.getElementById('toneSelect').value = 'expert';
                document.getElementById('useCaseSelect').value = 'general';
                hideAlert();
            }

            function fillExample(type) {
                const examples = {
                    'blog': 'Write a comprehensive blog post about sustainable living practices that individuals can adopt in 2025',
                    'email': 'Create a professional email to follow up with a potential client after a business meeting',
                    'social': 'Generate engaging Instagram captions for a new product launch in the tech industry'
                };
                document.getElementById('rawPrompt').value = examples[type];
            }

            function showAlert(message, type) {
                const alertBox = document.getElementById('alertBox');
                alertBox.textContent = message;
                alertBox.className = `alert ${type} show`;
            }

            function hideAlert() {
                const alertBox = document.getElementById('alertBox');
                alertBox.classList.remove('show');
            }

            document.getElementById('rawPrompt').addEventListener('keydown', function(e) {
                if (e.ctrlKey && e.key === 'Enter') {
                    generatePrompt();
                }
            });
        </script>
    </body>
    </html>
    """
    return HTMLResponse(content=html_content)


# if __name__ == "__main__":
#     uvicorn.run(app, host="127.0.0.1", port=8000)
