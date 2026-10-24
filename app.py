import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image
import json
import time
import tempfile
import itertools

# पेज सेटअप
st.set_page_config(page_title="FormulaSaathi & Teacher Pro Suite", layout="wide")

ALL_SUBJECTS = [
    "--- कृपया विषय चुनें (Select Subject) ---",
    "Computer Science (कंप्यूटर साइंस)",
    "Physics (भौतिकी)",
    "Chemistry (रसायन शास्त्र)",
    "Mathematics (गणित)",
    "Biology (जीव विज्ञान)",
    "Science (विज्ञान - Combined)",
    "Social Science - SST (सामाजिक विज्ञान)",
    "History (इतिहास)",
    "Geography (भूगोल)",
    "Economics (अर्थशास्त्र)",
    "Civics / Pol. Science (नागरिक शास्त्र)",
    "Hindi (हिंदी)",
    "Maithili (मैथिली)",
    "Sanskrit (संस्कृत)",
    "English (अंग्रेजी)",
    "Urdu (उर्दू)"
]

CLASSES_LIST = [
    "--- कक्षा चुनें ---",
    "Class 1", "Class 2", "Class 3", "Class 4", "Class 5", 
    "Class 6", "Class 7", "Class 8", "Class 9", "Class 10", 
    "Class 11 (General)", "Class 11 - IIT JEE", "Class 11 - NEET", 
    "Class 12 (General)", "Class 12 - IIT JEE", "Class 12 - NEET"
]

LANGUAGES_LIST = [
    "Bilingual (हिन्दी + English दोनों)",
    "Hindi (फुल्ली हिंदी मीडियम)",
    "English (फुल्ली इंग्लिश मीडियम)"
]

# मल्टीपल API Keys को मैनेज करने का सिस्टम
def get_api_keys():
    keys = []
    if "GEMINI_KEYS" in st.secrets:
        keys = list(st.secrets["GEMINI_KEYS"])
    elif "GEMINI_API_KEY" in st.secrets:
        keys = [st.secrets["GEMINI_API_KEY"]]
    return keys

api_keys_pool = get_api_keys()
key_cycler = itertools.cycle(api_keys_pool) if api_keys_pool else None

with st.sidebar:
    st.header("🚀 FormulaSaathi Pro")
    st.markdown("---")
    st.markdown(f"**Loaded Keys:** {len(api_keys_pool)}")
    st.markdown("1. Multi-Photo Upload Support\n2. Native Voice Audio Mic\n3. Turbo Speed & 503 Retry")

st.title("🚀 FormulaSaathi & Teacher Pro Suite")

tab1, tab2, tab3 = st.tabs(["👨‍🎓 Student Zone & Solver", "👨‍🏫 Teacher A4 Paper Generator", "🎙️ Voice Assistant & Interactive Quiz"])

# टर्बो स्पीड और ऑटो-रीट्राई वाला मजबूत जेमिनी कॉल फंक्शन
def call_gemini(contents_list):
    if not api_keys_pool:
        return "ERROR: No API Keys found in Streamlit Secrets!"
    
    last_error = ""
    for attempt in range(3):
        for _ in range(len(api_keys_pool)):
            current_key = next(key_cycler)
            try:
                client = genai.Client(api_key=current_key)
                response = client.models.generate_content(
                    model="gemini-3.8-flash",
                    contents=contents_list
                )
                if response and response.text:
                    return response.text
            except Exception as e:
                last_error = str(e)
                if "503" in last_error or "UNAVAILABLE" in last_error or "ResourceExhausted" in last_error:
                    time.sleep(0.5)
                continue
    return f"API_ERROR: {last_error}"

