import streamlit as st
from openai import OpenAI
import os
from dotenv import load_dotenv
import requests

# Load API key from environment variable
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

st.set_page_config(
    page_title="Build Your Business - Mr. Stumberg's Class Entrepreneur App",
    layout="wide",
    page_icon="💰"  
)
st.markdown("""
    <style>
        html, body, [class*="css"]  {
            font-family: 'Poppins', sans-serif !important;
            background-color: #111;
            color: #F8F8F8;
        }
        h1 {
            font-size: 3rem !important;
            color: #00E6E6;
            font-weight: bold;
        }
        h3 {
            font-size: 1.5rem !important;
            color: #F8F8F8;
        }
        .stButton > button {
            background-color: #8A2BE2;
            color: white;
            font-weight: bold;
            border-radius: 12px;
            padding: 12px 24px;
            transition: all 0.3s ease-in-out;
        }
        .stButton > button:hover {
            background-color: #1ABC9C;
            transform: scale(1.05);
        }
        .stSlider > div[data-baseweb='slider'] {
            background-color: transparent !important;
            box-shadow: none !important;
        }
        .stSlider > div[data-baseweb='slider'] > div:first-child {
            background: linear-gradient(to right, #FF5C8D, #33C1FF) !important;
            height: 2px !important;
            border-radius: 10px;
        }
        .stSlider > div[data-baseweb='slider'] > div > div > div {
            background-color: #FF5C8D !important;
            border: 2px solid #F8F8F8 !important;
            width: 35px !important;
            height: 35px !important;
        }
        .stRadio > div {
            background-color: #1a1a1a;
            padding: 1rem;
            border-radius: 1rem;
            border: 1px solid #333;
        }
        .stDownloadButton > button {
            background-color: #00E6E6;
            color: black;
            font-weight: bold;
            border-radius: 12px;
            padding: 12px 24px;
            transition: all 0.3s ease-in-out;
        }
        .stDownloadButton > button:hover {
            background-color: #1ABC9C;
            transform: scale(1.05);
        }
        .stTextInput > div > input {
            background-color: #222;
            border-radius: 10px;
            padding: 0.75rem;
            color: white;
        }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <h1>Build Your Business</h1>
    <h3>Mr. Stumberg's Class Entrepreneur App</h3>
""", unsafe_allow_html=True)

if 'step' not in st.session_state:
    st.session_state.step = 1

for key in ['student_name', 'interests', 'business_idea', 'business_name', 'slogan', 'flyer_url']:
    st.session_state.setdefault(key, "" if key != 'interests' else [])

# STEP 1

def step_1():
    st.subheader("Step 1: Pick Interests")
    col1, col2 = st.columns([1, 2])
    with col1:
        st.session_state.student_name = st.text_input("Your name:", value=st.session_state.student_name)
        st.session_state.interests = st.multiselect(
            "Things you love or are great at:",
            ["Reading", "Sports", "Helping", "Animals", "Outdoors", "Coloring", "Art", "Music"],
            default=st.session_state.interests
        )
        if st.button("🎉 Show Ideas"):
            if len(st.session_state.interests) < 2 or not st.session_state.student_name:
                st.warning("Add your name and at least 2 interests!")
                return

            prompt = f"""
            A 1st grader named {st.session_state.student_name} likes {', '.join(st.session_state.interests)}.
            Suggest 3 kid-friendly business ideas they could try now (like dog walking or coloring books) or in the future (like bakery or tutoring). Include fun names and a one-sentence description.
            """
            try:
                response = client.chat.completions.create(
                    model="gpt-4",
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=200
                )
                ideas = response.choices[0].message.content.strip().split("\n")
                st.session_state.ideas = [idea.strip("- ") for idea in ideas if idea]
                st.session_state.step = 2
            except Exception as e:
                st.error(f"Error: {e}")

# STEP 2

