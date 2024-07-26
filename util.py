import json

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'docx', 'pdf'}

def save_data(filepath):
    data = {
        "filename": filepath,
        "status": "processed"
    }
    with open(filepath.replace('.docx', '.json').replace('.pdf', '.json'), 'w') as json_file:
        json.dump(data, json_file, indent=4)
