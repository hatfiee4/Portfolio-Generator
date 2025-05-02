from flask import Flask, request, render_template_string
import os
import logging

app = Flask(__name__)

# Set up logging for debugging
logging.basicConfig(level=logging.DEBUG)

# HTML form with dynamic project fields, styles panel, and preview
FORM_TEMPLATE = '''
<!DOCTYPE html>
<html>
<head>
    <title>Portfolio Generator</title>
    <style>
        body {
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            background-color: #f4f4f9;
        }
        h1 {
            color: #333;
            text-align: center;
        }
        .main-container {
            display: flex;
            gap: 20px;
            flex-wrap: wrap;
        }
        .form-container, .preview-container {
            flex: 1;
            min-width: 300px;
        }
        form {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        label {
            display: block;
            margin: 10px 0 5px;
            font-weight: bold;
        }
        input[type="text"], textarea, input[type="number"] {
            width: 100%;
            padding: 8px;
            margin-bottom: 10px;
            border: 1px solid #ccc;
            border-radius: 4px;
            box-sizing: border-box;
        }
        textarea {
            height: 100px;
            resize: vertical;
        }
        input[type="submit"], button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 20px;
            border: none;
            border-radius: 4px;
            cursor: pointer;
            font-size: 16px;
            margin: 10px 5px 0 0;
        }
        input[type="submit"]:hover, button:hover {
            background-color: #45a049;
        }
        .error {
            color: red;
            text-align: center;
        }
        .project-field {
            border: 1px solid #eee;
            padding: 10px;
            margin-bottom: 10px;
            border-radius: 4px;
        }
        .remove-project {
            background-color: #e74c3c;
        }
        .remove-project:hover {
            background-color: #c0392b;
        }
        .styles-panel {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-top: 20px;
        }
        .styles-panel label {
            display: block;
            margin: 10px 0 5px;
            font-weight: bold;
        }
        .styles-panel input[type="color"] {
            width: 100%;
            height: 40px;
            border: none;
            cursor: pointer;
        }
        .styles-panel input[type="number"] {
            width: 100px;
        }
        .preview-container {
            background: white;
            padding: 20px;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        }
        .preview-container iframe {
            width: 100%;
            height: 600px;
            border: none;
            border-radius: 4px;
        }
        @media (max-width: 800px) {
            .main-container {
                flex-direction: column;
            }
        }
    </style>
    <script>
        function addProject() {
            const container = document.getElementById('projects-container');
            const index = container.children.length;
            const projectDiv = document.createElement('div');
            projectDiv.className = 'project-field';
            projectDiv.innerHTML = `
                <label for="project_title_${index}">Project Title:</label>
                <input type="text" name="project_titles[]" id="project_title_${index}" required oninput="updatePreview()">
                <label for="project_description_${index}">Project Description:</label>
                <textarea name="project_descriptions[]" id="project_description_${index}" required oninput="updatePreview()"></textarea>
                <label for="project_links_${index}">Links (e.g., GitHub: https://github.com/user/repo, Demo: https://app.com):</label>
                <input type="text" name="project_links[]" id="project_links_${index}" oninput="updatePreview()">
                <button type="button" class="remove-project" onclick="this.parentElement.remove(); updatePreview()">Remove Project</button>
            `;
            container.appendChild(projectDiv);
            updatePreview();
        }

        function escapeHtml(unsafe) {
            return unsafe
                .replace(/&/g, "&amp;")
                .replace(/</g, "&lt;")
                .replace(/>/g, "&gt;")
                .replace(/"/g, "&quot;")
                .replace(/'/g, "&#039;");
        }

        function updatePreview() {
            try {
                const portfolioTitle = escapeHtml(document.getElementById('portfolio_title').value || 'Your Portfolio');
                const name = escapeHtml(document.getElementById('name').value || 'Your Name');
                const skills = document.getElementById('skills').value;
                const projectTitles = Array.from(document.getElementsByName('project_titles[]')).map(input => escapeHtml(input.value)).filter(title => title.trim());
                const projectDescriptions = Array.from(document.getElementsByName('project_descriptions[]')).map(input => escapeHtml(input.value));
                const projectLinks = Array.from(document.getElementsByName('project_links[]')).map(input => input.value);
                const headerColor = document.getElementById('header-color').value;
                const footerColor = document.getElementById('footer-color').value;
                const textColor = document.getElementById('text-color').value;
                const backgroundColor = document.getElementById('background-color').value;
                const titleColor = document.getElementById('title-color').value;
                const createdByColor = document.getElementById('created-by-color').value;
                const footerTextColor = document.getElementById('footer-text-color').value;
                const titleSize = document.getElementById('title-size').value || '40';
                const createdBySize = document.getElementById('created-by-size').value || '19';
                const textSize = document.getElementById('text-size').value || '16';
                const skillsSize = document.getElementById('skills-size').value || '14';
                const projectsSize = document.getElementById('projects-size').value || '20';
                const footerSize = document.getElementById('footer-size').value || '16';

                // Sync color and size values to hidden inputs
                document.getElementById('header-color-hidden').value = headerColor;
                document.getElementById('footer-color-hidden').value = footerColor;
                document.getElementById('text-color-hidden').value = textColor;
                document.getElementById('background-color-hidden').value = backgroundColor;
                document.getElementById('title-color-hidden').value = titleColor;
                document.getElementById('created-by-color-hidden').value = createdByColor;
                document.getElementById('footer-text-color-hidden').value = footerTextColor;
                document.getElementById('title-size-hidden').value = titleSize;
                document.getElementById('created-by-size-hidden').value = createdBySize;
                document.getElementById('text-size-hidden').value = textSize;
                document.getElementById('skills-size-hidden').value = skillsSize;
                document.getElementById('projects-size-hidden').value = projectsSize;
                document.getElementById('footer-size-hidden').value = footerSize;

                const projects = projectTitles.map((title, i) => {
                    const links = projectLinks[i] ? projectLinks[i].split(',').map(link => {
                        link = link.trim();
                        if (link.includes(':')) {
                            const [name, url] = link.split(':', 2).map(s => s.trim());
                            return name && url ? { name: escapeHtml(name), url: escapeHtml(url) } : null;
                        }
                        return null;
                    }).filter(link => link) : [];
                    return { title, description: projectDescriptions[i] || '', links };
                });

                const skillsList = skills.split(',').map(skill => escapeHtml(skill.trim())).filter(skill => skill);

                const template = `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${portfolioTitle}</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: ${backgroundColor};
            color: ${textColor};
            font-size: ${textSize}px;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: ${headerColor};
            color: white;
            text-align: center;
            padding: 20px;
            width: 100%;
        }
        header h1 {
            margin: 0;
            font-size: ${titleSize}px;
            color: ${titleColor};
        }
        header p {
            font-size: ${createdBySize}px;
            margin: 10px 0;
            color: ${createdByColor};
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 0 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .projects h2, .skills h2 {
            color: ${textColor};
            margin: 20px 0;
            font-size: ${projectsSize}px;
        }
        .project {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            font-size: ${projectsSize}px;
        }
        .project h3 {
            color: ${textColor};
            margin-top: 0;
            font-size: ${parseInt(projectsSize) + 8}px;
        }
        .project-links {
            margin-top: 10px;
        }
        .project-links ul {
            list-style: none;
            padding: 0;
        }
        .project-links li {
            margin: 5px 0;
        }
        .project-links a {
            color: #3498db;
            text-decoration: none;
        }
        .project-links a:hover {
            text-decoration: underline;
        }
        .skills {
            margin: 20px 0;
        }
        .skills ul {
            list-style: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .skills li {
            background: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 15px;
            font-size: ${skillsSize}px;
        }
        footer {
            text-align: center;
            padding: 20px;
            background: ${footerColor};
            color: ${footerTextColor};
            width: 100%;
            font-size: ${footerSize}px;
        }
        @media (max-width: 600px) {
            header h1 {
                font-size: ${parseInt(titleSize) * 0.72}px;
            }
            .container {
                padding: 0 10px;
            }
            .project h3 {
                font-size: ${parseInt(projectsSize) * 0.8 + 8}px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>${portfolioTitle}</h1>
        <p>Created by ${name}</p>
    </header>
    <div class="container">
        <div class="projects">
            <h2>Projects</h2>
            ${projects.length ? projects.map(project => `
                <div class="project">
                    <h3>${project.title}</h3>
                    <p>${project.description}</p>
                    ${project.links.length ? `
                        <div class="project-links">
                            <ul>
                                ${project.links.map(link => `<li><a href="${link.url}" target="_blank">${link.name}</a></li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `).join('') : '<p>No projects added yet.</p>'}
        </div>
        <div class="skills">
            <h2>Skills</h2>
            <ul>
                ${skillsList.length ? skillsList.map(skill => `<li>${skill}</li>`).join('') : '<li>No skills added yet.</li>'}
            </ul>
        </div>
    </div>
    <footer>
        <p>© ${name} ${new Date().getFullYear()}. All rights reserved.</p>
    </footer>
</body>
</html>`;

                const iframe = document.getElementById('preview-iframe');
                iframe.srcdoc = template;
                console.log('Preview updated successfully');
            } catch (error) {
                console.error('Error updating preview:', error);
            }
        }

        // Initialize preview on page load
        window.onload = function() {
            try {
                updatePreview();
                console.log('Initial preview loaded');
            } catch (error) {
                console.error('Error initializing preview:', error);
            }
        };
    </script>
</head>
<body>
    <h1>Portfolio Generator</h1>
    {% if error %}
        <p class="error">{{ error }}</p>
    {% endif %}
    <div class="main-container">
        <div class="form-container">
            <form method="POST" action="/generate">
                <label for="portfolio_title">Portfolio Title:</label>
                <input type="text" name="portfolio_title" id="portfolio_title" required oninput="updatePreview()">

                <label for="name">Your Name:</label>
                <input type="text" name="name" id="name" required oninput="updatePreview()">

                <label for="skills">Skills (comma-separated, e.g., Python, JavaScript):</label>
                <input type="text" name="skills" id="skills" required oninput="updatePreview()">

                <div id="projects-container">
                    <div class="project-field">
                        <label for="project_title_0">Project Title:</label>
                        <input type="text" name="project_titles[]" id="project_title_0" required oninput="updatePreview()">
                        <label for="project_description_0">Project Description:</label>
                        <textarea name="project_descriptions[]" id="project_description_0" required oninput="updatePreview()"></textarea>
                        <label for="project_links_0">Links (e.g., GitHub: https://github.com/user/repo, Demo: https://app.com):</label>
                        <input type="text" name="project_links[]" id="project_links_0" oninput="updatePreview()">
                    </div>
                </div>
                <button type="button" onclick="addProject()">Add Project</button>
                <input type="submit" value="Generate Portfolio">
                <input type="hidden" name="header_color" id="header-color-hidden">
                <input type="hidden" name="footer_color" id="footer-color-hidden">
                <input type="hidden" name="text_color" id="text-color-hidden">
                <input type="hidden" name="background_color" id="background-color-hidden">
                <input type="hidden" name="title_color" id="title-color-hidden">
                <input type="hidden" name="created_by_color" id="created-by-color-hidden">
                <input type="hidden" name="footer_text_color" id="footer-text-color-hidden">
                <input type="hidden" name="title_size" id="title-size-hidden">
                <input type="hidden" name="created_by_size" id="created-by-size-hidden">
                <input type="hidden" name="text_size" id="text-size-hidden">
                <input type="hidden" name="skills_size" id="skills-size-hidden">
                <input type="hidden" name="projects_size" id="projects-size-hidden">
                <input type="hidden" name="footer_size" id="footer-size-hidden">
            </form>
            <div class="styles-panel">
                <label for="header-color">Header Background Color:</label>
                <input type="color" id="header-color" value="#2c3e50" oninput="updatePreview(); document.getElementById('header-color-hidden').value = this.value">
                <label for="footer-color">Footer Background Color:</label>
                <input type="color" id="footer-color" value="#2c3e50" oninput="updatePreview(); document.getElementById('footer-color-hidden').value = this.value">
                <label for="text-color">Body Text Color:</label>
                <input type="color" id="text-color" value="#333333" oninput="updatePreview(); document.getElementById('text-color-hidden').value = this.value">
                <label for="background-color">Background Color:</label>
                <input type="color" id="background-color" value="#f4f4f9" oninput="updatePreview(); document.getElementById('background-color-hidden').value = this.value">
                <label for="title-color">Title Color:</label>
                <input type="color" id="title-color" value="#ffffff" oninput="updatePreview(); document.getElementById('title-color-hidden').value = this.value">
                <label for="created-by-color">Created By Color:</label>
                <input type="color" id="created-by-color" value="#ffffff" oninput="updatePreview(); document.getElementById('created-by-color-hidden').value = this.value">
                <label for="footer-text-color">Footer Text Color:</label>
                <input type="color" id="footer-text-color" value="#ffffff" oninput="updatePreview(); document.getElementById('footer-text-color-hidden').value = this.value">
                <label for="title-size">Title Font Size (px):</label>
                <input type="number" id="title-size" value="40" min="10" max="100" oninput="updatePreview(); document.getElementById('title-size-hidden').value = this.value">
                <label for="created-by-size">Created By Font Size (px):</label>
                <input type="number" id="created-by-size" value="19" min="10" max="50" oninput="updatePreview(); document.getElementById('created-by-size-hidden').value = this.value">
                <label for="text-size">Body Text Font Size (px):</label>
                <input type="number" id="text-size" value="16" min="10" max="30" oninput="updatePreview(); document.getElementById('text-size-hidden').value = this.value">
                <label for="skills-size">Skills Font Size (px):</label>
                <input type="number" id="skills-size" value="14" min="10" max="30" oninput="updatePreview(); document.getElementById('skills-size-hidden').value = this.value">
                <label for="projects-size">Projects Font Size (px):</label>
                <input type="number" id="projects-size" value="20" min="10" max="40" oninput="updatePreview(); document.getElementById('projects-size-hidden').value = this.value">
                <label for="footer-size">Footer Font Size (px):</label>
                <input type="number" id="footer-size" value="16" min="10" max="30" oninput="updatePreview(); document.getElementById('footer-size-hidden').value = this.value">
            </div>
        </div>
        <div class="preview-container">
            <h2>Preview</h2>
            <iframe id="preview-iframe" sandbox="allow-same-origin"></iframe>
        </div>
    </div>
</body>
</html>
'''

