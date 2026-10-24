import streamlit as st
import streamlit.components.v1 as components
from google import genai
from PIL import Image
import json
import time

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
    "English (फुल्ली इंग्लिश मीडियम)", 
    "Hindi (फुल्ली हिंदी मीडियम)"
]

# सीधे Streamlit Secrets से API Key ले लेगा
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("🚀 FormulaSaathi Pro")
    st.markdown("---")
    st.markdown("**Advanced Features:**\n1. Camera Reset Button Added\n2. Smart Exponential Retry\n3. Infinite MCQ Poll Quiz\n4. Voice & Oral Revision")

st.title("🚀 FormulaSaathi & Teacher Pro Suite")

tab1, tab2, tab3 = st.tabs(["👨‍🎓 Student Zone & Solver", "👨‍🏫 Teacher A4 Paper Generator", "🎙️ Voice Assistant & Interactive Quiz"])

# स्मार्ट और सुरक्षित बैकग्राउंड रिट्राई फंक्शन (लंबे अंतराल के साथ ताकि लिमिट पार न हो)
def call_gemini_smart_retry(contents_data):
    if not api_key:
        return None
    
    client = genai.Client(api_key=api_key)
    for attempt in range(8):  # 8 स्मार्ट प्रयास
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=contents_data
            )
            if response and response.text:
                return response.text
        except Exception as e:
            # धीरे-धीरे समय बढ़ाकर कोशिश करेगा (2s, 4s, 6s...)
            time.sleep((attempt + 1) * 2.0)
            continue
    return None

# ==========================================
# TAB 1: STUDENT ZONE & MULTIMODAL SOLVER
# ==========================================
with tab1:
    st.subheader("💡 Smart Doubt Solver (Text, Photo & Voice Input)")
    
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        stu_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="s_class_1")
        stu_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="s_sub_1")
        stu_lang = st.radio("माध्यम चुनें", LANGUAGES_LIST, key="s_lang_1")
        
        st.markdown("---")
        st.markdown("📸 **या फोटो से सवाल पूछें:**")
        uploaded_image = st.file_uploader("गैलरी से फोटो अपलोड करें", type=["jpg", "png", "jpeg"])
        
        # कैमरा इनपुट और रीसेट करने का बटन
        camera_image = st.camera_input("या कैमरे से फोटो खींचें", key="cam_widget")
        if st.button("🗑️ कैमरा बंद करें / फोटो रीसेट करें"):
            if "cam_widget" in st.session_state:
                del st.session_state["cam_widget"]
                st.rerun()
        
        st.markdown("---")
        st.markdown("🎙️ **या बोलकर सवाल रिकॉर्ड करें:**")
        audio_file = st.audio_input("माइक पर बोलकर रिकॉर्ड करें")

    with col_s2:
        student_query = st.text_area("अपना सवाल या चैप्टर यहाँ लिखकर पूछें:", height=140, placeholder="उदाहरण: गति के नियमों को समझाएं या समीकरण हल करें...")
        
        if st.button("🔍 तुरंत हल देखें", key="btn_solve"):
            if not api_key:
                st.error("⚠️ कृपया Streamlit Secrets में GEMINI_API_KEY सेट करें!")
            else:
                with st.spinner("⚡ AI समाधान तैयार कर रहा है (स्मार्ट बैकग्राउंड कनेक्ट जारी है)..."):
                    prompt_text = f"""
                    Expert tutor for {stu_class} studying {stu_subject}.
                    Language: {stu_lang}. No dollar signs ($) or raw LaTeX. Use clean text.
                    Query/Context: {student_query if student_query.strip() else "Solve the given question/problem from the attached image or audio."}
                    Provide clear steps and explanation.
                    """
                    
                    contents_list = [prompt_text]
                    
                    active_img = uploaded_image if uploaded_image is not None else camera_image
                    if active_img is not None:
                        img = Image.open(active_img)
                        contents_list.append(img)
                    
                    if audio_file is not None:
                        audio_bytes = audio_file.read()
                        contents_list.append({"mime_type": "audio/wav", "data": audio_bytes})

                    res_text = call_gemini_smart_retry(contents_list)
                    if res_text:
                        st.success("✅ समाधान तैयार है!")
                        st.markdown(res_text)
                    else:
                        st.warning("⚠️ सर्वर अभी बहुत व्यस्त है। कृपया 5 सेकंड रुककर दोबारा क्लिक करें।")

