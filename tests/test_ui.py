def test_create_theme_returns_gradio_theme():
    import gradio as gr
    from ui.theme import create_theme
    theme = create_theme()
    assert isinstance(theme, gr.themes.Base)

def test_create_layout_returns_blocks():
    import gradio as gr
    from ui.layout import create_layout
    dummy_fn = lambda *args: ("결과 마크다운", None)
    demo = create_layout(dummy_fn)
    assert isinstance(demo, gr.Blocks)

def test_create_layout_has_correct_inputs():
    import gradio as gr
    from ui.layout import create_layout
    demo = create_layout(lambda *a: ("", None))
    component_types = {type(c).__name__ for c in demo.blocks.values()}
    assert "Dropdown"      in component_types
    assert "Slider"        in component_types
    assert "CheckboxGroup" in component_types
    assert "Radio"         in component_types
