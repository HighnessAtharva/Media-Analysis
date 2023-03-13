import json
import os

import regex as re
import streamlit as st
from lyricsgenius import Genius


def genius_to_json(album, artist):

    try:
        response = genius.search_album(name=album, artist=artist)
        os.chdir("csvs/genius/")
        response.save_lyrics(f"{album} By {artist}")
        os.chdir("../..")
    except AttributeError:
        st.error(
            f"Sorry, we couldn't find any lyrics for {album} by {artist} on Genius. Please try again."
        )
        st.stop()


def JSON_to_MD(album, artist):
    with open(f"csvs/genius/{album} By {artist}.json", "r", encoding="utf-8") as f:
        albumJSON = json.loads(f.read())

        title = albumJSON["full_title"]
        cover = albumJSON["cover_art_url"]
        tracks = albumJSON["tracks"]
        songID = [track["song"]["id"] for track in tracks]
        songs = [track["song"]["title"] for track in tracks]
        raw_lyrics = [track["song"]["lyrics"] for track in tracks]
        lyrics = [track["song"]["lyrics"] for track in tracks]

        lyrics = [re.sub("Translations(.*)Lyrics", "Lyrics", lyric) for lyric in lyrics]
        lyrics = [lyric.replace("Lyrics", "Lyrics\n\n") for lyric in lyrics]
        lyrics = [re.sub("Embed", "", lyric) for lyric in lyrics]
        lyrics = [lyric.replace("\n", "\n\n  ") for lyric in lyrics]

        with open(f"csvs/genius/{album} By {artist}.md", "w", encoding="utf-8") as f2:
            f2.write(f"# {title}  ")
            # if cover:
            #     f2.write(f"\n\n![Cover of {album}]({cover})")
            f2.write(f"\n\nTotal Songs: {len(songs)}")
            f2.write("\n___________________\n")

            zipper = zip(songID, songs, lyrics)
            for songID, song, lyrics in zipper:
                # TITLE
                f2.write(f"\n## {song}\n\n")

                # LYRICS
                if lyrics:
                    lyrics = lyrics.replace("Lyrics", "")
                    f2.write(lyrics)
                else:
                    f2.write("**Lyrics not available**")

                # ANNOTATIONS
                myDict = {}
                annotationsList = genius.song_annotations(
                    song_id=songID, text_format="markdown"
                )

                for annotation in annotationsList:
                    raw_lyrics, explanation = annotation
                    explanation = explanation[0][0]
                    myDict[raw_lyrics] = explanation

                for key, value in myDict.items():
                    f2.write(f"\n### {key}\n  ")
                    f2.write("\n```ANNOTATION:```\n")
                    f2.write(f">{value}  ")

                f2.write("\n\n___________________\n")


def MD_to_PDF(album, artist):
    os.chdir("csvs/genius")
    os.system(f'mdpdf -o "{album} By {artist}.pdf" "{album} By {artist}.md"')
    os.remove("mdpdf.log")
    os.chdir("../..")


# PAGE CONFIG
st.set_page_config(
    page_title="Genius Lyrics To PDF",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# PAGE TITLE
st.title(":green[Genius] Lyrics to PDF :studio_microphone:")

# INTRO
st.markdown(
    """   

🎶 Are you tired of having to search for lyrics and annotations for every track of your favorite album? Look no further! 🚀 Our new tool allows you to easily export the lyrics and annotations for any desired album into a rich Markdown format or a PDF file to read on the go. 📝📱

💿 All you have to do is input the album name and the artist name, and our tool will generate a markdown/PDF file with the lyrics and annotations for every track off the album. No more wasted time searching for lyrics online or trying to decipher song meanings on your own - our tool has got you covered. 💪

🎵 Whether you're a music enthusiast, a musician, or simply someone who loves to sing along to their favorite songs, our tool is perfect for you. 🎤 It's quick, easy, and hassle-free, allowing you to enjoy your favorite music even more. 🎧

🎉 Try our tool today and see for yourself how it can enhance your musical experience. Don't miss out on the chance to have all the lyrics and annotations for your favorite albums at your fingertips! 👍
    """
)

st.write("---")
st.info(
    "All the data will be gathered from [Genius](https://genius.com/), a popular lyrics website. We are not affiliated with Genius in any way. Any issue with the lyrics or annotations should be reported to Genius."
)

album = st.text_input("Album Name", placeholder="Enter the album name")
artist = st.text_input("Artist Name", placeholder="Enter the artist name")

btn = st.button("Get the Lyrics and Annotations", key="genius")

if len(album) and len(artist) >= 2 and btn:

    # genius_access_token = st.secrets["GENIUS_CLIENT_ACCESS_TOKEN"]

    # instantiate genius object
    genius = Genius("pCgIOvoAnE1lYO2v5bwvFQGbPDWpyChM4iCTu6174fWJ9kJzmZJ3L1VrFkBe91rR")

    with st.spinner(
        f"Getting Lyrics and Annotations from Genius for {album} by {artist}..."
    ):
        if not os.path.exists(f"csvs/genius/{album} By {artist}.json"):
            genius_to_json(album, artist)

    with st.spinner("Preparing the Markdown file..."):
        JSON_to_MD(album, artist)

    with st.spinner("Preparing the PDF file..."):
        MD_to_PDF(album, artist)

    st.success("Your files are ready! 🎉")

    st.warning(
        "Please Note: The PDF can have some issues with the formatting and can fail halfway in rare cases. If you are not satisfied with the output, please download the Markdown file and use a Markdown to PDF converter."
    )

    with open(f"csvs/genius/{album} By {artist}.pdf", "rb") as f:
        st.download_button(
            label="Download PDF",
            data=f,
            file_name=f"{album} By {artist}.pdf",
            mime="application/pdf",
        )

    with open(f"csvs/genius/{album} By {artist}.md", "rb") as f:
        st.download_button(
            label="Download Markdown",
            data=f,
            file_name=f"{album} By {artist}.md",
            mime="text/markdown",
        )
