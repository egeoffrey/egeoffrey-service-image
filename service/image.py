### service/image: retrieve images from a url or command, perform motion detection and object recognition
## HOW IT WORKS: 
## DEPENDENCIES:
# OS: 
# Python: 
## CONFIGURATION:
# required: 
# optional: 
## COMMUNICATION:
# INBOUND: 
# - IN: 
#   required: url|command
#   optional: username, password, detect_motion_threshold, detect_object, detect_object_threshold
# OUTBOUND: 

import base64
import cv2
import numpy
import imutils
from imutils.object_detection import non_max_suppression
from imutils import paths
from clarifai.rest import ClarifaiApp
 
from sdk.python.module.service import Service

import sdk.python.utils.web
import sdk.python.utils.command
import sdk.python.utils.exceptions as exception

class Image(Service):
    # What to do when initializing
    def on_init(self):
        self.image_unavailable = "iVBORw0KGgoAAAANSUhEUgAAAT0AAADuCAIAAADEJEf/AAAAAXNSR0IArs4c6QAAAARnQU1BAACxjwv8YQUAAAAJcEhZcwAADsMAAA7DAcdvqGQAAATCSURBVHja7d1rbptAFIDRrL1eSbOSZifdSRvFFapaGeZxZ+AyB31/7UQWx2MGBt4e3x6ScvXmI5C4lcStJG4lbiVxK4lbiVtJ3EriVuJWEreSuJW4lcStJG4lcStxK4lbSdxK3EriVhK3EreSuJXErcStJG4lcSuJW4lbSdxK4lbiVhK3kriVuJXErSRuJW4lcSuJW4lbSdxK4lYStxK3kriVxK3ErSRuJXErcSuJW0ncStxK4lYSt5K4lbiVxK0kbiVuJXEriVuJW0ncSuJW4lYSt5K4lbjVsH5+bT4HcZsJ7a+vDV1xmwwtuuI2JVp0xW1KtOiK25Ro0RW3Wd2iK27RFbdCV9yii664RVfiFl1xqxF0S14evvkq4VbtdE9Biy63aqd7Ilp0uVUL3dPRosut6uheBC263OpxqYEUXW6FrrhF94Wcjx8fQ9v/r9DlVnV0p5lBl9sVqxrfrvkb9fALpW0wt29we93ucWw54gjcvsHtWm7vQde+we1ybm9A177B7Ypus9O1b3C7qNvUdO0b3K7rdofuzjnY7dzviXTtG9ze1m3hxcl/033//l57KvjzJfPp2je4Tea2dqArpFsrtl9v4Rlsbrld0e20a5hHHC1zy+26bmcuP4gdeLnldmm3Selyy+3qbjPS5ZZbblvo/rPir/zlIXS55ZbbOro78Aonn7nlltvZbg/nhw/19s8wc8stt3+wxZ7a2afb+WuZW265bTy+7fku6BxyueWW27rBNmrU7RlyueWW20f57WwC6Y74h+0b3C7kdodlyDRV+MQyt9yu7vaVqyfIELqv3qT5pzK33K7u9pWB7Q376R7+CW655TZmJrlh0V/t/9w8q8wtt6u7LTz47KQbe4jLLbfclr5bD91Yadxyy23FuzXT5ZZbbk9z20yXW265PdNtG11uueX2hHmpTrrmpbjl9hLnQqvoOg/ELbdTr7vop+u6C2419TrH8AWArnPkltux6woKXTXTta6AW26HrOPrvFhyZ7OOj1tuR62bL586qqVr3Ty33A68T80Iuu5Twy23w+8LF07XfeG45TbmPqyHd6sJnKYy3nLLbYzbEnLPk7E7nOb8VOaWW26LzgntPGqk5wG53HLLbcCbt92TdfLTcbnlltt8dLnlltv4CxhH0+WWW27bZ5gLr4sKn2HmlltuRw28ny/cTh3F0uWWW27jx97w28pxyy23vYD//+m7nROac0kGt9xyO7UQutxyy20+utxyy20+utxyy20+utxyy20+utxyexO324xurqoWMGyVPENQ3CZwa+OWW2655danwC233HJr45ZbbrkVt9xyy6245ZZbrbL8QNwKXW4ldLkVuuJW6HLrUxC63ArdEY/5E7eaTRdabpWMLrTcKhldaLlVMrrQcqtkdKHlVhK3EreSuJXErcStJG4lcStxK4lbSdxK3EriVhK3kriVuJXErSRuJW4lcSuJW4lbSdxK4lbiVhK3kriVuJXErSRuJXErcSuJW0ncStxK4lYStxK3kriVxK3ErSRuJXEriVuJW0ncSuJW4lYSt5K4lbiVxK0kbiVuJXEriVuJW0ncSuJWErcSt5K4lcStxK0kbiVxK3EriVtJ3ErcSuJWEreSnv0G71zk2XXRfqkAAAAASUVORK5CYII="
        # motion detection settings
        self.detect_motion_equalize_histogram = False
        self.detect_motion_gaussian_blur = True
        self.detect_motion_threshold_value = 60
        self.detect_motion_dilate = False
        self.detect_motion_min_area_ratio = 100
        self.detect_motion_cache_expire = 60*15
        # people detection settings
        self.detect_people_min_width = 400
        self.detect_people_win_stride = 8
        self.detect_people_padding = 8
        self.detect_people_scale = 1.05
        # object detection settings
        self.detect_object_app = None
        self.detect_object_model = None
        # configuration
        self.config = {}
        # require configuration before starting up
        self.config_schema = 1
        self.add_configuration_listener(self.fullname, "+", True)
    
    # What to do when running    
    def on_start(self):
        pass
    
    # What to do when shutting down    
    def on_stop(self):
        pass
        
    # return a cv2 object from a binary image
    def import_image(self, data):
        image = numpy.asarray(bytearray(data), dtype="uint8")
        image = cv2.imdecode(image, cv2.IMREAD_COLOR)
        return image

    # return a binary image from a cv2 object
    def export_image(self, image):
        r, buffer = cv2.imencode(".png",image)
        data = buffer.tostring()
        return data
        
    # save an image to disk
    def save_image(self, file, image):
        cv2.imwrite(file, image)
        
    # load an image from disk
    def load_image(self, filename):
        return cv2.imread(file)
        
    # normalize an image
    def normalize_image(self, image):
        if image is None: 
            return image
        normalized = image
        # convert the image to B&W and apply some filters
        normalized = cv2.cvtColor(normalized, cv2.COLOR_BGR2GRAY)
        if self.detect_motion_equalize_histogram: 
            normalized = cv2.equalizeHist(normalized)
        if self.detect_motion_gaussian_blur:
            normalied = cv2.GaussianBlur(normalized, (21, 21), 0)
        return normalized
        
    # detect differences between two or more images
    def detect_motion(self, images):
        max_percentage = 0
        max_image = None
        # for each image
        for i in range(len(images)-1):
            image1 = self.import_image(images[i])
            image2 = self.import_image(images[i+1])
            # normalize the images
            normalied_image1 = self.normalize_image(image1)
            normalied_image2 = self.normalize_image(image2)
            if normalied_image1 is None or normalied_image2 is None: 
                continue
            # calculate height and width
            image1_height, image1_width = normalied_image1.shape[:2]
            image2_height, image2_width = normalied_image2.shape[:2]
            # if they have difference sizes, the image is invalid, ignore it
            if image1_height != image2_height or image1_width != image2_width: 
                continue
            area = image1_height*image1_width
            # calculate the difference
            delta = cv2.absdiff(normalied_image1, normalied_image2)
            # calculate the threshold by painting the background in black and motion in white
            delta = cv2.threshold(delta, self.detect_motion_threshold_value, 255, cv2.THRESH_BINARY)[1]
            # removes gaps in between the motions
            if self.detect_motion_dilate: 
                delta = cv2.dilate(delta, None)
            # find the white images in the black background
            countour,heirarchy = cv2.findContours(delta, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            # draw rectangles around motions
            for i in countour:
                # do not draw a rectangle if too small
                if cv2.contourArea(i) < area/self.detect_motion_min_area_ratio:
                    continue
                (x, y, w, h) = cv2.boundingRect(i)
                cv2.rectangle(image2, (x, y), (x + w, y + h), (0, 0, 255), 2)
            # return the percentage of change by calculating how many pixels have changed over the total number of pixel of the image
            percentage = cv2.countNonZero(delta)*100/(area)
            # when receiving more than two images to compare, return the one with the maximum motion
            if percentage >= max_percentage: 
                max_percentage = percentage
                max_image = image2
        if max_image is None: 
            return None
        return [max_percentage, self.export_image(max_image)]
        
    # detect people in an image
    def detect_people(self, image):
        image = self.import_image(image)
        # resize the image it to have a maximum width
        image = imutils.resize(image, width=min(self.detect_people_min_width, image.shape[1]))
        # detect people in the image
        hog = cv2.HOGDescriptor()
        hog.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        (rects, weights) = hog.detectMultiScale(image, winStride=(self.detect_people_win_stride, self.detect_people_win_stride), padding=(self.detect_people_padding, self.detect_people_padding), scale=self.detect_people_scale)
        # apply non-maxima suppression to avoid overlapping boxes
        rects = numpy.array([[x, y, x + w, y + h] for (x, y, w, h) in rects])
        picks = non_max_suppression(rects, probs=None, overlapThresh=0.65)
        for (xA, yA, xB, yB) in picks:
            cv2.rectangle(image, (xA, yA), (xB, yB), (0, 255, 0), 2)
        return [len(picks), self.export_image(image)]   

    # detect objects in an image
    def detect_object(self, image):
        # identify the objects
        result = self.detect_object_model.predict_by_bytes(image)
        concepts = result["outputs"][0]["data"]["concepts"]
        objects = {}
        # normalize the results
        for concept in concepts:
            objects[concept["name"]] = int(concept["value"]*100)
        return objects
        
    # What to do when receiving a request for this module
    def on_message(self, message):
        if message.command == "IN":
            sensor_id = message.args
            # retrieve the image
            if message.has("url"): 
                url = message.get("url")
                username = message.get("username") if message.has("username") else None
                password = message.get("password") if message.has("password") else None
                # download the image pointed by the url
                try:
                    data = sdk.python.utils.web.get(url, username, password, binary=True)
                except Exception,e: 
                    self.log_debug("unable to connect to "+url+": "+exception.get(e))
                    data = ""
            elif message.has("command"):
                command = message.get("command")
                try:
                    data = sdk.python.utils.command.run(command)
                except Exception,e: 
                    self.log_error("unable to run command "+command+": "+exception.get(e))
                    data = ""
            else:
                self.log_error(sensor_id+" must have a url or a command configured")
                return
            # return empty if the data is not binary
            if "<html" in data.lower(): data = ""
            if data == "": data = self.image_unavailable
            orig_data = data
            # perform motion detection if requested
            if message.has("detect_motion_threshold"):
                # return if there is no previous image saved
                if not self.cache.find(sensor_id):
                    self.log_debug("["+sensor_id+"] ignoring image since there is nothing to compare against yet")
                    # save the current image for later comparison (will be kept in cache for 15 minutes)
                    self.cache.add(sensor_id, data, self.detect_motion_cache_expire)
                    return
                # retrieve the previous image
                prev_data = self.cache.get(sensor_id)
                # do the comparison with the current image
                result = self.detect_motion([prev_data, data])
                # save the current image for later comparison (will be kept in cache for 15 minutes)
                self.cache.add(sensor_id, data, self.detect_motion_cache_expire)
                # compare the two images
                if result is None: 
                    self.log_debug("["+sensor_id+"] unable to compare the two images")
                    return
                difference = result[0]
                image = result[1]
                self.log_debug("["+sensor_id+"] motion detected is "+str(difference)+"%, threshold is "+str(message.get("detect_motion_threshold"))+"%")
                # return if motions is less than the threshold
                if difference < message.get("detect_motion_threshold"): 
                    return
                self.log_info("["+sensor_id+"] motion detected: "+str(difference)+"%")
                data = image
            # perform people detection if requested
            if message.has("detect_people_threshold"):
                # detect the people
                result = self.detect_people(data)
                people = result[0]
                image = result[1]
                self.log_debug("["+sensor_id+"] people detected: "+str(people)+", threshold is "+str(message.get("detect_people_threshold")))
                # return if people are not detected
                if people < message.get("detect_people_threshold"):
                    return
                self.log_info("["+sensor_id+"] people detected: "+str(people))
                data = image
            # perform object detection if requested
            if message.has("detect_object_name") and self.detect_object_app is not None:
                # detect the objects
                objects = self.detect_object(orig_data)
                self.log_debug("["+sensor_id+"] objects detected: "+str(objects))
                # check if the object has been found
                if message.get("detect_object_name") not in objects:
                    return
                # if a threshold is set, return if it is lower than the confidence level
                if message.has("detect_object_threshold") and objects[message.get("detect_object_name")] < message.get("detect_object_threshold"):
                    return
                self.log_info("["+sensor_id+"] object '"+message.get("detect_object_name")+"' detected with confidence "+str(objects[message.get("detect_object_name")])+"%")
            # reply to the requesting module 
            data = base64.b64encode(data)
            message.reply()
            message.set("value", data)
            # send the response back
            self.send(message)

    # What to do when receiving a new/updated configuration for this module
    def on_configuration(self,message):
        # module's configuration
        if message.args == self.fullname and not message.is_null:
            if message.config_schema != self.config_schema: 
                return False
            self.config = message.get_data()
            # initialize the detect object object
            if "clarifai_api_key" in self.config and self.config["clarifai_api_key"] is not None:
                try:
                    self.detect_object_app = ClarifaiApp(api_key=self.config["clarifai_api_key"])
                    self.detect_object_model = self.detect_object_app.public_models.general_model
                except Exception,e: 
                    self.log_error("unable to initialize detect object app: "+exception.get(e))
        # register/unregister the sensor
        if message.args.startswith("sensors/"):
            if message.is_null: 
                sensor_id = self.unregister_sensor(message)
            else: 
                sensor_id = self.register_sensor(message)