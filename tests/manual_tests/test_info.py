import setup_test
from bootstrap import app

# require: bootstrap register info module (InfoManager)


class TestParent():
    def init_info(self, key):
        return {'init': 'this is init'}

    def test(self):
        print(app.infomanager.get_info('TEST', self))


t = TestParent()
t.test()

print(app.infomanager.get_info('TEST'))
