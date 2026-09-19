import pytest

from src.preprocessing import TextPreprocessor


@pytest.fixture
def processor():
    return TextPreprocessor()


def test_lowercases(processor):
    assert processor.clean_text("HELLO WORLD") == "hello world"


def test_punctuation_becomes_spaces(processor):
    assert processor.clean_text("first-aid") == "first aid"
    assert processor.clean_text("music/noise") == "music nois"
    assert processor.clean_text("co-ed") == "co ed"


def test_stopwords_removed(processor):
    assert processor.clean_text("what are the gym timings") == "gym time"


def test_synonyms_normalized(processor):
    assert processor.clean_text("membership price?") == "membership cost"
    assert processor.clean_text("pause membership") == "freez membership"


def test_steaming_of_plurals(processor):
    assert processor.clean_text("classes") == "class"
    assert processor.clean_text("facilities") == "facil"


def test_24_7_normalized(processor):
    assert processor.clean_text("open 24/7") == "open 247"


def test_covid_normalized(processor):
    assert processor.clean_text("covid-19 policy") == "covid polici"