def step_2():
    st.subheader("Step 2: Choose a Business Idea")
    if not st.session_state.get("ideas"):
        st.warning("Please go back and generate ideas first.")
        return
    selected_idea = st.radio("Pick your favorite idea:", st.session_state.ideas, key="business_idea_selection")
    st.session_state.business_idea = selected_idea
    creativity = st.slider("Name creativity (1 = simple, 5 = silly)", 1, 5, 3)

    if st.button("🧠 Make Name Ideas"):
        prompt = f"Suggest 3 business names for a kid named {st.session_state.student_name}, based on the idea: '{st.session_state.business_idea}'. Make the names suitable for a first grade student. Creativity level: {creativity}."
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            names = response.choices[0].message.content.strip().split("\n")
            st.session_state.business_names = [n.strip("- ") for n in names if n]
            st.session_state.step = 3
        except Exception as e:
            st.error(f"Error: {e}")

# STEP 3

def step_3():
    st.subheader("Step 3: Pick a Name")
    if not st.session_state.business_names:
        st.error("Please complete Step 2 first.")
        return
    selected_name = st.radio("Which name do you like best?", st.session_state.business_names, key="business_name_selection")
    st.session_state.business_name = selected_name
    if st.button("✨ Get Slogans"):
        name = st.session_state.business_name
        prompt = f"Make 3 slogans for a business called '{selected_name}' run by a 1st grader named {st.session_state.student_name}."
        try:
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            st.session_state.slogans = [s.strip("- ") for s in response.choices[0].message.content.split("\n") if s]
            st.session_state.step = 4
        except Exception as e:
            st.error(f"Error: {e}")

# STEP 4

def step_4():
    if not all([st.session_state.business_name, st.session_state.business_idea, st.session_state.slogans]):
        st.error("Please complete all previous steps before generating a flyer.")
        return

    st.subheader("Step 4: Design Your Flyer")
    st.radio("Pick your slogan:", st.session_state.slogans, key="slogan")
    icon = st.text_input("Add a symbol or small phrase (like 'star', 'paw print')", value="star")
    color1 = st.color_picker("Flyer Color 1", "#FF5733")
    color2 = st.color_picker("Flyer Color 2", "#33C1FF")

    if st.button("🎨 Make My Flyer"):
        business = st.session_state.business_name
        slogan = st.session_state.slogan
        name = st.session_state.student_name or "a 1st grader"

        prompt = (
            f"Design the top half of a colorful flyer for a business called '{business}', run by a 1st grader named {name}. "
            f"Use bold, playful illustrations with limited large readable text. Highlight the business name in big font, "
            f"include the slogan '{slogan}' in a banner or ribbon. Use {color1} and {color2} in the layout. "
            f"Add a visual element like a '{icon}' to help convey the theme. Focus on making it look like a polished kid-made ad."
        )

        try:
            image = client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size="1024x1024",
                quality="standard"
            )
            if image and image.data and image.data[0].url:
                st.session_state.flyer_url = image.data[0].url
                st.image(st.session_state.flyer_url, caption="🎉 Your Flyer!")
                st.balloons()
            else:
                st.error("No image URL returned. Please try again.")
        except Exception as e:
            st.error(f"Error generating image: {e}")

# Control Step Flow
if st.session_state.step == 1:
    step_1()
elif st.session_state.step == 2:
    step_2()
elif st.session_state.step == 3:
    step_3()
elif st.session_state.step == 4:
    step_4()

# Add download option if flyer_url is generated
if st.session_state.get('flyer_url'):
    student = st.session_state.get('student_name', 'student').replace(" ", "_")
    business = st.session_state.get('business_name', 'flyer').replace(" ", "_")
    file_name = f"{student}_{business}_flyer.png"
    st.download_button(
        label="📥 Download Your Flyer",
        data=requests.get(st.session_state.flyer_url).content,
        file_name=file_name,
        mime="image/png"
    )