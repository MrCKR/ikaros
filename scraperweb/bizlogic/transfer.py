# -*- coding: utf-8 -*-
'''
'''
import os
import shutil
from .manager import movie_lists
from .info import transferService


def copysub(src_folder, destfolder):

    file_type = ['.ass', '.srt', '.ssa', '.sub']
    dirs = os.listdir(src_folder)
    for item in dirs:
        (path, ext) = os.path.splitext(item)
        if ext.lower() in file_type:
            src_file = os.path.join(src_folder, item)
            shutil.copy(src_file, destfolder)


def transfer(src_folder, dest_folder, prefix, escape_folders):

    movie_list = movie_lists(src_folder, escape_folders)

    for movie_path in movie_list:
        movie_info = transferService.getTransferLogByPath(movie_path)
        if not movie_info or not movie_info.success:
            transferService.addTransferLog(movie_path)

            (filefolder, name) = os.path.split(movie_path)
            midfolder = filefolder.replace(src_folder, '').lstrip("\\").lstrip("/")
            newpath = os.path.join(dest_folder, midfolder, name)
            soft_path = os.path.join(prefix, name)

            (newfolder, tname) = os.path.split(newpath)
            if not os.path.exists(newfolder):
                os.makedirs(newfolder)
            # os.symlink(soft_path, newpath)
            copysub(filefolder, newfolder)
            transferService.updateTransferLog(movie_path, soft_path, newpath)

    return True