# ==========================================
# TAB 1: STUDENT ZONE & MULTIMODAL SOLVER
# ==========================================
with tab1:
    st.subheader("💡 Smart Doubt Solver (Multi-Photo, Text & Voice Audio)")
    
    col_s1, col_s2 = st.columns([1, 2])
    
    with col_s1:
        stu_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="s_class_1")
        stu_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="s_sub_1")
        stu_lang = st.selectbox("माध्यम चुनें", LANGUAGES_LIST, key="s_lang_1")
        
        st.markdown("---")
        st.markdown("📸 **एक से अधिक फोटो अपलोड करें:**")
        uploaded_images = st.file_uploader("गैलरी से कई फोटो चुनें", type=["jpg", "png", "jpeg"], accept_multiple_files=True)
        
        use_camera = st.checkbox("📸 कैमरा चालू करें")
        camera_image = st.camera_input("कैमरा", key="cam_widget") if use_camera else None

    with col_s2:
        st.markdown("### 🎙️ बोलकर पूछें (Voice Mic) या ✍️ लिखकर बताएं")
        
        # वॉइस रिकॉर्डर (माइक बटन)
        audio_file = st.audio_input("🎙️ माइक पर बोलकर रिकॉर्ड करें (क्लिक करें)")
        
        student_query = st.text_area("या अपना सवाल लिखकर यहाँ बताएं:", height=100, placeholder="उदाहरण: प्रकाश संश्लेषण क्या है?")
        
        if st.button("🔍 तुरंत हल देखें", key="btn_solve"):
            if not api_keys_pool:
                st.error("⚠️ कृपया Streamlit Secrets में GEMINI_KEYS सेट करें!")
            elif not student_query.strip() and not uploaded_images and camera_image is None and audio_file is None:
                st.warning("⚠️ कृपया कुछ लिखें, बोलें या कम से कम एक फोटो अपलोड करें!")
            else:
                with st.spinner("⚡ AI आपकी फोटो, आवाज और सवाल का समाधान तैयार कर रहा है (रॉकेट स्पीड)..."):
                    prompt_text = f"""
                    Expert tutor for {stu_class} studying {stu_subject}.
                    Language Medium: {stu_lang}. (If Bilingual, provide explanation in both Hindi and English). No raw LaTeX or dollar signs. Use clean text.
                    Query/Context: {student_query if student_query.strip() else "Solve the questions/content provided in the attached images or audio."}
                    Provide clear steps and explanation.
                    """
                    
                    contents_to_send = [prompt_text]
                    
                    # अगर एक या एक से अधिक फोटो हैं तो सभी को जोड़ें
                    if uploaded_images:
                        for img_file in uploaded_images:
                            contents_to_send.append(Image.open(img_file))
                            
                    if camera_image is not None:
                        contents_to_send.append(Image.open(camera_image))
                        
                    # अगर आवाज रिकॉर्ड की गई है
                    if audio_file is not None:
                        audio_bytes = audio_file.read()
                        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
                            tmp.write(audio_bytes)
                            tmp_path = tmp.name
                        
                        current_key = next(key_cycler)
                        client = genai.Client(api_key=current_key)
                        uploaded_audio_ref = client.files.upload(file=tmp_path)
                        contents_to_send.append(uploaded_audio_ref)
                    
                    res_text = call_gemini(contents_to_send)
                    if res_text and not res_text.startswith("API_ERROR") and not res_text.startswith("ERROR"):
                        st.success("✅ समाधान तैयार है!")
                        st.markdown(res_text)
                        
                        safe_res_json = json.dumps(res_text)
                        components.html(f"""
                        <script>
                        var textData = {safe_res_json};
                        var blob = new Blob([textData], {{ type: 'text/markdown' }});
                        var link = document.createElement('a');
                        link.href = window.URL.createObjectURL(blob);
                        link.download = 'FormulaSaathi_Solution.md';
                        document.body.appendChild(link);
                        link.click();
                        document.body.removeChild(link);
                        </script>
                        """, height=0)
                    else:
                        st.error(f"⚠️ गूगल सर्वर से एरर आया है: {res_text}")

