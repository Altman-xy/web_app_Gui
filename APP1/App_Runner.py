from APP1.App import MobileTest

class App_Run:

    def __init__(self):
        pass


    def App_login(self,time):
        mt = MobileTest()
        mt.login(time)


if __name__ == '__main__':
    AC = App_Run()
    AC.App_login(0)

