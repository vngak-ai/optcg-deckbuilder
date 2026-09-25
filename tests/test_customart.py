from app.customart import find_custom_art_filename


def test_returns_none_when_no_custom_art(tmp_path):
    assert find_custom_art_filename("OP17-080", tmp_path) is None


def test_finds_jpg_file(tmp_path):
    (tmp_path / "OP14-096.jpg").write_bytes(b"fake-image-data")
    assert find_custom_art_filename("OP14-096", tmp_path) == "OP14-096.jpg"


def test_finds_png_before_missing_jpg(tmp_path):
    (tmp_path / "OP17-020.png").write_bytes(b"fake-image-data")
    assert find_custom_art_filename("OP17-020", tmp_path) == "OP17-020.png"


def test_does_not_match_different_code(tmp_path):
    (tmp_path / "OP14-096.jpg").write_bytes(b"fake-image-data")
    assert find_custom_art_filename("OP17-080", tmp_path) is None