# Template for the generated portfolio
PORTFOLIO_TEMPLATE = '''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{{ portfolio_title }}</title>
    <style>
        body {
            font-family: 'Segoe UI', Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: {{ background_color }};
            color: {{ text_color }};
            font-size: {{ text_size }}px;
            line-height: 1.6;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }
        header {
            background: {{ header_color }};
            color: white;
            text-align: center;
            padding: 20px;
            width: 100%;
        }
        header h1 {
            margin: 0;
            font-size: {{ title_size }}px;
            color: {{ title_color }};
        }
        header p {
            font-size: {{ created_by_size }}px;
            margin: 10px 0;
            color: {{ created_by_color }};
        }
        .container {
            max-width: 900px;
            margin: 20px auto;
            padding: 0 20px;
            flex: 1;
            display: flex;
            flex-direction: column;
            justify-content: center;
        }
        .projects h2, .skills h2 {
            color: {{ text_color }};
            margin: 20px 0;
            font-size: {{ projects_size }}px;
        }
        .project {
            background: white;
            padding: 20px;
            margin: 20px 0;
            border-radius: 8px;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
            font-size: {{ projects_size }}px;
        }
        .project h3 {
            color: {{ text_color }};
            margin-top: 0;
            font-size: {{ projects_size|float + 8 }}px;
        }
        .project-links {
            margin-top: 10px;
        }
        .project-links ul {
            list-style: none;
            padding: 0;
        }
        .project-links li {
            margin: 5px 0;
        }
        .project-links a {
            color: #3498db;
            text-decoration: none;
        }
        .project-links a:hover {
            text-decoration: underline;
        }
        .skills {
            margin: 20px 0;
        }
        .skills ul {
            list-style: none;
            padding: 0;
            display: flex;
            flex-wrap: wrap;
            gap: 10px;
        }
        .skills li {
            background: #3498db;
            color: white;
            padding: 8px 15px;
            border-radius: 15px;
            font-size: {{ skills_size }}px;
        }
        footer {
            text-align: center;
            padding: 20px;
            background: {{ footer_color }};
            color: {{ footer_text_color }};
            width: 100%;
            font-size: {{ footer_size }}px;
        }
        @media (max-width: 600px) {
            header h1 {
                font-size: {{ title_size|float * 0.72 }}px;
            }
            .container {
                padding: 0 10px;
            }
            .project h3 {
                font-size: {{ projects_size|float * 0.8 + 8 }}px;
            }
        }
    </style>
</head>
<body>
    <header>
        <h1>{{ portfolio_title }}</h1>
        <p>Created by {{ name }}</p>
    </header>
    <div class="container">
        <div class="projects">
            <h2>Projects</h2>
            {% for project in projects %}
            <div class="project">
                <h3>{{ project.title }}</h3>
                <p>{{ project.description }}</p>
                {% if project.links %}
                <div class="project-links">
                    <ul>
                        {% for link in project.links %}
                        <li><a href="{{ link.url }}" target="_blank">{{ link.name }}</a></li>
                        {% endfor %}
                    </ul>
                </div>
                {% endif %}
            </div>
            {% endfor %}
        </div>
        <div class="skills">
            <h2>Skills</h2>
            <ul>
                {% for skill in skills %}
                    <li>{{ skill }}</li>
                {% endfor %}
            </ul>
        </div>
    </div>
    <footer>
        <p>© {{ name }} {{ current_year }}. All rights reserved.</p>
    </footer>
</body>
</html>
'''

