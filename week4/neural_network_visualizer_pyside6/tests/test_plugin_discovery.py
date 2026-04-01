import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

def test_discover_labs_finds_four():
    from launcher.launcher_window import discover_labs
    labs = discover_labs()
    assert len(labs) == 4

def test_discover_labs_have_required_keys():
    from launcher.launcher_window import discover_labs
    for meta in discover_labs():
        assert "id" in meta
        assert "title" in meta
        assert "icon" in meta
        assert "description" in meta
        assert "window_class" in meta
