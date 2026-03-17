import cv2
import numpy as np
import pyautogui
import time
import os

class IconGrounder:
    """
    Enhanced Visual Grounding System for Desktop Icons
    
    This implementation provides flexible icon detection that can:
    - Handle different icon positions (top-left, center, bottom-right)
    - Adapt to different icon sizes
    - Work with light/dark themes
    - Bypass unexpected pop-ups using multi-strategy detection
    """

    def __init__(self, template_path, debug=False):
        """
        Initialize the IconGrounder
        
        Args:
            template_path: Path to the icon template image
            debug: Enable debug mode to save screenshots
        """
        # Load template in grayscale
        self.template = cv2.imread(template_path, 0)
        if self.template is None:
            raise ValueError(f"Could not load template: {template_path}")
        
        self.template_h, self.template_w = self.template.shape
        self.debug = debug
        self.screenshot_count = 0
        
        # Detection parameters
        self.min_confidence = 0.35
        self.scales = [0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]  # Extended range
        if not os.path.exists("annotations"):
            os.makedirs("annotations")
    def screenshot(self):
        """Capture a screenshot of the desktop"""
        img = pyautogui.screenshot()
        # Convert PIL image to OpenCV format (BGR)
        frame = cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)
        self.screenshot_count += 1
        
        if self.debug:
            debug_path = f"screenshots/screenshot_{self.screenshot_count}.png"
            cv2.imwrite(debug_path, frame)
            print(f"Debug: Saved screenshot to {debug_path}")
        
        return frame
    
    def preprocess_template(self):
        """Preprocess template for better matching"""
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(self.template, (3, 3), 0)
        # Apply adaptive thresholding for theme invariance
        processed = cv2.adaptiveThreshold(
            blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY, 11, 2
        )
        return processed
    
    def preprocess_screenshot(self, screenshot):
        """Preprocess screenshot for matching"""
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        # Apply Gaussian blur
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        # Apply histogram equalization for lighting invariance
        equalized = cv2.equalizeHist(blurred)
        return equalized
    
    def edge_based_detection(self, screenshot):
        """
        Edge-based detection for more robust matching
        Works well with icons that have clear edges
        """
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Detect edges in screenshot
        edges = cv2.Canny(gray, 50, 150)
        
        # Detect edges in template
        template_edges = cv2.Canny(self.template, 50, 150)
        
        # Template matching on edges
        result = cv2.matchTemplate(edges, template_edges, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        return max_val, max_loc
    
    def multi_scale_detection(self, processed_screenshot):
        """
        Multi-scale template matching
        Tests different scales to find the icon regardless of size
        """
        best_score = 0
        best_location = None
        best_scale = 1.0
        best_size = None
        
        for scale in self.scales:
            # Resize template
            new_w = int(self.template_w * scale)
            new_h = int(self.template_h * scale)
            
            resized = cv2.resize(
                self.template, 
                (new_w, new_h),
                interpolation=cv2.INTER_LINEAR
            )
            
            # Template matching
            result = cv2.matchTemplate(
                processed_screenshot,
                resized,
                cv2.TM_CCOEFF_NORMED
            )
            
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if self.debug:
                print(f"  Scale {scale:.1f}: confidence = {max_val:.3f}")
            
            if max_val > best_score:
                best_score = max_val
                best_location = max_loc
                best_scale = scale
                best_size = (new_w, new_h)
        
        return best_score, best_location, best_size
    
    def feature_based_detection(self, screenshot):
        """
        Feature-based detection using ORB
        Good for handling partial occlusion and rotations
        """
        # Convert to grayscale
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Initialize ORB detector
        orb = cv2.ORB_create(nfeatures=1000)
        
        # Find keypoints and descriptors
        kp1, des1 = orb.detectAndCompute(self.template, None)
        kp2, des2 = orb.detectAndCompute(gray, None)
        
        if des1 is None or des2 is None:
            return 0, None
        
        # Create BFMatcher
        bf = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True)
        
        # Match descriptors
        matches = bf.match(des1, des2)
        
        if len(matches) < 10:
            return 0, None
        
        # Sort matches by distance
        matches = sorted(matches, key=lambda x: x.distance)
        
        # Extract matched points
        src_pts = np.float32([kp1[m.queryIdx].pt for m in matches]).reshape(-1, 1, 2)
        dst_pts = np.float32([kp2[m.trainIdx].pt for m in matches]).reshape(-1, 1, 2)
        
        # Find homography
        try:
            M, mask = cv2.findHomography(src_pts, dst_pts, cv2.RANSAC, 5.0)
            if M is not None:
                # Get bounding box
                h, w = self.template.shape
                pts = np.float32([[0, 0], [w, 0], [w, h], [0, h]]).reshape(-1, 1, 2)
                dst = cv2.perspectiveTransform(pts, M)
                
                # Calculate center
                center_x = int(np.mean(dst[:, 0, 0]))
                center_y = int(np.mean(dst[:, 0, 1]))
                
                # Calculate confidence based on match quality
                confidence = len(matches) / 100.0
                return min(confidence, 1.0), (center_x, center_y)
        except:
            pass
        
        return 0, None
    
    def find_icon(self, save_screenshot=True):
        """
        Find the icon on desktop using multiple strategies
        
        Returns:
            tuple: (x, y) center coordinates of the icon, or None if not found
        """
        print("Capturing screenshot...")
        screenshot = self.screenshot()
        
        # Try multiple detection strategies
        strategies = [
            ("Multi-Scale Template Matching", self._try_multi_scale),
            ("Edge-Based Detection", self._try_edge_detection),
            ("Feature-Based Detection", self._try_feature_detection),
        ]
        
        best_result = None
        best_confidence = 0
        detected_size = (self.template_w, self.template_h)
        for strategy_name, strategy_func in strategies:
            print(f"Trying {strategy_name}...")
            res = strategy_func(screenshot)
            confidence = res[0]
            result = res[1]
            
            if confidence > best_confidence:
                best_confidence = confidence
                best_result = result
            
            if confidence > 0.7:
                print(f"  ✓ High confidence: {confidence:.3f}")
                break
        
        if best_result and best_confidence > self.min_confidence:
            x, y = best_result
            annotated_img = screenshot.copy()
            cv2.rectangle(annotated_img, (int(x-25), int(y-25)), (int(x+25), int(y+25)), (0, 255, 0), 3)
            cv2.putText(annotated_img, f"Conf: {best_confidence:.2f}", (int(x-25), int(y-35)),cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
            cv2.imwrite(f"annotations/detected_{int(time.time())}.png", annotated_img)
            print(f"✓ Icon found at ({x}, {y}) with confidence {best_confidence:.3f}")
            return (x, y)
        
        print(f"✗ Icon not found. Best confidence: {best_confidence:.3f}")
        return None
    
    def _try_multi_scale(self, screenshot):
        """Multi-scale template matching strategy"""
        # Preprocess
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        blurred = cv2.GaussianBlur(gray, (3, 3), 0)
        
        best_score = 0
        best_location = None
        best_size = None
        
        for scale in self.scales:
            new_w = int(self.template_w * scale)
            new_h = int(self.template_h * scale)
            
            resized = cv2.resize(self.template, (new_w, new_h))
            
            result = cv2.matchTemplate(blurred, resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(result)
            
            if max_val > best_score:
                best_score = max_val
                best_location = max_loc
                best_size = (new_w, new_h)
        
        if best_score > self.min_confidence and best_location:
            center_x = best_location[0] + best_size[0] // 2
            center_y = best_location[1] + best_size[1] // 2
            return best_score, (center_x, center_y)
        
        return best_score, None
    
    def _try_edge_detection(self, screenshot):
        """Edge-based detection strategy"""
        gray = cv2.cvtColor(screenshot, cv2.COLOR_BGR2GRAY)
        
        # Canny edge detection
        edges = cv2.Canny(gray, 50, 150)
        template_edges = cv2.Canny(self.template, 50, 150)
        
        result = cv2.matchTemplate(edges, template_edges, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val > self.min_confidence:
            center_x = max_loc[0] + self.template_w // 2
            center_y = max_loc[1] + self.template_h // 2
            return max_val, (center_x, center_y)
        
        return max_val, None
    
    def _try_feature_detection(self, screenshot):
        """Feature-based detection strategy"""
        return self.feature_based_detection(screenshot)