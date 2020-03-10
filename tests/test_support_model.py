def test_get_support_dict():
    from model.support_model import Support
    support = Support()
    result = support.get_feature_dict()
    expected = dict
    assert type(result) == expected
