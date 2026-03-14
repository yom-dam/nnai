import gradio as gr

def create_theme():
    return gr.themes.Soft(
        primary_hue=gr.themes.colors.blue,
        secondary_hue=gr.themes.colors.teal,
        font=[gr.themes.GoogleFont("Inter"), "sans-serif"],
    ).set(
        button_primary_background_fill="#0C447C",
        button_primary_background_fill_hover="#185FA5",
        button_primary_text_color="white",
    )
