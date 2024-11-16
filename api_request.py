from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from openai import OpenAI
import pdfplumber
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
CORS(app)

# 업로드 폴더 설정
UPLOAD_FOLDER = 'uploads'
os.makedirs(UPLOAD_FOLDER, exist_ok=True)
os.makedirs('videos', exist_ok=True)

# 1. PDF에서 텍스트 추출
def extract_text_from_pdf(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        return ''.join([page.extract_text() for page in pdf.pages])

# 2. GPT 프롬프트 생성
def generate_prompt(job_description, resume_text):
    return f"""
    채용공고:
    {job_description}

    지원자의 이력서:
    {resume_text}

    해당 이력서와 채용공고를 기반으로 심오하고 구체적인 면접 질문은 3개 만들어주세요. 
    말투는 면접관스러운 자연스러운 말투로 만들어주세요.
    각 질문은 번호와 함께 새로운 줄에 작성해주세요.
    """

# 3. GPT API 호출
def get_interview_questions(prompt, api_key):
    client = OpenAI(api_key=api_key)
    response = client.chat.completions.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "당신은 채용 면접관입니다."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

# 4. 질문 텍스트 처리
def process_questions(questions_text):
    # 질문을 줄바꿈으로 분리하고 빈 줄 제거
    questions = [q.strip() for q in questions_text.split('\n') if q.strip()]
    # 번호가 있는 질문만 선택 (최대 3개)
    questions = [q for q in questions if any(q.startswith(str(i)) for i in range(1, 4))][:3]
    return questions

@app.route('/api/interview', methods=['POST'])
def get_interview_data():
    try:
        # FormData에서 파일과 텍스트 받기
        if 'resume' not in request.files:
            return jsonify({'success': False, 'error': 'No resume file'}), 400
            
        resume_file = request.files['resume']
        job_description = request.form.get('jobDescription')
        
        if not job_description:
            return jsonify({'success': False, 'error': 'No job description'}), 400

        # PDF 파일 임시 저장
        filename = secure_filename(resume_file.filename)
        resume_path = os.path.join(UPLOAD_FOLDER, filename)
        resume_file.save(resume_path)

        #api_key = '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'

        try:
            # 질문 생성
            resume_text = extract_text_from_pdf(resume_path)
            prompt = generate_prompt(job_description, resume_text)
            questions = get_interview_questions(prompt, api_key)
            
            # 질문 처리
            processed_questions = process_questions(questions)
            
            # 비디오 파일 경로
            video_files = ['test1.mp4', 'test2.mp4', 'test3.mp4']
            
            # 응답 데이터 구성
            response_data = {
                'quiz_title': processed_questions,
                'video': video_files
            }
            
            return jsonify({
                'success': True,
                'data': response_data
            })

        finally:
            # 임시 파일 삭제
            if os.path.exists(resume_path):
                os.remove(resume_path)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/api/video/<filename>', methods=['GET'])
def get_video(filename):
    try:
        video_path = os.path.join('videos', filename)
        return send_file(
            video_path,
            mimetype='video/mp4',
            as_attachment=True,
            download_name=filename
        )
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 404

if __name__ == '__main__':
    app.run(debug=True, port=5000)