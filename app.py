import streamlit as st
import streamlit.components.v1 as components
from google import genai
import json
import time

# पेज सेटअप
st.set_page_config(page_title="FormulaSaathi & Teacher Pro", layout="wide")

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

# सीधे Streamlit Secrets से API Key ले लेगा (सुरक्षित तरीका)
api_key = st.secrets.get("GEMINI_API_KEY")

with st.sidebar:
    st.header("🚀 FormulaSaathi Pro")
    st.markdown("---")
    st.markdown("**Platform Features:**\n1. Ultra Fast Speed\n2. Unlimited Questions\n3. Clean Text Format")

st.title("🚀 FormulaSaathi & Teacher Pro Suite")

tab1, tab2 = st.tabs(["👨‍🎓 Student Free Zone", "👨‍🏫 Teacher A4 Question Paper Generator"])

# स्मार्ट और सुपर-फास्ट ऑटो-रिट्राई फंक्शन (सिर्फ असली और तेज मॉडल के साथ)
def call_gemini_with_smart_retry(client, prompt_text):
    # गूगल का सबसे तेज और स्थिर मॉडल
    models_to_try = ["gemini-1.5-flash"]
    
    for attempt in range(3): # कुल 3 बार कोशिश करेगा
        for m in models_to_try:
            try:
                response = client.models.generate_content(model=m, contents=prompt_text)
                if response and response.text:
                    return response.text
            except Exception as e:
                time.sleep(1) # 1 सेकंड रुककर दोबारा प्रयास करेगा
                continue
    return None

# ==========================================
# TAB 1: STUDENT FREE ZONE
# ==========================================
with tab1:
    st.subheader("💡 Smart Doubt & Numerical Solver")
    
    col_s1, col_s2 = st.columns([1, 2])
    with col_s1:
        stu_class = st.selectbox("अपनी कक्षा / परीक्षा चुनें", CLASSES_LIST, key="s_class")
        stu_subject = st.selectbox("विषय चुनें (Subject)", ALL_SUBJECTS, key="s_sub")
        stu_lang = st.radio("माध्यम चुनें (Medium)", LANGUAGES_LIST, key="s_lang")
    
    with col_s2:
        student_query = st.text_area(
            "अपना सवाल या चैप्टर यहाँ लिखें:", 
            height=140, 
            placeholder="उदाहरण: \n1. Explain laws of motion...\n2. गति के नियमों को समझाएं..."
        )
    
    if st.button("🔍 तुरंत हल देखें"):
        if not api_key:
            st.error("⚠️ कृपया Streamlit Secrets में GEMINI_API_KEY सेट करें!")
        elif stu_class == "--- कक्षा चुनें ---" or stu_subject == "--- कृपया विषय चुनें (Select Subject) ---":
            st.warning("⚠️ कृपया पहले सही कक्षा और विषय चुनें!")
        elif not student_query.strip():
            st.warning("⚠️ कृपया अपना सवाल लिखें।")
        else:
            with st.spinner("⚡ AI समाधान तैयार कर रहा है (सुपर-फास्ट मोड सक्रिय है)..."):
                try:
                    client = genai.Client(api_key=api_key)
                    prompt = f"""
                    Expert tutor for {stu_class} studying {stu_subject}.
                    Language: {stu_lang}. No dollar signs ($) or raw LaTeX. Use clean text (e.g., x^2).
                    Query: {student_query}.
                    Provide clear steps and 1 practice question.
                    """
                    res_text = call_gemini_with_smart_retry(client, prompt)
                    if res_text:
                        st.success("✅ समाधान तैयार है!")
                        st.markdown(res_text)
                    else:
                        st.warning("⚠️ सर्वर अभी अत्यधिक व्यस्त है। कृपया एक बार फिर से बटन पर क्लिक करें।")
                except Exception as e:
                    st.error(f"त्रुटि (Error): {e}")