@app.route('/')
def index():
    return render_template_string(FORM_TEMPLATE, error=None)

@app.route('/generate', methods=['POST'])
def generate():
    # Collect form data
    portfolio_title = request.form.get('portfolio_title')
    name = request.form.get('name')
    skills = request.form.get('skills')
    project_titles = request.form.getlist('project_titles[]')
    project_descriptions = request.form.getlist('project_descriptions[]')
    project_links = request.form.getlist('project_links[]')
    header_color = request.form.get('header_color', '#2c3e50')
    footer_color = request.form.get('footer_color', '#2c3e50')
    text_color = request.form.get('text_color', '#333333')
    background_color = request.form.get('background_color', '#f4f4f9')
    title_color = request.form.get('title_color', '#ffffff')
    created_by_color = request.form.get('created_by_color', '#ffffff')
    footer_text_color = request.form.get('footer_text_color', '#ffffff')
    title_size = request.form.get('title_size', '40')
    created_by_size = request.form.get('created_by_size', '19')
    text_size = request.form.get('text_size', '16')
    skills_size = request.form.get('skills_size', '14')
    projects_size = request.form.get('projects_size', '20')
    footer_size = request.form.get('footer_size', '16')

    # Log form data for debugging
    app.logger.debug(f"Received form data: portfolio_title={portfolio_title}, name={name}, skills={skills}")
    app.logger.debug(f"Project titles: {project_titles}")
    app.logger.debug(f"Project descriptions: {project_descriptions}")
    app.logger.debug(f"Project links: {project_links}")
    app.logger.debug(f"Colors: header={header_color}, footer={footer_color}, text={text_color}, background={background_color}, title={title_color}, created_by={created_by_color}, footer_text={footer_text_color}")
    app.logger.debug(f"Sizes: title={title_size}, created_by={created_by_size}, text={text_size}, skills={skills_size}, projects={projects_size}, footer={footer_size}")

    # Validate input
    if not all([portfolio_title, name, skills]) or not project_titles or not project_descriptions:
        app.logger.error("Validation failed: Missing required fields")
        return render_template_string(FORM_TEMPLATE, error="Portfolio title, name, skills, and at least one project are required")
    if len(project_titles) != len(project_descriptions):
        app.logger.error("Validation failed: Mismatched project titles and descriptions")
        return render_template_string(FORM_TEMPLATE, error="Mismatched project titles and descriptions")

    # Create projects list
    projects = []
    for i, (title, desc) in enumerate(zip(project_titles, project_descriptions)):
        # Parse links (comma-separated, format: "Name: URL")
        links = []
        if i < len(project_links) and project_links[i]:
            for link in project_links[i].split(','):
                link = link.strip()
                if ':' in link:
                    name, url = link.split(':', 1)
                    name = name.strip()
                    url = url.strip()
                    if name and url:
                        links.append({'name': name, 'url': url})
        projects.append({'title': title.strip(), 'description': desc.strip(), 'links': links})
    app.logger.debug(f"Processed projects: {projects}")

    # Split skills into a list
    skills_list = [skill.strip() for skill in skills.split(',') if skill.strip()]
    app.logger.debug(f"Skills list: {skills_list}")

    # Ensure portfolios directory exists
    os.makedirs('portfolios', exist_ok=True)

    # Render portfolio template
    from datetime import datetime
    portfolio_html = render_template_string(PORTFOLIO_TEMPLATE,
                                          portfolio_title=portfolio_title,
                                          name=name,
                                          projects=projects,
                                          skills=skills_list,
                                          current_year=datetime.now().year,
                                          header_color=header_color,
                                          footer_color=footer_color,
                                          text_color=text_color,
                                          background_color=background_color,
                                          title_color=title_color,
                                          created_by_color=created_by_color,
                                          footer_text_color=footer_text_color,
                                          title_size=title_size,
                                          created_by_size=created_by_size,
                                          text_size=text_size,
                                          skills_size=skills_size,
                                          projects_size=projects_size,
                                          footer_size=footer_size)

    # Save to file
    try:
        with open('portfolios/portfolio.html', 'w', encoding='utf-8') as f:
            f.write(portfolio_html)
        app.logger.info("Portfolio generated successfully")
    except Exception as e:
        app.logger.error(f"Error saving portfolio: {str(e)}")
        return render_template_string(FORM_TEMPLATE, error=f"Error saving portfolio: {str(e)}")

    return f'Portfolio generated at <a href="/portfolios/portfolio.html">portfolios/portfolio.html</a>'

# Serve generated portfolio files
@app.route('/portfolios/<path:filename>')
def serve_portfolio(filename):
    return app.send_static_file(os.path.join('portfolios', filename))

if __name__ == '__main__':
    app.run(port=8080, debug=True)