# ==========================================
# TAB 2: TEACHER A4 QUESTION PAPER GENERATOR
# ==========================================
with tab2:
    st.subheader("📄 सुपर-फास्ट A4 क्वेश्चन पेपर जनरेटर")
    
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
    include_answers = st.checkbox("अलग पेज पर Answer Key (उत्तर माला) जोड़ें", value=True)

    if st.button("✨ सुपर-फास्ट A4 क्वेश्चन पेपर तैयार करें"):
        if not api_key:
            st.error("⚠️ कृपया Streamlit Secrets में GEMINI_API_KEY सेट करें!")
        elif not topic_name.strip():
            st.warning("⚠️ कृपया चैप्टर का नाम लिखें!")
        else:
            with st.spinner("⚡ प्रश्न-पत्र जनरेट हो रहा है..."):
                t_prompt = f"""
                Generate exam Question Paper in clean HTML format (ONLY inner HTML tags like <h4>, <ol>, <li>, <p>, NO markdown ```html fences).
                Language: {paper_lang}. Class: {t_class}, Subject: {t_subject}, Topic: {topic_name}, Difficulty: {difficulty}.
                Sections: MCQ: {mcq_q}, Fill blanks: {fib_q}, 2 Marks: {two_m_q}, 3 Marks: {three_m_q}, 5 Marks: {five_m_q}.
                - {"At the end, insert Answer Key." if include_answers else ""}
                """
                res_html = call_gemini_smart_retry([t_prompt])
                if res_html:
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
                    
                    components.html(full_a4_html, height=600, scrolling=True)

# ==========================================
# TAB 3: VOICE ASSISTANT & POLL-STYLE QUIZ
# ==========================================
with tab3:
    st.subheader("🎙️ Voice Assistant & Bilingual Poll-Style Quiz")
    
    quiz_tab1, quiz_tab2 = st.tabs(["🗣️ Oral Revision & Audio Assistant", "📊 Poll-Style MCQ Quiz (Bilingual)"])
    
    with quiz_tab1:
        st.markdown("### मौखिक रिवीजन (Oral Exam Revision)")
        v_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="v_sub")
        v_topic = st.text_input("रिवीजन के लिए टॉपिक लिखें:", placeholder="जैसे: गुरुत्वाकर्षण (Gravitation)")
        
        if st.button("🗣️ मौखिक रिवीजन प्रश्न पूछें"):
            if not v_topic.strip():
                st.warning("⚠️ कृपया टॉपिक का नाम लिखें!")
            else:
                with st.spinner("⚡ ओरल रिवीजन सेट तैयार हो रहा है..."):
                    v_prompt = f"""
                    Act as a strict and encouraging school teacher doing oral revision before an exam for {v_subject}, Topic: {v_topic}.
                    Ask 3 revision questions one by one (1 short conceptual question, 1 two-mark question, 1 five-mark important question) in Hindi. Provide answers below each.
                    """
                    v_res = call_gemini_smart_retry([v_prompt])
                    if v_res:
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
                        st.warning("⚠️ सर्वर व्यस्त है। कृपया पुनः प्रयास करें।")

    with quiz_tab2:
        st.markdown("### 📊 पोल-टाइप इंटरैक्टिव क्विज़ (Interactive MCQ Poll)")
        pq_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="pq_cls")
        pq_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="pq_sub")
        pq_lang = st.selectbox("माध्यम चुनें", ["Hindi (हिंदी)", "English (अंग्रेजी)", "Bilingual (हिन्दी + English)"], key="pq_lang")
        pq_topic = st.text_input("क्विज़ के लिए चैप्टर/टॉपिक लिखें:", placeholder="जैसे: विद्युत धारा (Electric Current)", key="pq_top")
        
        if st.button("🚀 क्विज़ शुरू करें"):
            if not pq_topic.strip():
                st.warning("⚠️ कृपया टॉपिक का नाम लिखें!")
            else:
                with st.spinner("⚡ इंटरैक्टिव क्विज़ जनरेट हो रहा है..."):
                    quiz_prompt = f"""
                    Generate 5 multiple-choice questions (MCQs) for {pq_class}, Subject: {pq_subject}, Topic: {pq_topic}.
                    Language Medium: {pq_lang}.
                    Provide output in a strict JSON format list of objects:
                    [
                      {{"question": "...", "options": ["A) ...", "B) ...", "C) ...", "D) ..."], "answer": "A", "explanation": "..."}}
                    ]
                    Return ONLY valid JSON, no markdown formatting fences if possible, or clean JSON text.
                    """
                    raw_quiz = call_gemini_smart_retry([quiz_prompt])
                    if raw_quiz:
                        try:
                            cleaned_json = raw_quiz.replace("```json", "").replace("```", "").strip()
                            quiz_data = json.loads(cleaned_json)
                            st.session_state['quiz_data'] = quiz_data
                            st.success("✅ क्विज़ तैयार है! नीचे पोल में जवाब दें:")
                        except:
                            st.markdown(raw_quiz)
                    else:
                        st.warning("⚠️ सर्वर व्यस्त है। कृपया पुनः प्रयास करें।")

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
