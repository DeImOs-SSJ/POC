import cv2
import json
import sqlite3
import os
import numpy as np

def generate_color(id):
    """ Generate a color based on the ID. """
    np.random.seed(id)  # Ensure the same color is generated for the same ID
    return tuple(np.random.randint(0, 255, 3).tolist())

def process_image_for_3d(image_path):
    # Load the floor plan image
    image = cv2.imread(image_path)

    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Apply thresholding to get a binary image
    _, binary = cv2.threshold(gray, 200, 255, cv2.THRESH_BINARY_INV)

    # Detect contours in the binary image
    contours, _ = cv2.findContours(binary, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    elements = []
    element_counter = 1

    # Create a copy of the original image for annotation
    annotated_image = image.copy()

    for contour in contours:
        # Get the bounding box for each contour
        x, y, w, h = cv2.boundingRect(contour)
        
        # Generate a color for this element
        color = generate_color(element_counter)
        
        # Create a dictionary for the element
        element = {
            'id': element_counter,  # Use integer for id
            'dimensions': {
                'length': w / image.shape[1],  # Normalize width
                'height': 0.2,  # Assume a constant height for simplicity
                'width': h / image.shape[0]  # Normalize height
            },
            'position': {
                'x': x / image.shape[1],  # Normalize x position
                'y': 0,  # Set y = 0 for grounded objects
                'z': y / image.shape[0]  # Normalize z position
            }
        }
        
        elements.append(element)
        element_counter += 1

        # Draw the bounding box, ID, and dimensions on the image
        cv2.rectangle(annotated_image, (x, y), (x + w, y + h), color, 2)
        label = f'ID {element["id"]}'
        cv2.putText(annotated_image, label, (x, y - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    # Save the annotated image
    image_name = os.path.basename(image_path)
    annotated_image_path = os.path.join('uploads/upload', f'annotated_{image_name}')
    cv2.imwrite(annotated_image_path, annotated_image)

    # Save metadata to database
    store_image_metadata(image_name, annotated_image_path, elements)

    return json.dumps(elements, indent=4, separators=(',', ': '))

def store_image_metadata(name, file_path, elements):
    conn = sqlite3.connect('images.db')
    c = conn.cursor()
    
    # Create a label string with IDs
    labels = ', '.join([f"ID {elem['id']}" for elem in elements])
    
    c.execute('''
        INSERT INTO images (name, file_path)
        VALUES (?, ?)
    ''', (name, file_path))
    
    conn.commit()
    conn.close()
