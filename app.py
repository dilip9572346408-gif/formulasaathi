import streamlit as st
import streamlit.components.v1 as components
from google import genai
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
    st.markdown("**Advanced Features:**\n1. Heavy Background Auto-Retry\n2. Infinite MCQ Practice\n3. Voice Assistant Revision\n4. A4 Paper Generator")

st.title("🚀 FormulaSaathi & Teacher Pro Suite")

tab1, tab2, tab3 = st.tabs(["👨‍🎓 Student Zone & MCQs", "👨‍🏫 Teacher A4 Paper Generator", "🎙️ Voice Assistant & Oral Revision"])

# हेवी बैकग्राउंड ऑटो-रिट्राई फंक्शन (जो 12-15 बार चुपचाप कोशिश करेगा)
def call_gemini_heavy_retry(prompt_text):
    if not api_key:
        return None
    
    client = genai.Client(api_key=api_key)
    for attempt in range(15):  # 15 बार तक बैकग्राउंड में कोशिश करेगा
        try:
            response = client.models.generate_content(
                model="gemini-1.5-flash",
                contents=prompt_text
            )
            if response and response.text:
                return response.text
        except Exception as e:
            time.sleep(1.2)  # थोड़ा रुककर फिर से प्रयास करेगा
            continue
    return None

# ==========================================
# TAB 1: STUDENT ZONE & INFINITE MCQS
# ==========================================
with tab1:
    st.subheader("💡 Smart Doubt Solver & Infinite MCQ Practice")
    
    sub_tab1, sub_tab2 = st.tabs(["🔍 Doubt & Numerical Solver", "🎯 Infinite MCQ Practice Generator"])
    
    with sub_tab1:
        col_s1, col_s2 = st.columns([1, 2])
        with col_s1:
            stu_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="s_class_1")
            stu_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="s_sub_1")
            stu_lang = st.radio("माध्यम चुनें", LANGUAGES_LIST, key="s_lang_1")
        
        with col_s2:
            student_query = st.text_area("अपना सवाल या चैप्टर यहाँ लिखें:", height=140, placeholder="उदाहरण: गति के नियमों को समझाएं...")
        
        if st.button("🔍 तुरंत हल देखें", key="btn_solve"):
            if not api_key:
                st.error("⚠️ कृपया Streamlit Secrets में GEMINI_API_KEY सेट करें!")
            elif not student_query.strip():
                st.warning("⚠️ कृपया अपना सवाल लिखें।")
            else:
                with st.spinner("⚡ AI समाधान तैयार कर रहा है (हेवी ऑटो-कनेक्ट जारी है)..."):
                    prompt = f"""
                    Expert tutor for {stu_class} studying {stu_subject}.
                    Language: {stu_lang}. No dollar signs ($) or raw LaTeX. Use clean text.
                    Query: {student_query}. Provide clear steps.
                    """
                    res_text = call_gemini_heavy_retry(prompt)
                    if res_text:
                        st.success("✅ समाधान तैयार है!")
                        st.markdown(res_text)
                    else:
                        st.warning("⚠️ सर्वर अत्यधिक व्यस्त है। कृपया पुनः प्रयास करें।")

    with sub_tab2:
        st.markdown("### 🎯 इनफाइनाइट बहुविकल्पीय प्रश्न (MCQ) प्रैक्टिस")
        mcq_col1, mcq_col2, mcq_col3 = st.columns(3)
        with mcq_col1:
            mcq_class = st.selectbox("कक्षा चुनें", CLASSES_LIST, key="mcq_cls")
        with mcq_col2:
            mcq_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="mcq_sub")
        with mcq_col3:
            mcq_count = st.slider("प्रश्नों की संख्या चुनें", min_value=5, max_value=30, value=10)
        
        mcq_topic = st.text_input("चैप्टर या टॉपिक का नाम लिखें:", placeholder="जैसे: प्रकाश का परावर्तन (Reflection of Light)")
        
        if st.button("🚀 इनफाइनाइट MCQs जनरेट करें"):
            if not mcq_topic.strip():
                st.warning("⚠️ कृपया चैप्टर या टॉपिक का नाम लिखें!")
            else:
                with st.spinner("⚡ इनफाइनाइट MCQs तैयार हो रहे हैं..."):
                    mcq_prompt = f"""
                    Generate {mcq_count} multiple-choice questions (MCQs) for {mcq_class} student studying {mcq_subject}, Topic: {mcq_topic}.
                    Format each question cleanly with options (A, B, C, D) and provide an Answer Key at the end.
                    Language: Hindi. No LaTeX or dollar signs.
                    """
                    mcq_result = call_gemini_heavy_retry(mcq_prompt)
                    if mcq_result:
                        st.success("✅ आपके प्रैक्टिस MCQs तैयार हैं!")
                        st.markdown(mcq_result)
                    else:
                        st.warning("⚠️ सर्वर व्यस्त है। कृपया पुनः प्रयास करें।")

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
                res_html = call_gemini_heavy_retry(t_prompt)
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
# TAB 3: VOICE ASSISTANT & ORAL REVISION
# ==========================================
with tab3:
    st.subheader("🎙️ Voice Assistant & Oral Revision (मौखिक रिवीजन)")
    st.markdown("यहाँ से आप वॉइस असिस्टेंट की मदद से मौखिक रूप से सवाल पूछ सकते हैं और रिवीजन कर सकते हैं।")
    
    v_subject = st.selectbox("विषय चुनें", ALL_SUBJECTS, key="v_sub")
    v_topic = st.text_input("रिवीजन के लिए टॉपिक लिखें:", placeholder="जैसे: गुरुत्वाकर्षण (Gravitation)")
    
    if st.button("🗣️ मौखिक रिवीजन प्रश्न पूछें"):
        if not v_topic.strip():
            st.warning("⚠️ कृपया टॉपिक का नाम लिखें!")
        else:
            with st.spinner("⚡ ओरल रिवीजन प्रश्न तैयार हो रहे हैं..."):
                v_prompt = f"""
                Act as a strict and encouraging school teacher doing oral revision before an exam for {v_subject}, Topic: {v_topic}.
                Ask 3 revision questions one by one (1 short conceptual question, 1 two-mark question, 1 five-mark important question) in Hindi. Provide answers below each.
                """
                v_res = call_gemini_heavy_retry(v_prompt)
                if v_res:
                    st.success("✅ ओरल रिवीजन सेट तैयार है!")
                    st.markdown(v_res)
                    
                    # ब्राउज़र का स्पीच सिंथेसिस (बोलने की खूबी) जो ऐप को बोलकर सुनाएगा
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
