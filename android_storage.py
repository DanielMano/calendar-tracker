from kivy.utils import platform


def get_permissions():
    if platform == "android":
        from android.permission import request_permissions, Permission

        request_permissions([Permission.READ_EXTERNAL_STORAGE])


class Storage:
    def __init__(self, root) -> None:
        self.root = root
        if platform == "android":
            from androidstorage4kivy import SharedStorage, Chooser

            self.chooser = Chooser(self.chooser_callback)
            self.ss = SharedStorage()
        else:
            self.chooser = None
        self.path = None

    def chooser_start(self):
        if platform == "android":
            self.chooser.choose_content("*/*")
            return True
        else:
            self.root.copied_db_path = "test change"
        return False

    def chooser_callback(self, shared_files):
        try:
            for shared_file in shared_files:
                self.path = self.ss.copy_from_shared(shared_file)
                self.root.copied_db_path = self.path
        except Exception as e:
            pass

    def save_file(self, path, new_file_name):
        if platform == "android":
            self.shared = self.ss.copy_to_shared(path, filepath=new_file_name)
            return True
        return False
