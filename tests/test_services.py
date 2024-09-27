# import unittest
# from sqthon.services import start_service, stop_service, is_service_running
#
#
# class TestServices(unittest.TestCase):
#
#     def test_service_is_running(self):
#         """
#         Test if the service is running (positive case).
#         """
#         self.assertTrue(is_service_running("MySQL84"))
#
#     def test_service_is_not_running(self):
#         """
#         Test if the service is not running (negative case).
#         """
#
#         self.assertFalse(is_service_running("MySQL84"))
#
#
# if __name__ == "__main__":
#     unittest.main()


# cmd = "net start sql"
# cmd = cmd.split()

# re = " ".join(f'"{x}"' for x in cmd[1:])
# print(re)


import sys
print(sys.executable)


from sqthon.admin import _is_admin

print(_is_admin)
