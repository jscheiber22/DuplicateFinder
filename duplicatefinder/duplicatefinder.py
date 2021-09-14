import os
import sys
import cv2
from PIL import Image
from PIL import ImageChops
from datetime import datetime
import subprocess
from time import sleep
import multiprocessing as mp
import re

'''

Program Assumptions:
    -- The series of nested for loops expects each directory to contain either the video files, or directories containing video files, but no deeper than that
    -- Each directory in the directory file is on its own line and ends with a '/'

'''

class Finder:
    def __init__(self, photos = False, remove = False):
        self.imageDestination = '/media/sf_CompletedTorrents/Duplicates/'

        self.newPulls = []
        self.imagePulledCount = 0
        self.duplicatesFoundCount = 0
        self.imagesCheckedCount = 0

        # COLORS :)
        self.red = '\033[91m'
        self.yellow = '\033[93m'
        self.reset = '\033[0m'

    # The main running method that extends out to other methods, but will always return back here to do main stuff
    def pullImages(self, directory):
        toAdd = ''
        # Pulls image at x minutes (specified in pullImage method) for each video file within 2 directory layers
        directory = directory.replace('\n', '').replace('\r', '')
        if not directory.endswith('/'):
            directory = directory + '/'
        if directory is not None and directory != "":
            print("\nNow checking: " + directory + "\n")
            directoryContents = os.listdir(directory)
            for content in directoryContents:
                if os.path.isfile(directory + content) and not content.startswith('.'):
                    if content.lower().endswith('mp4') or content.lower().endswith('mov') or content.lower().endswith('avi') or content.lower().endswith('mkv') or 'mp4' in content.lower(): # checks for video filetype
                        if not content.endswith('.torrent'):
                            pulled = self.pullImage(directory, content)
                            if pulled:
                                toAdd = directory[1:-1].replace('/', '.') + '/' + content + '.jpg'
                                self.newPulls.append(directory[1:-1].replace('/', '.') + '/' + content + '.jpg')
                                self.imagePulledCount += 1

                elif os.path.isdir(directory + content):
                    contentOfDirectoryContent = os.listdir(directory + content)
                    for subcontent in contentOfDirectoryContent:
                        if os.path.isfile(directory + content + "/" + subcontent) and not subcontent.startswith('.'):
                            if subcontent.lower().endswith('mp4') or subcontent.lower().endswith('mov') or subcontent.lower().endswith('avi') or subcontent.lower().endswith('mkv') or 'mp4' in subcontent.lower(): # checks for video filetype
                                # do all the file stuff but replace content with subcontent
                                if not subcontent.endswith('.torrent'):
                                    pulled = self.pullImage(directory + content + "/", subcontent) # Sends more accurate directory info due to subcontent's existence
                                    if pulled:
                                        toAdd = directory[1:].replace('/', '.') + content + '/' + subcontent + '.jpg'
                                        self.newPulls.append(directory[1:].replace('/', '.') + content + '/' + subcontent + '.jpg')
                                        self.imagePulledCount += 1

            if self.newPulls and self.newPulls[0] is not None:
                return self.newPulls



    def compare(self, image):
        if image is None or image == '':
            return
        imageEnding = re.search('\/.*\.jpg', image).group().replace('/', '')
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

                if imageEnding != comparingImage and not used: # avoids it seeing itself duh
                    image_one = Image.open(self.imageDestination + image)
                    image_two = Image.open(self.imageDestination + secondaryDirectory + "/" + comparingImage)

                    diff = ImageChops.difference(image_one, image_two)

                    if diff.getbbox() is None:
                        # same
                        f = open('duplicates.txt', 'a')
                        f.write("\nDuplicate is " + imageEnding + ' from ' + image + ' which matched with ' + comparingImage + ' from ' + secondaryDirectory + '.' + '\n')
                        f.close()
                        print(self.red + "\n\nDuplicate is " + imageEnding + ' from ' + image + ' which matched with ' + comparingImage + ' from ' + secondaryDirectory + '.' + self.reset + "\n\n")

        if imageEnding is not None:
            # After checking an image against all other images, its name is added to the checked list in checked.txt and should not be checked against any others
            f = open('checked.txt', 'a')
            f.write(imageEnding + '\n')
            f.close()
            # f = open('checked.txt', 'r')
            # linecount = f.readlines()
            # f.close()
            # print('Comparison ' + str(len(linecount)) + ' out of ' + str(len(newPulls)) + ' completed.')
            print('Another one checked.')

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
                # print(self.yellow + "\n\nNotice: " + imageDestination + directory[1:-1].replace('/', '.') + "/" + content + ".jpg already exists?? Skipping :D\n\n" + self.reset)
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

    def resetChecked(self):
        try:
            subprocess.call(['rm', 'checked.txt'])
            subprocess.call(['touch', 'checked.txt'])
        except:
            subprocess.call(['touch', 'checked.txt'])