# ==========================================
# TAB 2: TEACHER A4 QUESTION PAPER GENERATOR
# ==========================================
with tab2:
    st.subheader("📄 सुपर-फास्ट A4 क्वेश्चन पेपर जनरेटर (Bilingual Supported)")
    
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        coaching_name = st.text_input("कोचिंग / संस्थान का नाम", value="", placeholder="कोचिंग का नाम")
    with c2:
        t_class = st.selectbox("कक्षा स्तर", CLASSES_LIST, index=10, key="t_class")
    with c3:
        t_subject = st.selectbox("विषय", ALL_SUBJECTS, key="t_sub")
    with c4:
        topic_name = st.text_input("चैप्टर / टॉपिक", placeholder="जैसे: Chapter 1")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        exam_time = st.text_input("समय", value="2 Hours")
    with c6:
        difficulty = st.selectbox("कठिनाई स्तर", ["Board Standard", "Medium", "Hard", "IIT-JEE / NEET Advanced"])
    with c7:
        paper_lang = st.selectbox("माध्यम", LANGUAGES_LIST, key="t_lang")
    with c8:
        paper_size = st.selectbox("पेज साइज", ["A4", "Legal", "Letter"])

    q1, q2, q3, q4, q5 = st.columns(5)
    with q1:
        mcq_str = st.text_input("MCQ (1 अंक)", value="5")
        mcq_q = int(mcq_str.strip()) if mcq_str.strip().isdigit() else 0
    with q2:
        fib_str = st.text_input("Fill in Blanks", value="5")
        fib_q = int(fib_str.strip()) if fib_str.strip().isdigit() else 0
    with q3:
        two_str = st.text_input("2-अंक प्रश्न", value="3")
        two_m_q = int(two_str.strip()) if two_str.strip().isdigit() else 0
    with q4:
        three_str = st.text_input("3-अंक प्रश्न", value="2")
        three_m_q = int(three_str.strip()) if three_str.strip().isdigit() else 0
    with q5:
        five_str = st.text_input("5-अंक प्रश्न", value="2")
        five_m_q = int(five_str.strip()) if five_str.strip().isdigit() else 0

    calculated_marks = (mcq_q * 1) + (fib_q * 1) + (two_m_q * 2) + (three_m_q * 3) + (five_m_q * 5)
    total_questions = mcq_q + fib_q + two_m_q + three_m_q + five_m_q
    
    st.info(f"📊 **कुल प्रश्न: {total_questions} | कुल पूर्णांक: {calculated_marks} अंक**")
    include_answers = st.checkbox("अलग पेज पर Answer Key जोड़ें", value=True)

    if st.button("✨ सुपर-फास्ट A4 क्वेश्चन पेपर तैयार करें"):
        if not api_keys_pool:
            st.error("⚠️ कृपया Streamlit Secrets में GEMINI_KEYS सेट करें!")
        elif not topic_name.strip():
            st.warning("⚠️ कृपया चैप्टर का नाम लिखें!")
        else:
            with st.spinner("⚡ प्रश्न-पत्र जनरेट हो रहा है (टर्बो स्पीड)..."):
                t_prompt = f"""
                Generate exam Question Paper in clean HTML format (ONLY inner HTML tags like <h4>, <ol>, <li>, <p>, NO markdown ```html fences).
                Language Medium: {paper_lang}. (If Bilingual, provide questions in both Hindi and English). Class: {t_class}, Subject: {t_subject}, Topic: {topic_name}, Difficulty: {difficulty}.
                Sections: MCQ: {mcq_q}, Fill blanks: {fib_q}, 2 Marks: {two_m_q}, 3 Marks: {three_m_q}, 5 Marks: {five_m_q}.
                - {"At the end, insert Answer Key." if include_answers else ""}
                """
                res_html = call_gemini([t_prompt])
                if res_html and not res_html.startswith("API_ERROR") and not res_html.startswith("ERROR"):
                    clean_questions_html = res_html.replace("```html", "").replace("```", "").strip()
                    coaching_header = f"<div class='coaching-title'>{coaching_name.strip()}</div>" if coaching_name.strip() else ""
                    
                    full_a4_html = f"""<!DOCTYPE html>
<html>
<head><meta charset="utf-8"><title>Question_Paper</title>
<style>
    @page {{ size: {paper_size}; margin: 10mm 12mm; }}
    body {{ font-family: 'Times New Roman', serif; font-size: 11pt; line-height: 1.3; color: #000; background: #fff; }}
    .coaching-title {{ text-align: center; font-size: 15pt; font-weight: bold; text-transform: uppercase; }}
    .sub-header {{ text-align: center; font-size: 11.5pt; font-weight: bold; }}
    .meta-bar {{ display: flex; justify-content: space-between; font-size: 10.5pt; font-weight: bold; border-top: 1px solid #000; border-bottom: 1.5px solid #000; padding: 3px 0; margin-bottom: 8px; }}
</style>
</head>
<body>
    {coaching_header}
    <div class="sub-header">{t_class} | Subject: {t_subject} ({topic_name})</div>
    <div class="meta-bar"><span>Time: {exam_time}</span><span>Full Marks: {calculated_marks}</span></div>
    {clean_questions_html}
</body>
</html>"""
                    st.success("✅ प्रश्न-पत्र तैयार है!")
                    safe_html_json = json.dumps(full_a4_html)
                    
                    components.html(f"""
                    <script>
                    var htmlContent = {safe_html_json};
                    var blob = new Blob([htmlContent], {{ type: 'text/html' }});
                    var link = document.createElement('a');
                    link.href = window.URL.createObjectURL(blob);
                    link.download = 'Question_Paper_{t_class.replace(" ", "_")}.html';
                    document.body.appendChild(link);
                    link.click();
                    document.body.removeChild(link);
                    </script>
                    """, height=0)

                    col_btn1, col_btn2 = st.columns(2)
                    with col_btn1:
                        components.html(f"""
                        <script>
                        function printA4() {{
                            var win = window.open('', '_blank');
                            win.document.write({safe_html_json});
                            win.document.close();
                            win.print();
                        }}
                        </script>
                        <button onclick="printA4()" style="background:#1a73e8;color:white;padding:10px 18px;font-size:15px;font-weight:bold;border:none;border-radius:6px;cursor:pointer;width:100%;">🖨️ A4 Print / Save PDF</button>
                        """, height=55)
                    with col_btn2:
                        st.download_button("📥 Download HTML File", data=full_a4_html, file_name="Question_Paper.html", mime="text/html", use_container_width=True)
                else:
                    st.error(f"⚠️ गूगल सर्वर से एरर आया है: {res_html}")

