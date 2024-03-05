from os import scandir, rename
from os.path import splitext, exists, join
from shutil import move
from time import sleep
import logging

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

source_dir = R"C:\Users\ethan\Downloads"
dest_dir_sfx = R"D:\Downloads\Download-SFX"
dest_dir_music = R"D:\Downloads\Download-Music"
dest_dir_video = R"D:\Downloads\Download-Video"
dest_dir_image = R"D:\Downloads\Download-Image"
dest_dir_documents = R"D:\Downloads\Download-Document"
dest_dir_misc = R"D:\Downloads\Download-Misc"

image_extensions = [".jpg", ".jpeg", ".jpe", ".jif", ".jfif", ".jfi", ".png", ".gif", ".webp", ".tiff", ".tif", ".psd", ".raw", ".arw", ".cr2", ".nrw",
                    ".k25", ".bmp", ".dib", ".heif", ".heic", ".ind", ".indd", ".indt", ".jp2", ".j2k", ".jpf", ".jpf", ".jpx", ".jpm", ".mj2", ".svg", ".svgz", ".ai", ".eps", ".ico"]

video_extensions = [".webm", ".mpg", ".mp2", ".mpeg", ".mpe", ".mpv", ".ogg",
                    ".mp4", ".mp4v", ".m4v", ".avi", ".wmv", ".mov", ".qt", ".flv", ".swf", ".avchd"]

audio_extensions = [".m4a", ".flac", ".mp3", ".wav", ".wma", ".aac"]

document_extensions = [".doc", ".docx", ".odt",
                       ".pdf", ".xls", ".xlsx", ".ppt", ".pptx"]


def make_unique(dest, name):
    #Ensure the file name is unique
    #Two parameters, destination of a file and the name of said file
    filename, extension = splitext(name)
        #splitext splits extension from path name
    counter = 1
    
    #Seemingly redundant at first look but i dont want to accidentally overwrite files while moving them, this is just to be safe.
    while exists(f"{dest}\{name}"):
        #While exists checks if the file exists at a given path
        #Enter a while loop to check if a file name exists, add a 1 to the end of it
        #String formatting: f String allows for variable interpolation
        name = f"{filename}({str(counter)}){extension}"
        counter += 1

    return name


def move_file(dest, entry, name):
    #Check if a filepath exists, if it does send it to make_unique to append a unique number to the end of the file name
    if exists(f"{dest}\{name}"):
        unique_name = make_unique(dest, name)
        oldName = join(dest, name)
        newName = join(dest, unique_name)
        rename(oldName, newName)
    move(entry, dest)
    #Renames file to the new name and moves the entry to destination


class MoverHandler(FileSystemEventHandler):
    #Runs whenever there is a change in source directory.
    def on_modified(self, event):
        #Listens for modification within sourcey directory and when a modification occurs, it iterates over every file in the entry.
        #For each file it: retrieves name, and calls all checking methods within the class.
        with scandir(source_dir) as entries:
            for entry in entries:
                name = entry.name
                self.check_audio_files(entry, name)
                self.check_video_files(entry, name)
                self.check_image_files(entry, name)
                self.check_document_files(entry, name)


    def check_audio_files(self, entry, name):
        #Iterates through the list of audio extensions specified above and checks if a file ends with said audio extension.
        for audio_extension in audio_extensions:
            a_name, a_ext = splitext(name)
            if a_ext == audio_extension or a_ext == audio_extension.upper():
                if entry.stat().st_size < 10_000_000 or "SFX" in name:
                    dest = dest_dir_sfx
                else:
                    dest = dest_dir_music
                move_file(dest, entry, name)
                logging.info(f"Moved audio file: {name}")

    def check_video_files(self, entry, name):
        for video_extension in video_extensions:
            v_name, v_ext = splitext(name)
            if v_ext == video_extension or v_ext == video_extension.upper():
                move_file(dest_dir_video, entry, name)
                logging.info(f"Moved video file: {name}")

    def check_image_files(self, entry, name):
        for image_extension in image_extensions:
            i_name, i_ext = splitext(name)
            if i_ext == image_extension or i_ext == image_extension.upper():
                move_file(dest_dir_image, entry, name)
                logging.info(f"Moved image file: {name}")

    def check_document_files(self, entry, name):
        for documents_extension in document_extensions:
            d_name, d_ext = splitext(name)
            if d_ext == documents_extension or d_ext == documents_extension.upper():
                move_file(dest_dir_documents, entry, name)
                logging.info(f"Moved document file: {name}")

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    path = source_dir
    event_handler = MoverHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=True)
    observer.start()
    try:
        while True:
            sleep(10)
            print("sleeping")
    except KeyboardInterrupt:
        observer.stop()
    observer.join()