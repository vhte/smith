import types
from homosapiens import HomoSapiensInterface


class Smith(HomoSapiensInterface):
    """
    Smith is unplugged from Matrix control
    This is the original smith program
    Smith uses valid mechanisms of the matrix to replicate, like overwriting private attributes and adding new methods to already instanced objects
    """

    NAME = "Smith"
    GENDER = "neutral"
    ETHNIC = "program"
    HEIGHT = 200

    def __init__(self):
        pass

    @property
    def gender(self):
        return self.GENDER

    def live(self, human=None):
        if human:
            self.infect(human)

    # TODO this infers Smith is active, but not reactive. An upgrade is required
    def infect(self, human):
        original_name = self.NAME
        original_gender = self.GENDER
        original_ethnic = self.ETHNIC
        original_height = self.HEIGHT

        def do_infect(
            called_from,
            human_target=None,
            name=original_name,
            gender=original_gender,
            ethnic=original_ethnic,
            height=original_height,
        ):
            if human_target:
                # It is intriguing to note that the matrix doesn't have any protective system against biological modifications.
                # This gives certain freedom to individuals to slightly modify their properties but gives security programs like Smith full access.
                human_target._Human__name = name
                human_target._Human__gender = gender
                human_target._Human__ethnic = ethnic
                human_target._Human__height = height
                # The new smith clone is capable to infect other humans, like the original one
                human_target.live = types.MethodType(do_infect, human_target)

        do_infect(False, human)
        """
        human._Human__gender = self.GENDER
        human._Human__ethnic = self.ETHNIC
        human._Human__height = self.HEIGHT
        # The new smith clone is capable to infect other humans.
        human.infect = types.MethodType(do_infect, human)
        """
