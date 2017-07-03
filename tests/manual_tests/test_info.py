import setup_test
from bootstrap import app
from plugins.info import InfoManager

# test config
conf = {
    'DEFAULT_PARAMS' : {
        "TEST": {
            'hello': 'world'
        }
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
        print(app.infomanager.get_info('TEST', self))


t = TestParent()
t.test()

# get default params without init object
print(app.infomanager.get_info('TEST'))