class PhotosFinder:
    def __init__(self):
        self.duplicatesFoundCount = 0
        self.imagesCheckedCount = 0
        self.foundFilesyucky = []

        # COLORS :)
        self.red = '\033[91m'
        self.yellow = '\033[93m'
        self.reset = '\033[0m'

    def fileWalk(self, rootDirectory):
        thusFoundFiles = {} # reset with each new directory to keep data usage down
        for root, direc, files in os.walk(".", topdown=False):
            for file in files:
                if '.jpeg' in file:
                    thusFoundFiles[len(thusFoundFiles)] = (root, file)
        if len(thusFoundFiles) > 0:
            return thusFoundFiles

    def compare(self, images):
        print('resetting chefcked')
        self.resetChecked()
        if images is None:
            return
        for image in images:
            # print(images[image][1])
            # print('image')
            for workerData in self.foundFilesyucky:
                for comparingImage in workerData:
                    f = open('checked.txt', 'r+')
                    checkedImages = f.readlines()
                    f.close()

                    used = False
                    for line in checkedImages:
                        # needs to check image its looking at duh
                        if os.path.join(workerData[comparingImage][0], workerData[comparingImage][1]) in line:
                            used = True
                            break

                    if os.path.join(images[image][0], images[image][1]) != os.path.join(workerData[comparingImage][0], workerData[comparingImage][1]) and not used: # avoids it seeing itself duh
                        image_one = Image.open(os.path.join(images[image][0], images[image][1]))
                        image_two = Image.open(os.path.join(workerData[comparingImage][0], workerData[comparingImage][1]))

                        diff = ImageChops.difference(image_one, image_two)

                        if diff.getbbox() is None:
                            # same
                            f = open('duplicates.txt', 'a')
                            f.write("\nDuplicate is " + images[image][1] + ' from ' + images[image][0] + ' which matched with ' + workerData[comparingImage][1] + ' from ' + workerData[comparingImage][0] + '.' + '\n')
                            f.close()
                            print(self.red + "\n\nDuplicate is " + images[image][1] + ' from ' + images[image][0] + ' which matched with ' + workerData[comparingImage][1] + ' from ' + workerData[comparingImage][0] + '.' + self.reset + "\n\n")

            # After checking an image against all other images, its name is added to the checked list in checked.txt and should not be checked against any others
            f = open('checked.txt', 'a')
            f.write(os.path.join(images[image][0], images[image][1]) + '\n')
            f.close()
            print('Another one checked.')

    def resetChecked(self):
        try:
            subprocess.call(['rm', 'checked.txt'])
            subprocess.call(['touch', 'checked.txt'])
        except:
            subprocess.call(['touch', 'checked.txt'])


if __name__ == "__main__":
    '''
    TO DO: Finish the -r arg to make it remove the file or move it to the reddrive/duplicateholding/ folder plaese
    '''
    pool = mp.Pool(6)

    if '--photos' in sys.argv:
        finder = PhotosFinder()
        discoveredFiles = []

        listPath = 'photodir.txt'
        f = open(listPath, 'r')
        directories = f.readlines()
        f.close()
        directories = [i for i in directories if not i.startswith('#')]

        finder.foundFilesyucky = pool.map(finder.fileWalk, directories)
        # for workerData in finder.foundFilesyucky: # iterating through dictionary
        #     for tuple in workerData:
        #         print(workerData[tuple][0])

        if len(finder.foundFilesyucky) < 1:
            print("not enough files found, exiting")
            exit()
        # for file in foundFilesyucky:
        #     if file is not None:
        #         discoveredFiles += file
        # foundFilesyucky = []

        print("\n\nChecking for duplicates.\nTime Started: " + datetime.now().strftime("%H:%M") + "\n\n")

        # pool.map(finder.compare, discoveredFiles)
        pool.map(finder.compare, finder.foundFilesyucky)
        exit()
    else:
        finder = Finder('-r' in sys.argv)
        newPulls = []

        listPath = 'directories.txt'
        f = open(listPath, 'r')
        directories = f.readlines()
        f.close()

        directories = [i for i in directories if not i.startswith('#')]

        newPullsyucky = pool.map(finder.pullImages, directories)
        for pull in newPullsyucky:
            if pull is not None:
                newPulls += pull
        print("\n\nPulled " + str(len(newPulls)) + " images.\nNow checking them for duplicates.\nTime Started: " + datetime.now().strftime("%H:%M") + "\n\n")

        if len(newPulls) > 0:
            pool.map(finder.compare, newPulls)

        print("Time Finished: " + datetime.now().strftime("%H:%M") + "\n\n")

        finder.resetChecked()
