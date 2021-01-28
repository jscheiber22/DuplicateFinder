import os
import sys
import cv2
from PIL import Image
from PIL import ImageChops

'''

Program Assumptions:
    -- The series of nested for loops expects each directory to contain either the video files, or directories containing video files, but no deeper than that
    -- Each directory in the directory file is on its own line and ends with a '/'

'''

class Finder:
    def __init__(self):
        self.imageDestination = '/media/sf_CompletedTorrents/Duplicates/'

        # COLORS :)
        self.red = '\033[91m'
        self.yellow = '\033[93m'
        self.reset = '\033[0m'

    # The main running method that extends out to other methods, but will always return back here to do main stuff
    def find(self):
        listPath = 'directories.txt'
        f = open(listPath, 'r')
        directories = f.readlines()
        f.close()

        imagePulledCount = 0

        # Pulls image at x minutes (specified in pullImage method) for each video file within 2 directory layers
        print("\nBeginning to pull images.\n\n")
        for directory in directories:
            directory = directory.replace('\n', '').replace('\r', '')
            if directory is not None and directory != "":
                print("\nNow checking: " + directory + "\n")
                directoryContents = os.listdir(directory)
                for content in directoryContents:
                    if os.path.isfile(directory + content) and not content.startswith('.'):
                        if content.lower().endswith('mp4') or content.lower().endswith('mov') or content.lower().endswith('avi') or content.lower().endswith('mkv') or 'mp4' in content.lower(): # checks for video filetype
                            pulled = self.pullImage(directory, content)
                            if pulled:
                                imagePulledCount += 1
                        else:
                            print(self.yellow + "\n\nNotice: Ignoring " + content + " because it has the wrong file ending :/\n\n" + self.reset)

                    elif os.path.isdir(directory + content):
                        contentOfDirectoryContent = os.listdir(directory + content)
                        for subcontent in contentOfDirectoryContent:
                            if os.path.isfile(directory + content + "/" + subcontent) and not subcontent.startswith('.'):
                                if subcontent.lower().endswith('mp4') or subcontent.lower().endswith('mov') or subcontent.lower().endswith('avi') or subcontent.lower().endswith('mkv') or 'mp4' in subcontent.lower(): # checks for video filetype
                                    # do all the file stuff but replace content with subcontent
                                    pulled = self.pullImage(directory + content + "/", subcontent) # Sends more accurate directory info due to subcontent's existence
                                    if pulled:
                                        imagePulledCount += 1


        if imagePulledCount > 0:
            print("\n\nPulled " + str(imagePulledCount) + " images.\nNow checking them for duplicates.\n\n")

            duplicatesFoundCount = 0
            imagesCheckedCount = 0
            # Now actually does duplicate checking
            for directory in os.listdir(self.imageDestination): # each directory in duplicates folder
                for image in os.listdir(self.imageDestination + directory): # each image in each directory
                    for secondaryDirectory in os.listdir(self.imageDestination): # each directory in duplicates folder to search in for comparing images
                        for comparingImage in os.listdir(self.imageDestination + secondaryDirectory): # all images each other image is to be compared to
                            # Although repetitive, it should be updated frequently so that it doesn't reuse any images to kill even more time
                            f = open('checked.txt', 'r+')
                            checkedImages = f.readlines()
                            f.close()

                            used = False
                            for line in checkedImages:
                                if comparingImage in line:
                                    used = True
                                    break

                            if not image == comparingImage and not used: # avoids it seeing itself duh
                                image_one = Image.open(self.imageDestination + directory + "/" + image)
                                image_two = Image.open(self.imageDestination + secondaryDirectory + "/" + comparingImage)

                                diff = ImageChops.difference(image_one, image_two)

                                if diff.getbbox() is None:
                                    # same
                                    f = open('duplicates.txt', 'a')
                                    f.write(image + '\n')
                                    f.close()
                                    duplicatesFoundCount += 1
                                    print(self.red + "\n\nDuplicate " + str(duplicatesFoundCount) + " is " + image + self.reset + "\n\n")

                    # After checking an image against all other images, its name is added to the checked list in checked.txt and should not be checked against any others
                    f = open('checked.txt', 'a')
                    f.write(image)
                    f.close()

                    imagesCheckedCount += 1
                    print("Checked image #" + str(imagesCheckedCount) + " out of " + str(imagePulledCount) + ", ie " + str(round(imagesCheckedCount / imagePulledCount, 3)) + "% complete :).")

            print("\nFound " + str(duplicatesFoundCount) + " duplicates.")

        else:
            print("\nNo images pulled. uho :/\n")


    def pullImage(self, directory, content):
        imageDestination = self.imageDestination
        minutes = 3 # Number of minutes in to take the image capture

        # This bit looks to make the final location for each image a folder
        # named after the one it came from, to make finding the original video
        # much easier and then excludes anything that already has a directory
        # to make it faster
        if not os.path.isdir(imageDestination + directory[1:-1].replace('/', '.')):
            os.mkdir(imageDestination + directory[1:-1].replace('/', '.'))
        else:
            if os.path.isfile(imageDestination + directory[1:-1].replace('/', '.') + "/" + content + ".jpg"):
                print(self.yellow + "\n\nNotice: " + imageDestination + directory[1:-1].replace('/', '.') + "/" + content + ".jpg already exists?? Skipping :D\n\n" + self.reset)
                return False

        vidcap = cv2.VideoCapture(directory + content)
        vidcap.set(0, minutes * 60000)     # just cue to 20 sec. position (via milliseconds)
        success,image = vidcap.read()
        if success:
            if '-v' in sys.argv or '-V' in sys.argv:
                print("Pulling content: " + content)
            cv2.imwrite(imageDestination + directory[1:-1].replace('/', '.') + "/" + content + ".jpg", image)    # save frame as JPEG file
            cv2.waitKey()
            return True
        else:
            return False




if __name__ == "__main__":
    Finder().find()
