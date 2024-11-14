from Database.connection import connect_to_mongo, data_store, fetch_signatures
from flask import Flask, request, jsonify, render_template
from dotenv import load_dotenv
from functools import wraps
from PIL import Image
import base64
import os
import io
from imagePreprocess import process_and_extract_features
from vgg_cosine import is_signature_genuine
from resnet_cosine import is_signature_genuine_resnet
import time
from datetime import timedelta 

load_dotenv()
app = Flask(__name__)
UPLOAD_API_KEY = os.getenv("UPLOAD_API_KEY")
API_KEY_VERIFICATION = os.getenv("API_KEY_VERIFICATION")

app.config['MATCHING_FOLDER'] = 'static/person'
os.makedirs(app.config['MATCHING_FOLDER'], exist_ok=True)

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

def require_api_key(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != UPLOAD_API_KEY:
            return jsonify({'error': 'Invalid API Key'}), 403
        return f(*args, **kwargs)
    return decorated_function

def require_api_key_verification(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        api_key = request.headers.get('x-api-key')
        if api_key != API_KEY_VERIFICATION:
            return jsonify({'error': 'Invalid API Key'}), 403
        return f(*args, **kwargs)
    return decorated_function


def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def image_to_base64(image_file):
    encoded_string = base64.b64encode(image_file.read()).decode('utf-8')
    return encoded_string

def base64_to_image(base64_string, filename):
    img_data = base64.b64decode(base64_string)
    img = Image.open(io.BytesIO(img_data))
    img.save(filename)

def is_duplicate_image( person_name, base64_image):
    db = connect_to_mongo()
    try:
        existing_image = db.signatures.find_one({
            'person_name': person_name,
            'signature': base64_image
        })
        return existing_image is not None
    except Exception as e:
        print(f"Error checking for duplicate image: {e}")
        return False  
    
@app.route('/upload', methods=['POST'])
@require_api_key
def upload_image():
    try:
        if request.method != 'POST':
            return jsonify({'error': 'Method not allowed'}), 405

        person_name = request.form['person_name'].lower()
        if not person_name:
            return jsonify({'error': "No person found."}), 400

        img_type = request.form.get('type', 'genuine')

        if 'reference_images' not in request.files:
            return jsonify({'error': 'No image found'}), 400

        files = request.files.getlist('reference_images')
        if files and all(allowed_file(file.filename) for file in files):
            documents = []
            for file in files:
        
                try:
                    base64_image = image_to_base64(file)

                    documents.append({
                        'person_name': person_name,
                        'signature': base64_image,
                        'type': img_type
                    })

                except Exception as e:
                    print(f"Error processing image file: {e}")
                    return jsonify({'error': 'Failed to process image file'}), 500
            
            try:
                db = connect_to_mongo()
                if data_store(db, documents):
                    return jsonify({'message': 'Images uploaded and stored successfully'}), 200
                else:
                    return jsonify({'error': 'Failed to store images in database'}), 500
            except Exception as e:
                print(f"Error connecting to database or storing data: {e}")
                return jsonify({'error': 'Database operation failed'}), 500
        else:
            return jsonify({'error': 'Invalid file format. Only PNG, JPG, JPEG files are allowed.'}), 400

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/signature-matching', methods = ['POST'])
@require_api_key_verification
def signature_matching():
    start_time = time.time()
    try:
        if request.method != 'POST':
            return jsonify({'error': 'POST Method not allowed'}), 405

        person_name = request.form['person_name'].lower()
        similarity_threshold = float(request.form.get('threshold', 85))

        print("Person Name:", person_name)
        print("Threshold:", similarity_threshold)

        if not person_name:
            return jsonify({'error': 'No person name provided'}), 400

        if 'verification_image' not in request.files:
            return jsonify({'error': 'No test image provided'}), 400

        test_image = request.files['verification_image']
        print("test image is found..!!\nThe image is:", test_image)

        if test_image and allowed_file(test_image.filename):
            temp_dir = "static/uploads"
            os.makedirs(temp_dir, exist_ok=True)
            test_image_path = os.path.join(temp_dir, f"{person_name}_test_image.jpg")
            
            # Try saving the test image
            try:
                test_image.save(test_image_path)
                print("The test image is saved.")
            except Exception as e:
                print(f"Error saving test image: {e}")
                return jsonify({'error': 'Failed to save test image'}), 500

            person_dir = os.path.join("static/person/", person_name)
            os.makedirs(person_dir, exist_ok=True)
            print(f"The person {person_name} folder is created successfully")

            # Connect to MongoDB
            try:
                db = connect_to_mongo()
                signatures = fetch_signatures(db, person_name)
            except Exception as e:
                print(f"Error connecting to MongoDB or fetching signatures: {e}")
                return jsonify({'error': 'Database connection or query failed'}), 500

            if not signatures:
                return jsonify({'error': f'No signatures found for {person_name}'}), 404

            print(f"Number of signatures found: {len(signatures)}")

            # existing_files = set(os.listdir(person_dir))
            
            start_of_conversion = time.time()    
            for i, signature in enumerate(signatures):
                print("The data is: ", signature)
                signature_base64 = signature['signature']
                signature_filename = f"{person_name}_{signature['_id']}_{i}.png"
                signature_path = os.path.join(person_dir, signature_filename)

                # if signature_filename in existing_files:
                #     print(f"Signature file '{signature_filename}' already exists. Skipping conversion.")
                #     continue

                # Convert and save the Base64 image
                try:
                    base64_to_image(signature_base64.encode(), signature_path)
                    print(f"Converted base64 to image: {signature_filename}")
                except Exception as e:
                    print(f"Error converting base64 to image for signature {signature['_id']}: {e}")
                    return jsonify({'error': 'Failed to process signature image'}), 500

            end_of_conversion = time.time()
            print("Converted all images successfully")

            real_images_paths = [os.path.join(person_dir, filename) for filename in os.listdir(person_dir) ]

            try:
                # print("Finding VGG score.....")
                # result = is_signature_genuine(test_image_path, real_images_paths, similarity_threshold)
            
                print("Finding ResNet score...")
                result = is_signature_genuine_resnet(test_image_path, real_images_paths, similarity_threshold)
            except Exception as e:
                print(f"Error in signature matching: {e}")
                return jsonify({'error': 'Failed to match signatures'}), 500
            
            end_time = time.time()
            conversion_time = end_of_conversion - start_of_conversion 
            elapsed_time = end_time - start_time
            print("Time passed when converting:", str(timedelta(seconds=conversion_time)))
            print("Time passed:", str(timedelta(seconds=elapsed_time)))
            response = jsonify({
                'vgg': {
                    'prediction': result[0],
                    'score': float(result[1])
                }
            })
            
            # Delete the person_dir folder after returning the response
            try:
                import shutil
                shutil.rmtree(person_dir)
                print(f"Deleted the person directory: {person_dir}")
            except Exception as e:
                print(f"Error deleting person directory: {e}")
            
            return response
        
        else:
            return jsonify({'error': 'Invalid file format. Only PNG, JPG, JPEG files are allowed.'}), 400

    except Exception as e:
        print(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500


@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(host="0.0.0.0", port=5000)


# For real & forged signature 
# def signature_matching():
#     if request.method == 'POST':
#         person_name = request.form['person_name'].lower()
#         similarity_threshold = float(request.form.get('threshold', 85))

#         print("person Name:", person_name)
#         print("threshold:", similarity_threshold)
#         if not person_name:
#             return jsonify({'error': 'No person name provided'}), 400
        
#         if 'verification_image' not in request.files:
#             return jsonify({'error': 'No test image provided'}), 400

#         test_image = request.files['verification_image']
#         print("test image is FOund..!! \n THe image is :", test_image)
#         if test_image and allowed_file(test_image.filename):
#             temp_dir = "static/uploads"
#             os.makedirs(temp_dir, exist_ok=True)
#             test_image_path = os.path.join(temp_dir, "test_image.jpg")
#             test_image.save(test_image_path)
#             print("The test image is saved.")
            
#             person_dir = os.path.join("static/person/", person_name)
#             os.makedirs(person_dir, exist_ok=True)
#             print(f"The person {person_name} folder is created successfuly")
            
#             db = connect_to_mongo()
#             signatures = fetch_signatures(db, person_name)
#             if not signatures:
#                 return jsonify({'error': f'No signatures found for {person_name}'}), 404
            
#             print(f"NO of signatures found: {len(signatures)}")
#             # real_count = 0
#             # forged_count = 0

#             # for signature in signatures:
#             #     if signature['type'] == 'real':
#             #         real_count += 1
#             #     elif signature['type'] == 'forged':
#             #         forged_count += 1

#             # Get a list of existing files in the person's directory
#             existing_files = set(os.listdir(person_dir))

#             for i, signature in enumerate(signatures): 
#                 signature_base64 = signature['signature']
#                 signature_filename = f"{person_name}_{signature['_id']}_{i}.png"
#                 signature_path = os.path.join(person_dir, signature_filename)

#                 if signature_filename in existing_files:
#                     print(f"Signature file '{signature_filename}' already exists. Skipping conversion.")
#                     continue  

#                 # Convert and save the Base64 image
#                 try:
#                     base64_to_image(signature_base64.encode(), signature_path)
#                     print(f"Converting base64 to image: {signature_filename}")
#                 except Exception as e:
#                     print(f"Error converting base64 to image for signature {signature['_id']}: {e}")
#                     return jsonify({'error': 'Failed to process signature image'}), 500

#             print("COnverting all the images Successfully")
#             test_image_path = temp_dir + "/test_image.jpg"
#             # print(test_image_path)
#             # print(person_dir)
#             real_images_paths = [os.path.join(person_dir, filename) for filename in os.listdir(person_dir) if filename.lower().endswith(('.png', '.jpg'))]
            
            
#             print("Finding VGG score.....")
#             # result = is_signature_genuine(test_image_path, real_images_paths, similarity_threshold)
#             # print("Finding ResNet score......")
#             result = is_signature_genuine_resnet(test_image_path, real_images_paths, similarity_threshold)
            
#             return jsonify({
#                 'vgg': {
#                     'prediction': result[0],
#                     'score': float(result[1])
#                 }
#             })
#             # return jsonify({
#             #     'vgg': {
#             #         'prediction': 'Genuine' if result[0] else 'Forged',
#             #         'score': float(result[1])
#             #     },
#             #     'resnet': {
#             #         'prediction': 'Genuine' if result_r[0] else 'Forged',
#             #         'score': float(result_r[1])
#             #     }
#             # })
            

#         else:
#             return jsonify({'error': 'Invalid file format. Only PNG, JPG, JPEG files are allowed.'}), 400
#     else:
#         return jsonify({'error': 'POST Method not allowed'}), 405