# ==========================================
# TAB 2: TEACHER A4 QUESTION PAPER GENERATOR
# ==========================================
with tab2:
    st.subheader("📄 सुपर-फास्ट A4 क्वेश्चन पेपर जनरेटर")
    
    st.markdown("#### 1. परीक्षा और माध्यम का विवरण")
    c1, c2, c3, c4 = st.columns(4)
    with c1:
        coaching_name = st.text_input("कोचिंग / संस्थान का नाम (Optional)", value="", placeholder="कोचिंग का नाम (या खाली छोड़ें)")
    with c2:
        t_class = st.selectbox("कक्षा / परीक्षा स्तर", CLASSES_LIST, index=10, key="t_class")
    with c3:
        t_subject = st.selectbox("विषय (Subject)", ALL_SUBJECTS, key="t_sub")
    with c4:
        topic_name = st.text_input("चैप्टर / टॉपिक या 'Chapter 1'", placeholder="जैसे: Chapter 1, Newton Laws...")

    c5, c6, c7, c8 = st.columns(4)
    with c5:
        exam_time = st.text_input("समय (Time Allowed)", value="2 Hours")
    with c6:
        difficulty = st.selectbox("कठिनाई स्तर (Level)", ["Board Standard", "Medium", "Hard", "IIT-JEE / NEET Advanced"])
    with c7:
        paper_lang = st.selectbox("प्रश्न-पत्र का माध्यम (Medium)", LANGUAGES_LIST, key="t_lang")
    with c8:
        paper_size = st.selectbox("पेज साइज (Print Format)", ["A4", "Legal", "Letter"])

    st.markdown("#### 2. प्रश्नों की संख्या चुनें (खाली छोड़ने पर स्वतः 0 माना जाएगा)")
    q1, q2, q3, q4, q5 = st.columns(5)
    
    with q1:
        mcq_str = st.text_input("MCQ (1 अंक)", value="5")
        mcq_q = int(mcq_str.strip()) if mcq_str.strip().isdigit() else 0
    with q2:
        fib_str = st.text_input("Fill in Blanks (1 अंक)", value="5")
        fib_q = int(fib_str.strip()) if fib_str.strip().isdigit() else 0
    with q3:
        two_str = st.text_input("2-अंक वाले प्रश्न", value="3")
        two_m_q = int(two_str.strip()) if two_str.strip().isdigit() else 0
    with q4:
        three_str = st.text_input("3-अंक वाले प्रश्न", value="2")
        three_m_q = int(three_str.strip()) if three_str.strip().isdigit() else 0
    with q5:
        five_str = st.text_input("5-अंक वाले प्रश्न", value="2")
        five_m_q = int(five_str.strip()) if five_str.strip().isdigit() else 0

    calculated_marks = (mcq_q * 1) + (fib_q * 1) + (two_m_q * 2) + (three_m_q * 3) + (five_m_q * 5)
    total_questions = mcq_q + fib_q + two_m_q + three_m_q + five_m_q
    
    st.info(f"📊 **कुल प्रश्न: {total_questions} | कुल पूर्णांक: {calculated_marks} अंक**")

    include_answers = st.checkbox("अलग पेज पर टीचर के लिए Answer Key (उत्तर माला) भी जोड़ें", value=True)

    if st.button("✨ सुपर-फास्ट A4 क्वेश्चन पेपर तैयार करें"):
        if not api_key:
            st.error("⚠️ कृपया Streamlit Secrets में GEMINI_API_KEY सेट करें!")
        elif t_class == "--- कक्षा चुनें ---" or t_subject == "--- कृपया विषय चुनें (Select Subject) ---":
            st.warning("⚠️ कृपया पहले सही कक्षा और विषय चुनें!")
        elif not topic_name.strip():
            st.warning("⚠️ कृपया चैप्टर का नाम या 'Chapter 1' लिखें!")
        elif total_questions == 0:
            st.warning("⚠️ कृपया कम से कम किसी एक सेक्शन में प्रश्नों की संख्या दर्ज करें!")
        else:
            with st.spinner("⚡ प्रश्न-पत्र जनरेट हो रहा है (सुपर-फास्ट गति सक्रिय है)..."):
                try:
                    client = genai.Client(api_key=api_key)
                        
                    t_prompt = f"""
                    Generate exam Question Paper in clean HTML format (ONLY inner HTML tags like <h4>, <ol>, <li>, <p>, NO <html>, <head>, <body> tags, and NO markdown ```html fences).
                    
                    Language: {paper_lang}. Strictly use this language.
                    No dollar signs ($) or raw LaTeX. Use clean text (e.g., x^2).
                    Class: {t_class}, Subject: {t_subject}, Topic: {topic_name}, Difficulty: {difficulty}.
                    
                    Sections:
                    1. Section A (MCQ - 1 Mark): {mcq_q} questions. Options A, B, C, D on a single line.
                    2. Section B (Fill in Blanks - 1 Mark): {fib_q} questions.
                    3. Section C (2 Marks): {two_m_q} questions.
                    4. Section D (3 Marks): {three_m_q} questions.
                    5. Section E (5 Marks): {five_m_q} questions.
                    
                    - {"At the end, insert <div style='page-break-before: always; border-top: 1px dashed #000; margin-top: 15px; padding-top: 10px;'><h4>Answer Key (उत्तर माला)</h4></div> with brief answers." if include_answers else ""}
                    """
                    
                    res_html = call_gemini_with_smart_retry(client, t_prompt)
                    
                    if res_html:
                        clean_questions_html = res_html.replace("```html", "").replace("```", "").strip()
                        coaching_header = f"<div class='coaching-title'>{coaching_name.strip()}</div>" if coaching_name.strip() else ""
                        
                        full_a4_html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Question_Paper_{t_class}</title>
