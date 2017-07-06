from bootstrap import app
from plugins.info import InfoManager

# test config
conf = {
    'DEFAULT_PARAMS': {
        "TEST": {
            'hello': 'world'
        },
        "other": [
            "TEST"
        ]
    }
}

# require: bootstrap register info module (InfoManager)
app.config_from_dict(conf)

infomanager = InfoManager()
infomanager.init_app(app)

# get default params with init object
# need implement init_info funtion


class TestParent():
    def init_info(self, key):
        return {'init': 'this is init'}

    def test(self):
        return app.infomanager.get_info('TEST', self)


t = TestParent()
rl = t.test()
assert rl['init'] == 'this is init'
assert 'hello' in rl

# get default params without init object
rl2 = app.infomanager.get_info('TEST')
assert 'init' not in rl2

obj = {'init': 'this is init'}
rl3 = app.infomanager.patch_info('TEST', obj)
assert 'init' in rl3
assert 'hello' in rl3

# test default reference
rl4 = app.infomanager.get_info('other')
assert 'hello' in rl4
assert 'TEST' not in rl4