# ==========================================
# TAB 3: VOICE ASSISTANT & POLL-STYLE QUIZ
# ==========================================
with tab3:
    st.subheader("🎙️ Voice Assistant & Bilingual Poll-Style Quiz")
    
    quiz_tab1, quiz_tab2 = st.tabs(["🗣️ Oral Revision & Audio Assistant", "📊 Poll-Style MCQ Quiz (Bilingual)"])
    
    with quiz_tab1:
        st.markdown("### मौखिक रिवीजन (Oral Exam Revision)")
        v_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="v_cls")
        v_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="v_sub")
        v_lang = st.selectbox("माध्यम चुनें", LANGUAGES_LIST, key="v_lang_oral")
        v_topic = st.text_input("रिवीजन के लिए टॉपिक लिखें:", placeholder="जैसे: गुरुत्वाकर्षण (Gravitation)", key="v_top_input")
        
        if st.button("🗣️ मौखिक रिवीजन प्रश्न पूछें", key="btn_oral"):
            if not v_topic.strip():
                st.warning("⚠️ कृपया टॉपिक का नाम लिखें!")
            else:
                with st.spinner("⚡ ओरल रिवीजन सेट तैयार हो रहा है (रॉकेट स्पीड)..."):
                    v_prompt = f"""
                    Act as a strict and encouraging school teacher doing oral revision before an exam for {v_class}, Subject: {v_subject}, Topic: {v_topic}.
                    Language Medium: {v_lang}. (If Bilingual, ask questions in both Hindi and English).
                    Ask 3 revision questions one by one (1 short conceptual question, 1 two-mark question, 1 five-mark important question). Provide answers below each.
                    """
                    v_res = call_gemini([v_prompt])
                    if v_res and not v_res.startswith("API_ERROR") and not v_res.startswith("ERROR"):
                        st.success("✅ ओरल रिवीजन सेट तैयार है!")
                        st.markdown(v_res)
                        
                        speech_text = v_res.replace('"', '').replace('\n', ' ')
                        components.html(f"""
                        <button onclick="speakText()" style="background:#34a853;color:white;padding:10px 18px;font-size:15px;font-weight:bold;border:none;border-radius:6px;cursor:pointer;width:100%;">🔊 ऑडियो सुनें (Listen Aloud)</button>
                        <script>
                        function speakText() {{
                            var msg = new SpeechSynthesisUtterance("{speech_text[:500]}");
                            msg.lang = 'hi-IN';
                            window.speechSynthesis.speak(msg);
                        }}
                        </script>
                        """, height=60)
                    else:
                        st.error(f"⚠️ एरर: {v_res}")

    with quiz_tab2:
        st.markdown("### 📊 पोल-टाइप इंटरैक्टिव क्विज़ (Interactive MCQ Poll)")
        pq_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="pq_cls")
        pq_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="pq_sub")
        pq_lang = st.selectbox("माध्यम चुनें", LANGUAGES_LIST, key="pq_lang")
        pq_topic = st.text_input("क्विज़ के लिए चैप्टर/टॉपिक लिखें:", placeholder="जैसे: विद्युत धारा (Electric Current)", key="pq_top")
        
        if st.button("🚀 क्विज़ शुरू करें", key="btn_quiz_start"):
            if not pq_topic.strip():
                st.warning("⚠️ कृपया टॉपिक का नाम लिखें!")
            else:
                with st.spinner("⚡ इंटरैक्टिव क्विज़ जनरेट हो रहा है (टर्बो स्पीड)..."):
                    quiz_prompt = f"""
                    Generate exactly 5 multiple-choice questions (MCQs) for {pq_class}, Subject: {pq_subject}, Topic: {pq_topic}.
                    Language Medium: {pq_lang}. (If Bilingual, write each question and options in both Hindi and English).
                    Provide output in a strict JSON format list of objects and nothing else:
                    [
                      {{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A", "explanation": "..."}}
                    ]
                    """
                    raw_quiz = call_gemini([quiz_prompt])
                    if raw_quiz and not raw_quiz.startswith("API_ERROR") and not raw_quiz.startswith("ERROR"):
                        try:
                            cleaned_json = raw_quiz.replace("```json", "").replace("```", "").strip()
                            quiz_data = json.loads(cleaned_json)
                            st.session_state['quiz_data'] = quiz_data
                            st.success("✅ क्विज़ तैयार है! नीचे पोल में जवाब दें:")
                        except Exception as e:
                            st.error(f"⚠️ JSON पार्सिंग में समस्या: {e}")
                            st.markdown(raw_quiz)
                    else:
                        st.error(f"⚠️ एरर: {raw_quiz}")

        if 'quiz_data' in st.session_state:
            for i, q in enumerate(st.session_state['quiz_data']):
                st.markdown(f"**Q{i+1}: {q.get('question', '')}**")
                user_choice = st.radio(f"विकल्प चुनें Q{i+1}", q.get('options', []), key=f"q_{i}")
                
                if st.button(f"उत्तर जाँचें Q{i+1}", key=f"check_{i}"):
                    correct_opt = q.get('answer', '')
                    if user_choice and user_choice.startswith(correct_opt):
                        st.success(f"🎉 बिल्कुल सही! स्पष्टीकरण: {q.get('explanation', '')}")
                    else:
                        st.warning(f"❌ गलत! सही उत्तर ऑप्शन {correct_opt} है। स्पष्टीकरण: {q.get('explanation', '')}")
                st.markdown("---")
