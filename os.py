import os
import time
import torch
import requests
import streamlit as st
from PIL import Image
from dotenv import load_dotenv
from diffusers import StableDiffusionPipeline
import openai 


# --- Load environment variables ---
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

# --- Spotify Credentials (Replace with actual credentials) ---
CLIENT_ID = '7353d5351c904d3e853a9a5f6b3786f0'
CLIENT_SECRET = 'b3b44989da744bd3830d4f82805a457c'

# --- Setup OpenAI client ---
client = None
if OPENAI_API_KEY:
    try:
        client = OpenAI(api_key=OPENAI_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize OpenAI client: {e}")

# --- Functions ---
def generate_invitation(occasion, color_theme, location, custom_song):
    fallback_text = (
        f"Invitation to a {occasion} Party\n\nYou are cordially invited to celebrate with us!\n\n"
        f"Please join us for a {occasion} with a beautiful {color_theme} theme.\nThe event will be held {location}.\n\n"
        "Date: [DATE]\nTime: [TIME]\nLocation: [ADDRESS]\n\nRSVP: [CONTACT]\n\nWe look forward to celebrating with you!"
    )

    if not OPENAI_API_KEY or client is None:
        return fallback_text

    prompt = (
        f"Create a formal and elegant invitation for a {occasion} party with a {color_theme} color theme.\n"
        f"The event will be held {location}.\n\n"
        "The invitation should include:\n"
        "- A catchy headline\n"
        "- An elegant and warm welcome message\n"
        "- A section for event details (placeholders for date, time, address)\n"
        "- RSVP instructions\n\n"
        "Make it sound festive and exciting but also sophisticated."
    )

    if custom_song.lower() == 'yes':
        prompt += "\nAlso mention that there will be a special musical performance."

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an expert party planner and invitation writer with an elegant style."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        return fallback_text

def generate_party_image(occasion, color_theme, location):
    model_id = "SG161222/Realistic_Vision_V5.1_noVAE"
    device = "cuda" if torch.cuda.is_available() else "cpu"
    dtype = torch.float16 if device == "cuda" else torch.float32

    pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
    pipe.to(device)

    prompt = (
        f"A beautiful and elegant {occasion} party decoration with a {color_theme} theme in an {location} setting. "
        f"Include tables, lights, flowers. Photorealistic. "
        f"A close-up of a themed centerpiece for a {occasion} celebration with {color_theme} colors in an {location} environment. "
        "Soft lighting, artistic photography."
    )

    image = pipe(prompt).images[0]
    time.sleep(2)

    output_dir = "generated_images"
    os.makedirs(output_dir, exist_ok=True)

    image_filename = f"generated_{occasion.lower()}{color_theme.lower()}.png".replace(" ", "")
    image_path = os.path.join(output_dir, image_filename)
    image.save(image_path)

    return image_path

def get_token(client_id, client_secret):
    auth_url = "https://accounts.spotify.com/api/token"
    auth_response = requests.post(
        auth_url,
        data={"grant_type": "client_credentials"},
        auth=(client_id, client_secret),
    )
    return auth_response.json().get("access_token")

def search_track(song_name, token):
    headers = {"Authorization": f"Bearer {token}"}
    params = {"q": song_name, "type": "track", "limit": 1}
    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    tracks = response.json().get("tracks", {}).get("items", [])
    return tracks[0] if tracks else None

# --- Streamlit UI ---
st.set_page_config(page_title="🎨 AI Party Designer", layout="centered")
st.title("🎉 AI Party Designer")

occasion = st.text_input("Occasion (e.g., Birthday, Wedding)")
color_theme = st.text_input("Color Theme (e.g., Pink, Gold)")
location = st.text_input("Location (e.g., Indoors, Beachside Garden, Rooftop)")
custom_song = st.selectbox("Include Musical Performance?", ["No", "Yes"])
song_name = st.text_input("Enter a song name to embed from Spotify (optional)")

if st.button("Generate Invitation & Image"):
    if not all([occasion, color_theme, location]):
        st.error("Please fill in all fields.")
    else:
        with st.spinner("Generating invitation..."):
            invitation_text = generate_invitation(occasion, color_theme, location, custom_song)
            st.subheader("📝 Your Party Invitation")
            st.text_area("Generated Invitation", invitation_text, height=300)

        with st.spinner("Creating party design image..."):
            image_path = generate_party_image(occasion, color_theme, location)
            st.image(image_path, caption="Generated Party Design", use_column_width=True)

        if song_name:
            token = get_token(CLIENT_ID, CLIENT_SECRET)
            track = search_track(song_name, token)

            if track:
                track_name = track["name"]
                artists = ", ".join([artist["name"] for artist in track["artists"]])
                album_name = track["album"]["name"]
                track_id = track["id"]
                spotify_url = track["external_urls"]["spotify"]
                embed_url = f"https://open.spotify.com/embed/track/{track_id}"

                st.subheader("🎧 Selected Song")
                st.markdown(f"**Track**: {track_name}")
                st.markdown(f"**Artists**: {artists}")
                st.markdown(f"**Album**: {album_name}")
                st.markdown(f"[🔗 Open in Spotify]({spotify_url})")

                st.subheader("▶️ Preview (Embed)")
                st.markdown(
                    f"""
                    <iframe src=\"{embed_url}\" width=\"300\" height=\"80\" frameborder=\"0\"
                    allowtransparency=\"true\" allow=\"encrypted-media\"></iframe>
                    """,
                    unsafe_allow_html=True
                )
            else:
                st.warning("No track found. Try a different song name.")

#---------------------------------------------------------------------------------------------------------------

# Invitation & image code

# import os
# import time
# import torch
# import streamlit as st
# from PIL import Image
# from dotenv import load_dotenv
# import openai
# from diffusers import StableDiffusionPipeline

# # --- Load .env and Initialize OpenAI ---
# load_dotenv()
# api_key = os.getenv("OPENAI_API_KEY=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")

# client = None
# if api_key:
#     try:
#         client = OpenAI(api_key=api_key)
#     except Exception as e:
#         st.error(f"Error initializing OpenAI client: {e}")

# # --- Streamlit Config ---
# st.set_page_config(page_title="🎨 AI Party Designer", layout="centered")
# st.title("🎉 AI Party Designer")

# # --- Inputs ---
# occasion = st.text_input("Occasion (e.g., Birthday, Wedding)")
# color_theme = st.text_input("Color Theme (e.g., Pink, Gold)")
# location = st.text_input("Location (e.g., Indoors, Beachside Garden, Rooftop)")
# custom_song = st.selectbox("Include Musical Performance?", ["No", "Yes"])


# # --- Generate Invitation Text ---
# def generate_invitation(occasion, color_theme, location, custom_song):
#     fallback_text = (
#         f"Invitation to a {occasion} Party\n\nYou are cordially invited to celebrate with us!\n\n"
#         f"Please join us for a {occasion} with a beautiful {color_theme} theme.\nThe event will be held {location}.\n\n"
#         "Date: [DATE]\nTime: [TIME]\nLocation: [ADDRESS]\n\nRSVP: [CONTACT]\n\nWe look forward to celebrating with you!"
#     )

#     if not api_key or client is None:
#         return fallback_text

#     prompt = (
#         f"Create a formal and elegant invitation for a {occasion} party with a {color_theme} color theme.\n"
#         f"The event will be held {location}.\n\n"
#         "The invitation should include:\n"
#         "- A catchy headline\n"
#         "- An elegant and warm welcome message\n"
#         "- A section for event details (placeholders for date, time, address)\n"
#         "- RSVP instructions\n\n"
#         "Make it sound festive and exciting but also sophisticated."
#     )

#     if custom_song.lower() == 'yes':
#         prompt += "\nAlso mention that there will be a special musical performance."

#     try:
#         response = client.chat.completions.create(
#             model="gpt-4",
#             messages=[
#                 {"role": "system", "content": "You are an expert party planner and invitation writer with an elegant style."},
#                 {"role": "user", "content": prompt}
#             ],
#             max_tokens=500
#         )
#         print(response.choices[0].message.content.strip())
#         return response.choices[0].message.content.strip()
#     except Exception as e:
#         return f"[Error generating invitation: {e}]\n\n{fallback_text}"


# # --- Generate Design Image ---
# def generate_party_image(occasion, color_theme, location):
#     model_id = "SG161222/Realistic_Vision_V5.1_noVAE"
#     device = "cuda" if torch.cuda.is_available() else "cpu"
#     dtype = torch.float16 if device == "cuda" else torch.float32

#     pipe = StableDiffusionPipeline.from_pretrained(model_id, torch_dtype=dtype)
#     pipe.to(device)

#     prompt = (
#         f"A beautiful and elegant {occasion} party decoration with a {color_theme} theme in an {location} setting. "
#         f"Include tables, lights, flowers. Photorealistic. "
#         f"A close-up of a themed centerpiece for a {occasion} celebration with {color_theme} colors in an {location} environment. "
#         "Soft lighting, artistic photography."
#     )

#     image = pipe(prompt).images[0]
#     time.sleep(2)

#     output_dir = "generated_images"
#     os.makedirs(output_dir, exist_ok=True)

#     image_filename = f"generated_{occasion.lower()}{color_theme.lower()}.png".replace(" ", "")
#     image_path = os.path.join(output_dir, image_filename)
#     image.save(image_path)

#     return image_path

# # --- Button Actions ---
# if st.button("Generate Invitation & Image"):
#     if not all([occasion, color_theme, location]):
#         st.error("Please fill in all fields.")
#     else:
#         with st.spinner("Generating invitation..."):
#             invitation_text = generate_invitation(occasion, color_theme, location, custom_song)
#             st.subheader("📝 Your Party Invitation")
#             st.text_area("Generated Invitation", invitation_text, height=300)

#         with st.spinner("Creating party design image..."):
#             image_path = generate_party_image(occasion, color_theme, location)
#             st.image(image_path, caption="Generated Party Design", use_column_width=True)
