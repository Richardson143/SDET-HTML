from flask import Blueprint, render_template, session, request, redirect, url_for, send_file, jsonify
from routes.utils import generate_gherkin_feature, generate_test_scenarios, main, identify_elements_and_generate_csv, streamlit_webagent_demo
from routes.utils import setup_interactive_browser, get_selected_elements, generate_test_scenarios
import os
import base64
from io import BytesIO
from PIL import Image
from selenium import webdriver

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    if 'user' in session:
        return redirect(url_for('main.dashboard'))
    return redirect(url_for('auth.login'))

@main_bp.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    return render_template('dashboard.html')

@main_bp.route('/test-idea-generation', methods=['GET', 'POST'])
def test_idea_generation():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        url = request.form['url']
        selected_elements = request.form['selected_elements']
        screenshot = request.files['screenshot'].read()
        test_scenarios = generate_test_scenarios(url, selected_elements, screenshot)
        return render_template('test_idea_generation.html', test_scenarios=test_scenarios)
    return render_template('test_idea_generation.html')

@main_bp.route('/setup-interactive-browser', methods=['POST'])
def setup_interactive_browser_route():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    url = request.form['url']
    driver = setup_interactive_browser(url)
    session['driver_pid'] = driver.service.process.pid
    return jsonify({'status': 'success'})

@main_bp.route('/get-selected-elements', methods=['GET'])
def get_selected_elements_route():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    driver_pid = session.get('driver_pid')
    if not driver_pid:
        return jsonify({'error': 'Browser not initialized'}), 400
    selected_elements = get_selected_elements(driver_pid)
    return jsonify(selected_elements)

@main_bp.route('/capture-screenshot', methods=['GET'])
def capture_screenshot():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    driver_pid = session.get('driver_pid')
    if not driver_pid:
        return jsonify({'error': 'Browser not initialized'}), 400
    driver = webdriver.Chrome()
    driver.service.process.pid = driver_pid
    screenshot = driver.get_screenshot_as_png()
    buffered = BytesIO(screenshot)
    img = Image.open(buffered)
    buffered = BytesIO()
    img.save(buffered, format="PNG")
    img_str = base64.b64encode(buffered.getvalue()).decode()
    return jsonify({'screenshot': img_str})

@main_bp.route('/element-inspector', methods=['GET', 'POST'])
def element_inspector():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        url = request.form['url']
        output_file = request.form['output_file']
        identify_elements_and_generate_csv(url, output_file)
        return send_file(output_file, as_attachment=True)
    return render_template('element_inspector.html')

@main_bp.route('/gherkin-generator', methods=['GET', 'POST'])
def gherkin_generator():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        user_story = request.form['user_story']
        detail_level = request.form['detail_level']
        gherkin_feature = generate_gherkin_feature(user_story, detail_level)
        return render_template('gherkin_generator.html', gherkin_feature=gherkin_feature)
    return render_template('gherkin_generator.html')

@main_bp.route('/code-generator', methods=['GET', 'POST'])
def code_generator():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        url = request.form['url']
        feature_content = request.form['feature_content']
        language = request.form['language']
        output_path, code = main(url, feature_content, language)
        return render_template('code_generator.html', code=code)
    return render_template('code_generator.html')

@main_bp.route('/agent-explorer', methods=['GET', 'POST'])
def agent_explorer():
    if 'user' not in session:
        return redirect(url_for('auth.login'))
    if request.method == 'POST':
        objective = request.form['objective']
        url = request.form['url']
        result = streamlit_webagent_demo(objective, url)
        return render_template('agent_explorer.html', result=result)
    return render_template('agent_explorer.html')