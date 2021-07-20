import re
import os


class Base:
    def __init__(self):
        self.state = True

    def replace_string(content, indexlist, strnew):
        length = len(content)
        contentlist = list(content)
        newlist = contentlist[0:indexlist[0]] + list(strnew) + contentlist[indexlist[1]:length]
        return ''.join(newlist)

    def sub_string(content, indexlist, strold, strnew):
        length = len(content)
        listcont = list(content)
        startstr = ''.join(listcont[0:indexlist[0]])
        substr = ''.join(listcont[indexlist[0]:indexlist[1]])
        remainstr = ''.join(listcont[indexlist[1]:length])

        substr = re.sub(r'(?P<start>[^a-zA-Z0-9_]+?)' + strold + r'(?P<end>[^a-zA-Z0-9_]+?)', r'\g<start>'+strnew+r'\g<end>', substr)

        # searched = re.search(r'([^a-zA-Z0-9]+?)' + strold + r'([^a-zA-Z0-9]+?)', substr)
        # while searched:
        #     indexs = [searched.span(1)[1], searched.span(2)[0]]
        #     length = len(substr)
        #     contentlist = list(substr)
        #     newlist = contentlist[0:indexs[0]] + list(strnew) + contentlist[indexs[1]:length]
        #     substr = ''.join(newlist)
        #     searched = re.search(r'([^a-zA-Z0-9]+?)' + strold + r'([^a-zA-Z0-9]+?)', substr)

        return startstr + substr + remainstr

    @classmethod
    def archive_pre_scan(cls, dir, archive_time_stamps):
        workspace = dir
        all_file_folder = os.listdir(workspace)

        # {'absolute file path': file modification time}
        # archive_time_stamps = {}
        for file_folder in all_file_folder:
            file_folder = os.path.join(workspace, file_folder)

            # only archive files, not folders
            if os.path.isfile(file_folder):
                archive_time_stamps[file_folder] = os.path.getmtime(file_folder)

    @classmethod
    def archive_post_mv(cls, workdir, dest, archive_time_stamps):
        """Archive output files"""
        import shutil

        all_file_folder = os.listdir(workdir)

        # create new archive directory
        if os.path.exists(dest):
            print('Warning. Existing folder {} removed.'.format(dest))
            shutil.rmtree(dest)
        os.makedirs(dest)

        for file_folder in all_file_folder:
            src = os.path.join(workdir, file_folder)
            dst = os.path.join(dest, file_folder)

            # only archive files, not folders
            if os.path.isfile(src):
                # case 1: new files generated
                if src not in archive_time_stamps.keys():
                    shutil.move(src, dst)
                # case 2: files modified
                else:
                    if os.path.getmtime(src) != archive_time_stamps[src]:
                        shutil.copy(src, dst)

    if __name__ == "__main__":
        string = 'powersqrt1234 sqrt 1234'
        replace = 'yes'
        str2 = sub_string(string, [0, 22], 'sqrt', replace)
        print(str2)