<style>
    @page {{ size: {paper_size}; margin: 10mm 12mm; }}
    body {{ font-family: 'Times New Roman', 'Nirmala UI', serif; font-size: 11pt; line-height: 1.3; color: #000; background: #fff; margin: 0; padding: 0; }}
    .paper-box {{ width: 100%; box-sizing: border-box; }}
    .coaching-title {{ text-align: center; font-size: 15pt; font-weight: bold; text-transform: uppercase; margin-bottom: 2px; }}
    .sub-header {{ text-align: center; font-size: 11.5pt; font-weight: bold; margin-bottom: 4px; }}
    .meta-bar {{ display: flex; justify-content: space-between; font-size: 10.5pt; font-weight: bold; border-top: 1px solid #000; border-bottom: 1.5px solid #000; padding: 3px 0; margin-bottom: 8px; }}
    h4 {{ font-size: 11.5pt; margin: 8px 0 4px 0; text-decoration: underline; }}
    ol {{ margin: 0 0 6px 0; padding-left: 20px; }}
    li {{ margin-bottom: 4px; text-align: justify; }}
    p {{ margin: 2px 0; }}
</style>
</head>
<body>
    <div class="paper-box">
        {coaching_header}
        <div class="sub-header">{t_class} | Subject: {t_subject} ({topic_name}) [{paper_lang}]</div>
        <div class="meta-bar">
            <span>Time: {exam_time}</span>
            <span>Full Marks: {calculated_marks}</span>
        </div>
        <div class="questions-area">
            {clean_questions_html}
        </div>
    </div>
</body>
</html>"""

                        st.success("✅ आपका A4 प्रश्न-पत्र तैयार है!")
                        safe_html_json = json.dumps(full_a4_html)
                        
                        col_btn1, col_btn2 = st.columns([1, 1])
                        with col_btn1:
                            components.html(f"""
                            <script>
                            function printA4Paper() {{
                                var htmlContent = {safe_html_json};
                                var printWin = window.open('', '_blank', 'width=900,height=700');
                                printWin.document.open();
                                printWin.document.write(htmlContent);
                                printWin.document.close();
                                printWin.focus();
                                setTimeout(function() {{ printWin.print(); }}, 400);
                            }}
                            </script>
                            <button onclick="printA4Paper()" style="background-color: #1a73e8; color: white; padding: 10px 18px; font-size: 15px; font-weight: bold; border: none; border-radius: 6px; cursor: pointer; width: 100%;">
                                🖨️ एक क्लिक में A4 Print / Save as PDF करें
                            </button>
                            """, height=55)
                            
                        with col_btn2:
                            st.download_button(
                                label="📥 ऑफलाइन प्रिंट फाइल डाउनलोड करें (.html)",
                                data=full_a4_html,
                                file_name=f"{t_class.replace(' ', '_')}_{t_subject.split()[0]}_Question_Paper.html",
                                mime="text/html",
                                use_container_width=True
                            )

                        st.markdown("##### 📄 लाइव A4 प्रिंट प्रीव्यू:")
                        components.html(full_a4_html, height=650, scrolling=True)
                    else:
                        st.error("⚠️ सर्वर पर अत्यधिक लोड होने के कारण उत्तर नहीं मिल पाया। कृपया पुनः प्रयास करें।")

                except Exception as e:
                    st.error(f"त्रुटि (Error): {e}")
