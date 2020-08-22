from src.utils import get_title, get_crystal

class TestUtils:
    JEDI = 'Jedi'
    SITH = 'Sith'
    OBSIDIAN = 'Obsidian'
    GEM = 'Dragite gem'

    single_type = {
        'type': JEDI,
        'crystal': OBSIDIAN,
    }
    array_type = {
        'type': [JEDI, SITH],
        'crystal': [OBSIDIAN, GEM]
    }

    def test_get_string_title(self):
        name = get_title(self.single_type)
        assert name == self.JEDI

    def test_get_array_title(self):
        name = get_title(self.array_type)
        assert name in [self.JEDI, self.SITH]

    def test_get_string_crystal(self):
        crystal = get_crystal(self.single_type)
        assert crystal == self.OBSIDIAN

    def test_get_array_crystal(self):
        crystal = get_crystal(self.array_type)
        assert crystal in [self.OBSIDIAN, self.GEM]