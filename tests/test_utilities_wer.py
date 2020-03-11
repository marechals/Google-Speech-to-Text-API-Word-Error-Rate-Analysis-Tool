import utilities.wer
def test_TxtPreprocess():
    raw = 'hello 12-34-56 this 789'
    expected = 'hello 123456 this 789'
    result = utilities.wer.TxtPreprocess(raw)
    assert result == expected
